import commands2
import wpimath.controller

from constants import ArmConstants
from subsystems.arm_subsystem import ArmSubsystem


class LowerArm(commands2.CommandBase):
    def __init__(self, arm: ArmSubsystem) -> None:
        super().__init__()

        self.arm = arm
        self.addRequirements([arm])

    def execute(self) -> None:
        self.arm.move(-0.3)

    def end(self, interrupted: bool) -> None:
        self.arm.stop()

    def isFinished(self) -> bool:
        return self.arm.at_lower_limit()


class ArmLowerHub(commands2.PIDCommand):
    def __init__(self, arm: ArmSubsystem):
        super().__init__(
            wpimath.controller.PIDController(
                ArmConstants.ROTATION_P,
                ArmConstants.ROTATION_I,
                ArmConstants.ROTATION_D
            ),
            arm.get_position,
            ArmConstants.LOWER_HUB_HEIGHT_DEGREES,
            arm.set_voltage,
            [arm]
        )

        self.controller = self.getController()
        self.controller.setTolerance(ArmConstants.ROTATION_TOLERANCE_DEGREES)

    def isFinished(self) -> bool:
        return self.controller.atSetpoint()


class ArmRamp(commands2.PIDCommand):
    def __init__(self, arm: ArmSubsystem):
        super().__init__(
            wpimath.controller.PIDController(
                ArmConstants.ROTATION_P,
                ArmConstants.ROTATION_I,
                ArmConstants.ROTATION_D
            ),
            arm.get_position,
            ArmConstants.RAMP_HEIGHT_DEGREES,
            arm.set_voltage,
            [arm]
        )

        self.controller = self.getController()
        self.controller.setTolerance(ArmConstants.ROTATION_TOLERANCE_DEGREES)

    def isFinished(self) -> bool:
        return self.controller.atSetpoint()
