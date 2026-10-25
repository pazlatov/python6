"""Exercise 1: self-contained polymorphic processing of mixed streams."""

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


class DataStream:
    """Route through the processor interface in registration order."""

    def __init__(self) -> None:
        self._processors: list[DataProcessor] = []

    def register_processor(self, proc: DataProcessor) -> None:
        """Register an instance once; first matching processor handles data."""
        if not isinstance(proc, DataProcessor):
            raise TypeError("Expected a DataProcessor instance")
        if any(proc is registered for registered in self._processors):
            raise ValueError("Processor instance is already registered")
        self._processors.append(proc)

    def process_stream(self, stream: list[Any]) -> None:
        """Handle each input independently, preserving later stream entries."""
        for element in stream:
            for proc in self._processors:
                try:
                    if not proc.validate(element):
                        continue
                    proc.ingest(element)
                except Exception as error:
                    print(f"DataStream processor error: {error}")
                break
            else:
                print(f"DataStream error - Can't process element: {element}")

    def print_processors_stats(self) -> None:
        """Show lifetime ingestion counts and current queue sizes."""
        print("== DataStream statistics ==")
        if not self._processors:
            print("No processor found, no data")
        for proc in self._processors:
            print(
                f"{type(proc).__name__}: total {proc.total_processed} "
                f"items processed, remaining {proc.remaining} on processor"
            )


def main() -> None:
    """Show routing before and after registering additional processors."""
    print("=== Code Nexus - Data Stream ===")
    stream = DataStream()
    stream.print_processors_stats()
    numeric = NumericProcessor()
    text = TextProcessor()
    logs = LogProcessor()
    stream.register_processor(numeric)
    batch: list[Any] = [
        "Hello world", [3.14, -1, 2.71],
        [
            {"log_level": "WARNING", "log_message": "Use ssh instead"},
            {"log_level": "INFO", "log_message": "User wil is connected"},
        ],
        42, ["Hi", "five"],
    ]
    print("Sending batch with only NumericProcessor registered")
    stream.process_stream(batch)
    stream.print_processors_stats()
    stream.register_processor(text)
    stream.register_processor(logs)
    print("Sending the same batch with all processors registered")
    stream.process_stream(batch)
    stream.print_processors_stats()
    for processor, count in ((numeric, 3), (text, 2), (logs, 1)):
        for _ in range(count):
            print(f"Consumed {type(processor).__name__}: {processor.output()}")
    stream.print_processors_stats()


if __name__ == "__main__":
    main()
