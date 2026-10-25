"""Exercise 2: self-contained stream with structurally typed exporters."""

from abc import ABC, abstractmethod
from typing import Any, Protocol


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


class ExportPlugin(Protocol):
    """A structural contract: exporters need not inherit from this class."""

    def process_output(self, data: list[tuple[int, str]]) -> None:
        """Export ranked string values."""
        ...


class CSVExportPlugin:
    """Render one valid CSV row, quoting and escaping every field."""

    def process_output(self, data: list[tuple[int, str]]) -> None:
        """Export values; CSV does not include processor-local ranks."""
        fields = ['"' + value.replace('"', '""') + '"' for _, value in data]
        print("CSV Output:")
        print(",".join(fields))


class JSONExportPlugin:
    """Render JSON without importing a serialization library."""

    @staticmethod
    def _quote(value: str) -> str:
        """Escape JSON quotes, backslashes, controls and surrogates."""
        escaped = ""
        for character in value:
            if character in ('"', "\\"):
                escaped += "\\" + character
            elif ord(character) < 32 or 0xD800 <= ord(character) <= 0xDFFF:
                escaped += f"\\u{ord(character):04x}"
            else:
                escaped += character
        return '"' + escaped + '"'

    def process_output(self, data: list[tuple[int, str]]) -> None:
        """Use each processor's lifetime rank as its JSON item key."""
        fields = [
            f'"item_{rank}": {self._quote(value)}' for rank, value in data
        ]
        print("JSON Output:")
        print("{" + ", ".join(fields) + "}")


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

    def output_pipeline(self, nb: int, plugin: ExportPlugin) -> None:
        """Export up to nb items per processor; restore on plugin failure."""
        if isinstance(nb, bool) or not isinstance(nb, int) or nb < 0:
            raise ValueError("Export count must be a non-negative integer")
        if nb == 0:
            return
        for proc in self._processors:
            count = min(nb, proc.remaining)
            if count == 0:
                continue
            saved_queue = list(proc._queue)
            saved_rank = proc._next_rank
            try:
                data = [proc.output() for _ in range(count)]
                plugin.process_output(data)
            except Exception as error:
                proc._queue = saved_queue
                proc._next_rank = saved_rank
                print(f"Export failed; processor queue restored: {error}")
                return


def main() -> None:
    """Export two mixed batches through unrelated, compatible plugins."""
    print("=== Code Nexus - Data Pipeline ===")
    stream = DataStream()
    stream.print_processors_stats()
    for processor in (NumericProcessor(), TextProcessor(), LogProcessor()):
        stream.register_processor(processor)
    batch: list[Any] = [
        "Hello world", [3.14, -1, 2.71],
        [
            {"log_level": "WARNING", "log_message": "Use ssh instead"},
            {"log_level": "INFO", "log_message": "User wil is connected"},
        ],
        42, ["Hi", "five"],
    ]
    stream.process_stream(batch)
    stream.print_processors_stats()
    print("Export up to 3 items from each processor as CSV")
    stream.output_pipeline(3, CSVExportPlugin())
    stream.print_processors_stats()
    stream.process_stream([
        21, ["I love AI", "LLMs are wonderful", "Stay healthy"],
        [
            {"log_level": "ERROR", "log_message": "500 server crash"},
            {"log_level": "NOTICE", "log_message": "Certificate expires soon"},
        ],
        [32, 42, 64, 84, 128, 168], "World hello",
    ])
    stream.print_processors_stats()
    print("Export up to 5 items from each processor as JSON")
    stream.output_pipeline(5, JSONExportPlugin())
    stream.print_processors_stats()


if __name__ == "__main__":
    main()
