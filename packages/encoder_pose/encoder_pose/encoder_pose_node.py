#!/usr/bin/env python3
from threading import Lock
from typing import Optional

import numpy as np
import rclpy
from duckietown_msgs.msg import WheelEncoderStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from std_srvs.srv import Trigger

from lx_ros2_tools.params import LiveParams
from lx_ros2_tools.robot import get_wheel_params

# the functions you write in `packages/odometry/odometry.py` (the notebooks import them the same way)
from odometry.odometry import delta_phi, estimate_pose


class EncoderPoseNode(Node):
    """
    Computes an estimate of the Duckiebot pose using the wheel encoders.

    Parameters (config/encoder_pose_node/default.yaml, live-updatable with `ros2 param set`):
        ~publish_rate (float): rate [Hz] at which the pose estimate is published
        ~verbose (bool): log every pose update to the screen

    Publisher:
        ~/odom (:obj:`nav_msgs/Odometry`): the estimated pose (frame `map`)
    Subscribers:
        left_wheel_encoder_driver_node/tick (:obj:`WheelEncoderStamped`): encoder ticks
        right_wheel_encoder_driver_node/tick (:obj:`WheelEncoderStamped`): encoder ticks
    Services:
        ~/reset (:obj:`std_srvs/Trigger`): reset the estimate to (0, 0, 0)
    """

    right_tick_prev: Optional[int]
    left_tick_prev: Optional[int]
    delta_phi_left: float
    delta_phi_right: float

    def __init__(self):
        super().__init__("encoder_pose_node")
        self.get_logger().info("Initializing...")
        # get the name of the robot
        self.veh = self.get_namespace().strip("/")

        self.right_wheel_mutex = Lock()
        self.left_wheel_mutex = Lock()

        # Init the parameters
        self.resetParameters()

        # node parameters (defaults in config/encoder_pose_node/default.yaml, loaded by the launch file)
        self.params = LiveParams(self, {"publish_rate": 2.0, "verbose": True}, on_change=self._on_param)

        # R and baseline of this robot, read from its calibration file
        # (/data/config/calibrations/robot/<ROBOT>.yaml on the robot, keys `wheel_radius`, `wheel_baseline`)
        wheels = get_wheel_params(self.veh)
        self.R = wheels.radius  # meters, wheel radius
        self.baseline = wheels.baseline  # meters, distance between the wheels
        self.encoder_resolution = wheels.encoder_resolution  # ticks per revolution (fallback only)
        self.get_logger().info(
            f"Wheel radius: {self.R} m, baseline: {self.baseline} m, "
            f"encoder resolution: {self.encoder_resolution} ticks/rev (from {wheels.source})"
        )

        # Defining subscribers (relative names: the launch file puts the node in the robot namespace):

        # Wheel encoder subscriber:
        self.create_subscription(
            WheelEncoderStamped, "left_wheel_encoder_driver_node/tick", self.cbLeftEncoder, qos_profile_sensor_data
        )

        # Wheel encoder subscriber:
        self.create_subscription(
            WheelEncoderStamped, "right_wheel_encoder_driver_node/tick", self.cbRightEncoder, qos_profile_sensor_data
        )

        # Odometry publisher
        self.db_estimated_pose = self.create_publisher(Odometry, "~/odom", 10)

        # reset service (the "reset" button in the notebook)
        self.create_service(Trigger, "~/reset", self.srvReset)

        self.get_logger().info("Initialized.")
        self._timer = self.create_timer(1.0 / float(self.params.publish_rate), self.posePublisher)

    def resetParameters(self):
        # Add the node parameters to the parameters dictionary
        self.delta_phi_left = 0.0
        self.left_tick_prev = None

        self.delta_phi_right = 0.0
        self.right_tick_prev = None

        # Initializing the odometry
        self.x_prev = 0.0
        self.y_prev = 0.0
        self.theta_prev = 0.0

    def _on_param(self, name, value):
        self.get_logger().info(f"parameter {name} = {value}")
        if name == "publish_rate" and float(value) > 0:
            self._timer.cancel()
            self._timer = self.create_timer(1.0 / float(value), self.posePublisher)

    def srvReset(self, _req, res):
        with self.left_wheel_mutex:
            with self.right_wheel_mutex:
                self.resetParameters()
        self.get_logger().info("Pose estimate reset to (0, 0, 0).")
        res.success, res.message = True, "pose estimate reset to (0, 0, 0)"
        return res

    def cbLeftEncoder(self, encoder_msg):
        """
        Wheel encoder callback
        Args:
            encoder_msg (:obj:`WheelEncoderStamped`) encoder ROS message.
        """
        with self.left_wheel_mutex:
            # initializing ticks to stored absolute value
            if self.left_tick_prev is None:
                self.left_tick_prev = encoder_msg.data
                return

            left_ticks_curr = encoder_msg.data

            # running the DeltaPhi() function copied from the notebooks to calculate rotations
            delta_phi_left = delta_phi(
                left_ticks_curr, self.left_tick_prev, encoder_msg.resolution or self.encoder_resolution
            )
            if delta_phi_left == 0:
                return
            self.left_tick_prev = left_ticks_curr
            self.delta_phi_left += delta_phi_left

    def cbRightEncoder(self, encoder_msg):
        """
        Wheel encoder callback, the rotation of the wheel.
        Args:
            encoder_msg (:obj:`WheelEncoderStamped`) encoder ROS message.
        """

        with self.right_wheel_mutex:
            if self.right_tick_prev is None:
                self.right_tick_prev = encoder_msg.data
                return

            right_ticks_curr = encoder_msg.data

            # calculate rotation of right wheel
            delta_phi_right = delta_phi(
                right_ticks_curr, self.right_tick_prev, encoder_msg.resolution or self.encoder_resolution
            )
            if delta_phi_right == 0:
                return
            self.right_tick_prev = right_ticks_curr
            self.delta_phi_right += delta_phi_right

    def posePublisher(self):
        """
        Publish the pose of the Duckiebot given by the kinematic model
            using the encoders.
        Publish:
            ~/odom (:obj:`nav_msgs/Odometry`): Duckiebot pose.
        """
        with self.left_wheel_mutex:
            with self.right_wheel_mutex:

                x_curr, y_curr, theta_curr = estimate_pose(
                    self.R,
                    self.baseline,
                    self.x_prev,
                    self.y_prev,
                    self.theta_prev,
                    self.delta_phi_left,
                    self.delta_phi_right,
                )

                if (x_curr == self.x_prev) and (y_curr == self.y_prev) and (theta_curr == self.theta_prev):
                    return

                theta_curr = self.angle_clamp(theta_curr)  # angle always between 0,2pi

                # logging to screen for debugging purposes
                if self.params.verbose:
                    self.get_logger().info("              ODOMETRY             ")
                    # self.get_logger().info(f"Baseline : {self.baseline}   R: {self.R}")
                    self.get_logger().info("Just this move:")
                    self.get_logger().info(
                        f"Theta : {np.rad2deg(theta_curr) - np.rad2deg(self.theta_prev)} deg,  "
                        f"x: {x_curr - self.x_prev} m,  y: {y_curr - self.y_prev} m"
                    )
                    self.get_logger().info("Total accumulated:")
                    self.get_logger().info(f"Theta : {np.rad2deg(theta_curr)} deg,  x: {x_curr} m,  y: {y_curr} m")

                    self.get_logger().info(
                        f"Rotation left wheel : {np.rad2deg(self.delta_phi_left)} deg,   "
                        f"Rotation right wheel : {np.rad2deg(self.delta_phi_right)} deg"
                    )
                    self.get_logger().info(
                        f"Prev Ticks left : {self.left_tick_prev}   Prev Ticks right : {self.right_tick_prev}"
                    )

                # Calculate new odometry only when new data from encoders arrives
                self.delta_phi_left = 0
                self.delta_phi_right = 0

                # Current estimate becomes previous estimate at next iteration
                self.x_prev = x_curr
                self.y_prev = y_curr
                self.theta_prev = theta_curr

                # Creating message to plot the pose in the notebook (TrajectoryPlot)
                odom = Odometry()
                odom.header.frame_id = "map"
                odom.header.stamp = self.get_clock().now().to_msg()

                odom.pose.pose.position.x = float(x_curr)  # x position - estimate
                odom.pose.pose.position.y = float(y_curr)  # y position - estimate
                odom.pose.pose.position.z = 0.0  # z position - no flying allowed in Duckietown

                # these are quaternions!
                odom.pose.pose.orientation.x = 0.0
                odom.pose.pose.orientation.y = 0.0
                odom.pose.pose.orientation.z = float(np.sin(theta_curr / 2))
                odom.pose.pose.orientation.w = float(np.cos(theta_curr / 2))

                self.db_estimated_pose.publish(odom)

    @staticmethod
    def angle_clamp(theta):
        if theta > 2 * np.pi:
            return theta - 2 * np.pi
        elif theta < -2 * np.pi:
            return theta + 2 * np.pi
        else:
            return theta


def main(args=None):
    rclpy.init(args=args)
    node = EncoderPoseNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
