"""Common entity interface and a separate transformation capability."""

from abc import ABC, abstractmethod


class Creature(ABC):
    """An entity has an identity and knows how to attack."""

    def __init__(self, name: str, creature_type: str) -> None:
        self.name: str = name
        self.creature_type: str = creature_type

    @abstractmethod
    def attack(self) -> str:
        """Describe this entity's current attack."""
        raise NotImplementedError

    def describe(self) -> str:
        """Describe any entity without knowing its concrete family."""
        return f"{self.name} is a {self.creature_type} type Creature"


class TransformCapability(ABC):
    """A capability independent of the Creature inheritance hierarchy."""

    def __init__(self) -> None:
        self.transformed: bool = False

    @abstractmethod
    def transform(self) -> str:
        """Enable the transformed state and describe the transition."""
        raise NotImplementedError

    @abstractmethod
    def revert(self) -> str:
        """Disable the transformed state and describe the transition."""
        raise NotImplementedError
