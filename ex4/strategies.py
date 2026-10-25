"""Strategies depend on entity and capability interfaces."""

from abc import ABC, abstractmethod

from ex3.creature import Creature, TransformCapability


class InvalidStrategyError(Exception):
    """Raised when a strategy is asked to act on an unsuitable entity."""


class BattleStrategy(ABC):
    """An interchangeable battle algorithm."""

    @abstractmethod
    def is_valid(self, entity: Creature) -> bool:
        """Report whether this strategy supports the entity."""
        raise NotImplementedError

    @abstractmethod
    def act(self, entity: Creature) -> None:
        """Perform the strategy or raise InvalidStrategyError."""
        raise NotImplementedError


class NormalStrategy(BattleStrategy):
    """Every Creature can perform its own normal attack method."""

    def is_valid(self, entity: Creature) -> bool:
        """Accept all entities in the abstract Creature hierarchy."""
        return isinstance(entity, Creature)

    def act(self, entity: Creature) -> None:
        """Use the entity's attack without any capability-specific logic."""
        if not self.is_valid(entity):
            raise InvalidStrategyError("Normal strategy requires a Creature")
        print(entity.attack())


class AggressiveStrategy(BattleStrategy):
    """Use the transformation capability and always restore normal state."""

    def is_valid(self, entity: Creature) -> bool:
        """Check the capability, not a concrete entity class."""
        return isinstance(entity, TransformCapability)

    def act(self, entity: Creature) -> None:
        """Transform, attack and revert; reject unsuitable entities."""
        if not isinstance(entity, TransformCapability):
            raise InvalidStrategyError(
                f"Invalid Creature '{entity.name}' "
                "for this aggressive strategy"
            )
        try:
            print(entity.transform())
            print(entity.attack())
        finally:
            print(entity.revert())
