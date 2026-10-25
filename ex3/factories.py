"""Abstract creation interface and its two interchangeable families."""

from abc import ABC, abstractmethod

from .creature import Creature
from .entities import Flameling, Morphagon, Pyrodon, Shiftling


class CreatureFactory(ABC):
    """Create family members without exposing concrete classes to callers."""

    @abstractmethod
    def create_base(self) -> Creature:
        """Create a new base entity."""
        raise NotImplementedError

    @abstractmethod
    def create_evolved(self) -> Creature:
        """Create a new evolved entity."""
        raise NotImplementedError


class FlameFactory(CreatureFactory):
    """Create members of the flame family."""

    def create_base(self) -> Flameling:
        """Return a fresh Flameling."""
        return Flameling()

    def create_evolved(self) -> Pyrodon:
        """Return a fresh Pyrodon."""
        return Pyrodon()


class TransformCreatureFactory(CreatureFactory):
    """Create entities supporting the transformation capability."""

    def create_base(self) -> Shiftling:
        """Return a fresh Shiftling."""
        return Shiftling()

    def create_evolved(self) -> Morphagon:
        """Return a fresh Morphagon."""
        return Morphagon()
