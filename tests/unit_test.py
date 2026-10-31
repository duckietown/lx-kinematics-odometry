import numpy as np


class UnitTestMessage:
    # Test the WheelEncoderStamped messages
    def __init__(self, callback):
        from duckietown_msgs.msg import WheelEncoderStamped
        from std_msgs.msg import Header

        # creating a dummy wheel encoder message to allow testing how to read fields

        header = Header()
        # node.get_clock().now().to_msg() is the correct stamp, anyway this works only when a node is initialized
        header.stamp.sec = 1618436796
        header.stamp.nanosec = 55785179
        header.frame_id = f"agent/left_wheel_axis"

        encoder_msg = WheelEncoderStamped(
            header=header, data=4, resolution=135, type=WheelEncoderStamped.ENCODER_TYPE_INCREMENTAL
        )

        callback(encoder_msg)


class UnitTestOdometry:
    # Test the odometry
    def __init__(self, R, baseline_wheel2wheel, poseEstimation):

        # initial conditions
        x_prev = y_prev = theta_prev = 0

        # to store the estimates, so we can plot them
        x_prev_ = []
        y_prev_ = []
        theta_prev_ = []

        x, y, robot_rotation = poseEstimation(
            R,
            baseline_wheel2wheel,
            x_prev,
            y_prev,
            theta_prev,
            5 * np.pi / 180,  # left wheel rotates by 5 degrees
            10 * np.pi / 180, # right wheel rotates by 10 degrees
            )
        # given how much the robot rotates with wheel rotations of 5 and 10 degrees,
        # calculate the number of steps required to do a circle.
        # this is independent from R and the baseline
        steps4circle = int(2 * np.pi / robot_rotation)

        # iterate steps4circle times the pose estimation
        # function to be tested.
        for _ in range(0, steps4circle):
            # save the current values of x, y and theta
            x_prev_.append(x_prev)
            y_prev_.append(y_prev)
            theta_prev_.append(theta_prev)
            x_prev, y_prev, theta_prev = poseEstimation(
                R,
                baseline_wheel2wheel,
                x_prev,
                y_prev,
                theta_prev,
                5 * np.pi / 180,
                10 * np.pi / 180,
            )

        # plot the results
        self.plot(x_prev_, y_prev_, theta_prev_)

    def plot(self, x, y, theta):
        import matplotlib.pyplot as plt

        figure, axes = plt.subplots(1)

        axes.plot(x, y, "r")
        axes.set_aspect(1)

        plt.xlabel("X position")
        plt.ylabel("Y position")

        plt.title("Am I a circle?")
        plt.show()
