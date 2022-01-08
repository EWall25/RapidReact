import commands2
import wpilib
import wpilib.drive

from constants import *


class DriveSubsystem(commands2.SubsystemBase):
    def __init__(self) -> None:
        super().__init__()

        self.fr_motor = wpilib.Spark(FRONT_RIGHT_MOTOR_PORT)
        self.br_motor = wpilib.Spark(BACK_RIGHT_MOTOR_PORT)
        self.fl_motor = wpilib.Spark(FRONT_LEFT_MOTOR_PORT)
        self.bl_motor = wpilib.Spark(BACK_LEFT_MOTOR_PORT)

        self.drive = wpilib.drive.DifferentialDrive(
            wpilib.SpeedControllerGroup(self.fl_motor, self.bl_motor),
            wpilib.SpeedControllerGroup(self.fr_motor, self.br_motor)
        )

    def arcade_drive(self, forward: float, rotation: float) -> None:
        """
        Drives the robot using arcade controls.

        :param forward: Forward movement rate
        :param rotation: Rotation rate
        """

        self.drive.arcadeDrive(forward, rotation, False)
