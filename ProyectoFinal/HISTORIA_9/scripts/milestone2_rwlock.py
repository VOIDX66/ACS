#!/usr/bin/env python3
"""
Milestone 2: Reader-Writer Lock con Prioridad de Escritor
10 lectores consultando tasas, 2 escritores actualizando.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import threading
import time
import random

from rich.panel import Panel
from rich.table import Table

from src.core.console import console
from src.infrastructure.sync.payment_config import payment_config


def run_milestone2():
    console.rule("[header]Milestone 2: Reader-Writer Lock — Prioridad Escritor[/]")
    console.print(
        Panel.fit(
            "[info]10 lectores (5 consultas c/u) | 2 escritores (3 actualizaciones c/u)[/]",
            title="Configuración",
        )
    )

    reader_count = 10
    writer_count = 2
    reads_per_reader = 5
    writes_per_writer = 3
    stop_event = threading.Event()

    readers: list[threading.Thread] = []
    writers: list[threading.Thread] = []

    for i in range(1, writer_count + 1):
        t = threading.Thread(
            target=_writer_worker,
            args=(i, writes_per_writer, stop_event),
            daemon=True,
        )
        writers.append(t)

    for i in range(1, reader_count + 1):
        t = threading.Thread(
            target=_reader_worker,
            args=(i, reads_per_reader, stop_event),
            daemon=True,
        )
        readers.append(t)

    start = time.time()

    for w in writers:
        w.start()
        time.sleep(0.05)

    for r in readers:
        r.start()

    for w in writers:
        w.join()
    for r in readers:
        r.join()

    elapsed = time.time() - start
    console.print(f"\n[info]Tiempo total: {elapsed:.2f}s[/]")

    table = Table(title="[header]Tasas Finales[/]")
    table.add_column("Moneda", style="currency")
    table.add_column("Tasa (USD)", style="amount")
    for currency, rate in payment_config.rates.items():
        table.add_row(currency, f"{rate:.4f}")

    console.print(table)
    console.rule("[success]Milestone 2 completado[/]")


def _reader_worker(rid: int, count: int, stop_event: threading.Event):
    currencies = list(payment_config.rates.keys())
    for i in range(count):
        if stop_event.is_set():
            break
        currency = random.choice(currencies)
        console.log(
            f"[reader]Lector {rid}[/] adquiere [info]read lock[/]"
        )
        rate = payment_config.get_rate(currency)
        console.log(
            f"[reader]Lector {rid}[/] tasa [currency]{currency}[/] = "
            f"[amount]{rate:.4f}[/] — libera read lock"
        )
        time.sleep(random.uniform(0.05, 0.15))


def _writer_worker(wid: int, count: int, stop_event: threading.Event):
    for i in range(count):
        if stop_event.is_set():
            break
        fake_rates = {
            "EUR": round(random.uniform(1.05, 1.12), 4),
            "GBP": round(random.uniform(1.24, 1.30), 4),
            "JPY": round(random.uniform(0.0065, 0.0070), 4),
        }
        console.log(
            f"[writer]Escritor {wid}[/] esperando [warning]write lock[/]..."
        )
        payment_config.update_rates(fake_rates)
        console.log(
            f"[writer]Escritor {wid}[/] [warning]actualizó tasas[/] "
            f"→ {fake_rates}"
        )
        time.sleep(0.5)


if __name__ == "__main__":
    run_milestone2()
