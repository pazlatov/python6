"""Exercise 0: abstract processors and atomic FIFO ingestion."""

from abc import ABC, abstractmethod
from typing import Any


class DataProcessor(ABC):
    """Store validated items in FIFO order with lifetime processing ranks."""

    def __init__(self) -> None:
        self._queue: list[str] = []
        self._next_rank: int = 0
        self.total_processed: int = 0

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Report whether the entire input can be ingested."""
        raise NotImplementedError

    @abstractmethod
    def ingest(self, data: Any) -> None:
        """Validate and store all items, or raise without changing state."""
        raise NotImplementedError

    def _store(self, items: list[str]) -> None:
        """Commit a complete batch only after validation and conversion."""
        self._queue.extend(items)
        self.total_processed += len(items)

    def output(self) -> tuple[int, str]:
        """Remove the oldest item; an empty queue raises IndexError."""
        if not self._queue:
            raise IndexError("No processed data available")
        value = self._queue.pop(0)
        rank = self._next_rank
        self._next_rank += 1
        return rank, value

    @property
    def remaining(self) -> int:
        """Return the number of items waiting to be extracted."""
        return len(self._queue)


class NumericProcessor(DataProcessor):
    """Accept numbers and numeric lists, but not boolean flags."""

    def validate(self, data: Any) -> bool:
        items = data if isinstance(data, list) else [data]
        return all(
            isinstance(item, (int, float)) and not isinstance(item, bool)
            for item in items
        )

    def ingest(self, data: int | float | list[int | float]) -> None:
        """Store each number separately after validating the whole input."""
        if not self.validate(data):
            raise ValueError("Improper numeric data")
        items = data if isinstance(data, list) else [data]
        self._store([str(item) for item in items])


class TextProcessor(DataProcessor):
    """Accept a string or a list containing only strings."""

    def validate(self, data: Any) -> bool:
        items = data if isinstance(data, list) else [data]
        return all(isinstance(item, str) for item in items)

    def ingest(self, data: str | list[str]) -> None:
        """Store strings separately without splitting them into characters."""
        if not self.validate(data):
            raise ValueError("Improper text data")
        items = data if isinstance(data, list) else [data]
        self._store(list(items))


class LogProcessor(DataProcessor):
    """Accept dictionaries whose keys and values are strings."""

    def validate(self, data: Any) -> bool:
        items = data if isinstance(data, list) else [data]
        return all(
            isinstance(item, dict)
            and all(
                isinstance(key, str) and isinstance(value, str)
                for key, value in item.items()
            )
            for item in items
        )

    def ingest(
        self, data: dict[str, str] | list[dict[str, str]]
    ) -> None:
        """Render standard logs or arbitrary string dictionaries atomically."""
        if not self.validate(data):
            raise ValueError("Improper log data")
        items = data if isinstance(data, list) else [data]
        converted: list[str] = []
        for item in items:
            if set(item) == {"log_level", "log_message"}:
                converted.append(
                    f"{item['log_level']}: {item['log_message']}"
                )
            else:
                converted.append(
                    ", ".join(f"{key}: {value}" for key, value in item.items())
                )
        self._store(converted)


def main() -> None:
    """Demonstrate validation, protected ingestion and ranked FIFO output."""
    print("=== Code Nexus - Data Processor ===")
    numeric = NumericProcessor()
    text = TextProcessor()
    logs = LogProcessor()
    for processor, good, bad in (
        (numeric, 42, "Hello"),
        (text, "Hello", 42),
        (logs, {"log_level": "INFO", "log_message": "Ready"}, "Hello"),
    ):
        print(f"Testing {type(processor).__name__}...")
        print(f"Validate {good!r}: {processor.validate(good)}")
        print(f"Validate {bad!r}: {processor.validate(bad)}")
    print("Invalid numeric ingestion without validation:")
    try:
        numeric.ingest("foo")
    except ValueError as error:
        print(f"Got exception: {error}")
    numeric.ingest([1, 2.5, 3, 4, 5])
    text.ingest(["Hello", "Nexus", "World"])
    logs.ingest([
        {"log_level": "NOTICE", "log_message": "Connection to server"},
        {"log_level": "ERROR", "log_message": "Unauthorized access!"},
    ])
    for processor, count in ((numeric, 3), (text, 1), (logs, 2)):
        for _ in range(count):
            rank, value = processor.output()
            print(f"{type(processor).__name__} item {rank}: {value}")
    try:
        logs.output()
    except IndexError as error:
        print(f"Empty processor handled: {error}")


if __name__ == "__main__":
    main()
