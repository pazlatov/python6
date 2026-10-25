"""Exercise 3: use the factory interface without naming concrete entities."""

from ex3 import CreatureFactory, FlameFactory, TransformCreatureFactory


def test_factory(factory: CreatureFactory) -> None:
    """Exercise base and evolved creation through one abstract interface."""
    print("Testing factory")
    for entity in (factory.create_base(), factory.create_evolved()):
        print(entity.describe())
        print(entity.attack())


def battle(first: CreatureFactory, second: CreatureFactory) -> None:
    """Let two freshly created base entities attack."""
    left = first.create_base()
    right = second.create_base()
    print("Testing battle")
    print(left.describe())
    print("vs.")
    print(right.describe())
    print("fight!")
    print(left.attack())
    print(right.attack())


def main() -> None:
    """Demonstrate both families using the same functions."""
    flame = FlameFactory()
    transform = TransformCreatureFactory()
    test_factory(flame)
    test_factory(transform)
    battle(flame, transform)


if __name__ == "__main__":
    main()
