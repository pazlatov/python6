"""Exercise 3: demonstrate the state transitions of both capable entities."""

from ex3 import TransformCreatureFactory


def main() -> None:
    """Describe, attack, transform, attack again and revert both forms."""
    factory = TransformCreatureFactory()
    print("Testing Creature with transform capability")
    for label, entity in (
        ("base", factory.create_base()),
        ("evolved", factory.create_evolved()),
    ):
        print(f"{label}:")
        print(entity.describe())
        print(entity.attack())
        print(entity.transform())
        try:
            print(entity.attack())
        finally:
            print(entity.revert())


if __name__ == "__main__":
    main()
