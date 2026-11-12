"""Pure, testable arbitration policy; the ROS node only adapts messages."""
from dataclasses import dataclass
from enum import Enum


class CommandSource(str, Enum):
    AUTONOMY = 'autonomy'
    HUMAN = 'human'
    FAILSAFE_STOP = 'failsafe_stop'


@dataclass(frozen=True)
class Command:
    linear: float = 0.0
    angular: float = 0.0


@dataclass(frozen=True)
class Decision:
    command: Command
    source: CommandSource
    reason: str


class ArbitrationPolicy:
    """Human control wins; stale input is never forwarded to the robot."""
    def __init__(self, timeout_seconds: float = 0.35, max_linear: float = 0.45,
                 max_angular: float = 1.50) -> None:
        self.timeout_seconds = timeout_seconds
        self.max_linear = max_linear
        self.max_angular = max_angular
        self.autonomy: tuple[Command, float] | None = None
        self.human: tuple[Command, float] | None = None
        self.human_override = False

    def set_autonomy(self, command: Command, timestamp: float) -> None:
        self.autonomy = (command, timestamp)

    def set_human(self, command: Command, timestamp: float) -> None:
        self.human = (command, timestamp)

    def set_human_override(self, enabled: bool) -> None:
        self.human_override = enabled

    def _fresh(self, item: tuple[Command, float] | None, now: float) -> bool:
        return item is not None and 0.0 <= now - item[1] <= self.timeout_seconds

    def _bounded(self, command: Command) -> Command:
        return Command(max(-self.max_linear, min(self.max_linear, command.linear)),
                       max(-self.max_angular, min(self.max_angular, command.angular)))

    def decide(self, now: float) -> Decision:
        if self.human_override and self._fresh(self.human, now):
            return Decision(self._bounded(self.human[0]), CommandSource.HUMAN, 'Active human override.')
        if self.human_override:
            return Decision(Command(), CommandSource.FAILSAFE_STOP, 'Human override is active but its command is stale.')
        if self._fresh(self.autonomy, now):
            return Decision(self._bounded(self.autonomy[0]), CommandSource.AUTONOMY, 'Fresh autonomous command.')
        return Decision(Command(), CommandSource.FAILSAFE_STOP, 'No fresh command source.')
