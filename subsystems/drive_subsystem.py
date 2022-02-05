import math

import commands2
import wpilib
import wpilib.drive
import wpimath.kinematics
from wpimath.geometry import Pose2d, Rotation2d
from ctre import PigeonIMU, CANCoder, SensorTimeBase

from constants import *


class DriveSubsystem(commands2.SubsystemBase):

    def __init__(self) -> None:
        super().__init__()

        # Front-left drive motor
        self.fl_motor = wpilib.Spark(FRONT_LEFT_MOTOR_PORT)
        # Back-left drive motor
        self.bl_motor = wpilib.Spark(BACK_LEFT_MOTOR_PORT)
        # Front-right drive motor
        self.fr_motor = wpilib.Spark(FRONT_RIGHT_MOTOR_PORT)
        # Back-right drive motor
        self.br_motor = wpilib.Spark(BACK_RIGHT_MOTOR_PORT)

        # Both drive motors on the left side of the robot
        self.l_motors = wpilib.MotorControllerGroup(self.fl_motor, self.bl_motor)
        self.l_motors.setInverted(False)

        # Both drive motors on the right side of the robot
        self.r_motors = wpilib.MotorControllerGroup(self.fr_motor, self.br_motor)
        self.r_motors.setInverted(True)

        self.drive = wpilib.drive.DifferentialDrive(self.l_motors, self.r_motors)

        # Left side encoder
        # self.l_encoder = CANCoder(2)
        self.l_encoder = wpilib.Encoder(0, 1)
        self.l_encoder.setReverseDirection(False)

        # Right side encoder
        # self.r_encoder = CANCoder(3)
        self.r_encoder = wpilib.Encoder(2, 3)
        self.r_encoder.setReverseDirection(True)

        # Configure the encoders to return a value in inches
        # Uses the wheel diameter and number of "counts" per motor rotation to calculate distance
        # self.l_encoder.configFeedbackCoefficient(6 * math.pi / 4096, "inches", SensorTimeBase.PerSecond)
        # self.r_encoder.configFeedbackCoefficient(6 * math.pi / 4096, "inches", SensorTimeBase.PerSecond)
        self.l_encoder.setDistancePerPulse(6 * math.pi / 360)
        self.r_encoder.setDistancePerPulse(6 * math.pi / 360)

        # Put encoders to Smart Dashboard
        wpilib.SmartDashboard.putData("Left Encoder", self.l_encoder)
        wpilib.SmartDashboard.putData("Right Encoder", self.r_encoder)

        # Inertia Measurement Unit/Gyroscope
        self.imu = PigeonIMU(1)

        # The robot's pose (position and rotation on the field).
        # This will be updated periodically.
        self.pose = Pose2d()

        # Encoders MUST be reset to 0 before instantiating odometry
        self.reset_encoders()

        # Create the odometry object.
        # Odometry allows us to know the position of the robot during autonomous.
        # It shouldn't be used during teleop because of drift from colliding with
        # other robots.
        # See periodic() for why the heading needs to be negated. I'm not writing it again.
        self.odometry = wpimath.kinematics.DifferentialDriveOdometry(
            Rotation2d.fromDegrees(-self.get_heading()), Pose2d(0, 0, Rotation2d()))

    def periodic(self) -> None:
        # Get the gyro angle. We have to negate it because WPILib classes expect
        # a negative value as the robot turns clockwise. Our gyro returns a positive
        # value as the robot turns clockwise.
        heading = Rotation2d.fromDegrees(-self.get_heading())

        # Get the distance the robot has driven. We need to convert it from customary units (inches)
        # into metres because WPILib odometry.
        l_distance = self.get_left_wheel_distance() / 39.37
        r_distance = self.get_right_wheel_distance() / 39.37

        # Update the robot's position and rotation on the field
        self.pose = self.odometry.update(heading, l_distance, r_distance)

        # Update the robot's heading direction on the Smart Dashboard
        wpilib.SmartDashboard.putNumber("Heading", self.get_heading())

    def arcade_drive(self, forward: float, rotation: float) -> None:
        """
        Drives the robot using arcade controls.

        :param forward: Forward movement rate
        :param rotation: Rotation rate
        """

        self.drive.arcadeDrive(forward, rotation, False)

    def stop(self) -> None:
        """
        Stops the robot's motors.
        """

        self.drive.stopMotor()

    def reset_heading(self) -> None:
        """
        Zeroes the gyroscope's heading.
        """

        self.imu.setYaw(0)

    def get_heading(self) -> float:
        """
        Gets the robot's heading direction.
        :return: The robot's heading direction in degrees from -180 to 180
        """

        # getYawPitchRoll returns an error code and an array containing the yaw, pitch and roll
        # Get that array then return the yaw
        ypr = self.imu.getYawPitchRoll()[1]
        return ypr[0]

    def get_left_wheel_distance(self) -> float:
        """
        Gets the distance travelled by the robot's left wheel.
        :return: The distance travelled by the left wheel in inches.
        """

        return self.l_encoder.getDistance()

    def get_right_wheel_distance(self) -> float:
        """
        Gets the distance travelled by the robot's right wheel.
        :return: The distance travelled by the right wheel in inches.
        """

        return self.r_encoder.getDistance()

    def get_average_distance(self) -> float:
        """
        Gets the distance travelled by the robot.
        :return: The average distance travelled by both drive motors in inches.
        """

        # Add together the left encoder and right encoder's position then average them by dividing by 2
        # return (self.l_encoder.getPosition() + self.r_encoder.getPosition()) / 2
        return (self.get_left_wheel_distance() + self.get_right_wheel_distance()) / 2

    def reset_encoders(self) -> None:
        """
        Resets the encoders' values to 0
        """

        # self.l_encoder.setPosition(0)
        # self.r_encoder.setPosition(0)
        self.l_encoder.reset()
        self.r_encoder.reset()

    def get_pose(self) -> Pose2d:
        """
        Gets the robot's position and rotation on the field from the odometry.
        :return: The robot's pose
        """

        return self.pose

    def reset_pose(self, pose: Pose2d) -> None:
        """
        Resets the robot's position to the specified pose. Also resets the encoders to zero,
        as encoders must be zeroed every time odometry is reset.
        :param pose: The pose to reset the odometry to
        """

        # Get the gyro angle. We have to negate it because WPILib classes expect
        # a negative value as the robot turns clockwise. Our gyro returns a positive
        # value as the robot turns clockwise.
        heading = Rotation2d.fromDegrees(-self.get_heading())

        self.reset_encoders()

        self.odometry.resetPosition(pose, heading)
