import threading
import time
from collections import defaultdict

from src.core.console import console
from rich.table import Table
from rich.live import Live


class MetricsCollector:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._counters = defaultdict(int)
                    cls._instance._timings: dict[str, list[float]] = defaultdict(list)
                    cls._instance._start_time = time.time()
        return cls._instance

    def increment(self, metric: str) -> None:
        with self._lock:
            self._counters[metric] += 1

    def record_timing(self, metric: str, elapsed: float) -> None:
        with self._lock:
            self._timings[metric].append(elapsed)

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "uptime": time.time() - self._start_time,
                "counters": dict(self._counters),
                "avg_timings": {
                    k: sum(v) / len(v) if v else 0
                    for k, v in self._timings.items()
                },
            }

    def display_live(self, refresh_per_second: int = 2):
        console.rule("[header]Métricas del Sistema[/]")
        table = Table(title="Métricas en Tiempo Real")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="white")
        with Live(table, console=console, refresh_per_second=refresh_per_second) as live:
            while True:
                snap = self.snapshot()
                table.rows.clear()
                table.add_row("Uptime", f"{snap['uptime']:.1f}s")
                for k, v in snap["counters"].items():
                    table.add_row(k, str(v))
                for k, v in snap["avg_timings"].items():
                    table.add_row(f"{k} (avg)", f"{v:.4f}s")
                time.sleep(1 / refresh_per_second)


metrics = MetricsCollector()
