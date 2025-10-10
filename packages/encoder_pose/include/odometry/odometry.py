from typing import Tuple

import numpy as np


def delta_phi(ticks: int, prev_ticks: int, resolution: int) -> float:
    """
    Args:
        ticks: Current tick count from the encoders.
        prev_ticks: Previous tick count from the encoders.
        resolution: Number of ticks per full wheel rotation returned by the encoder.
    Return:
        dphi: Rotation of the wheel in radians.
    """

    # TODO: these are random values, you have to implement your own solution in here
    
    dticks = ticks - prev_ticks
    dphi = (2 * np.pi) * (dticks / resolution)
    
    return dphi


def estimate_pose(
    R: float,
    baseline: float,
    x_prev: float,
    y_prev: float,
    theta_prev: float,
    delta_phi_left: float,
    delta_phi_right: float,
) -> Tuple[float, float, float]:

    """
    Calculate the current Duckiebot pose using the dead-reckoning model.

    Args:
        R:                  radius of wheel (both wheels are assumed to have the same size) - this is fixed in simulation,
                            and will be imported from your saved calibration for the real robot
        baseline:           distance from wheel to wheel; 2L of the theory
        x_prev:             previous x estimate - assume given
        y_prev:             previous y estimate - assume given
        theta_prev:         previous orientation estimate - assume given
        delta_phi_left:     left wheel rotation (rad)
        delta_phi_right:    right wheel rotation (rad)

    Return:
        x_curr:                  estimated x coordinate
        y_curr:                  estimated y coordinate
        theta_curr:              estimated heading
    """

    # distance travelled by each wheel
    d_left = R * delta_phi_left
    d_right = R * delta_phi_right
    
    # how much the robot travelled
    d_A = (d_right + d_left) / 2
    
    # corientation change
    d_theta = (d_right - d_left) / baseline
    
    # new orientation
    theta_mid = theta_prev + 0.5 * d_theta
    theta_curr = theta_prev + d_theta
    
    # new position
    x_curr = x_prev + d_A * np.cos(theta_mid)
    y_curr = y_prev + d_A * np.sin(theta_mid)
    
    
    return x_curr, y_curr, theta_curr
