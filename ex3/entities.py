"""Concrete entities; callers obtain these through the public factories."""

from .creature import Creature, TransformCapability


class Flameling(Creature):
    """The base member of the flame family."""

    def __init__(self) -> None:
        super().__init__("Flameling", "Fire")

    def attack(self) -> str:
        """Use the flame family's base attack."""
        return f"{self.name} uses Ember!"


class Pyrodon(Creature):
    """The evolved member of the flame family."""

    def __init__(self) -> None:
        super().__init__("Pyrodon", "Fire/Flying")

    def attack(self) -> str:
        """Use the evolved flame attack."""
        return f"{self.name} uses Flamethrower!"


class Shiftling(Creature, TransformCapability):
    """A creature that also implements the independent transform contract."""

    def __init__(self) -> None:
        Creature.__init__(self, "Shiftling", "Normal")
        TransformCapability.__init__(self)

    def attack(self) -> str:
        """Choose the attack using state, not the caller's knowledge."""
        if self.transformed:
            return f"{self.name} performs a boosted strike!"
        return f"{self.name} attacks normally."

    def transform(self) -> str:
        """Enter the sharper form; repeated calls keep it active."""
        self.transformed = True
        return f"{self.name} shifts into a sharper form!"

    def revert(self) -> str:
        """Return to the normal state."""
        self.transformed = False
        return f"{self.name} returns to normal."


class Morphagon(Creature, TransformCapability):
    """The evolved transformation-capable entity."""

    def __init__(self) -> None:
        Creature.__init__(self, "Morphagon", "Normal/Dragon")
        TransformCapability.__init__(self)

    def attack(self) -> str:
        """Use the transformed attack only while the capability is active."""
        if self.transformed:
            return f"{self.name} unleashes a devastating morph strike!"
        return f"{self.name} attacks normally."

    def transform(self) -> str:
        """Activate the evolved battle form."""
        self.transformed = True
        return f"{self.name} morphs into a dragonic battle form!"

    def revert(self) -> str:
        """Restore the normal attack."""
        self.transformed = False
        return f"{self.name} stabilizes its form."
