"""Exercise 4: a tournament for arbitrary factory-strategy pairs."""

from ex3 import CreatureFactory, FlameFactory, TransformCreatureFactory
from ex4 import (
    AggressiveStrategy,
    BattleStrategy,
    InvalidStrategyError,
    NormalStrategy,
)


def battle(opponents: list[tuple[CreatureFactory, BattleStrategy]]) -> None:
    """Run each unique pair once; abort on the first invalid strategy."""
    print("*** Tournament ***")
    print(f"{len(opponents)} opponents involved")
    if len(opponents) < 2:
        print("At least two opponents are needed for a battle.")
        return
    for first in range(len(opponents)):
        for second in range(first + 1, len(opponents)):
            left_factory, left_strategy = opponents[first]
            right_factory, right_strategy = opponents[second]
            left = left_factory.create_base()
            right = right_factory.create_base()
            print("* Battle *")
            print(left.describe())
            print("vs.")
            print(right.describe())
            print("now fight!")
            try:
                left_strategy.act(left)
                right_strategy.act(right)
            except InvalidStrategyError as error:
                print(f"Battle error, aborting tournament: {error}")
                return


def main() -> None:
    """Demonstrate a valid pair and a mismatched aggressive strategy."""
    flame = FlameFactory()
    transform = TransformCreatureFactory()
    normal = NormalStrategy()
    aggressive = AggressiveStrategy()
    print("Tournament 0 (basic)")
    battle([(flame, normal), (transform, aggressive)])
    print("\nTournament 1 (error)")
    battle([(transform, aggressive), (flame, aggressive)])


if __name__ == "__main__":
    main()
