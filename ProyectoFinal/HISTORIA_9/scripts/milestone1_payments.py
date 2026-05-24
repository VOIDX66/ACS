#!/usr/bin/env python3
"""
Milestone 1: Pagos Internacionales — Productor/Consumidor
Simula 15 pagos desde productores (hilos) procesados por N=3 workers.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import threading
import time
from random import choice, uniform

from rich.panel import Panel
from rich.table import Table

from src.core.console import console
from src.domain.entities.payment_request import PaymentRequest, MethodType
from src.infrastructure.worker_pool.pool_manager import WorkerPoolManager
from src.infrastructure.metrics.collector import metrics


CURRENCIES = ["USD", "EUR", "GBP", "JPY"]
METHODS = list(MethodType)
MERCHANTS = [101, 102, 103, 104, 105, 106, 107]


def generate_requests(count: int = 15) -> list[PaymentRequest]:
    return [
        PaymentRequest(
            merchant_id=choice(MERCHANTS),
            amount=round(uniform(10, 500), 2),
            currency=choice(CURRENCIES),
            method_type=choice(METHODS),
        )
        for _ in range(count)
    ]


def run_milestone1():
    console.rule("[header]Milestone 1: Pagos Internacionales — Producer/Consumer[/]")
    console.print(
        Panel.fit(
            "[info]15 pagos | Cola max=20 | 3 Workers | Comisión 5%[/]",
            title="Configuración",
        )
    )

    requests = generate_requests(15)
    pool = WorkerPoolManager(num_workers=3)

    start = time.time()
    pool.start()

    producers = []
    for i, req in enumerate(requests, 1):
        t = threading.Thread(
            target=_produce,
            args=(i, req, pool.queue),
            daemon=True,
        )
        t.start()
        producers.append(t)

    for t in producers:
        t.join()

    pool.join()
    elapsed = time.time() - start

    table = Table(title="[header]Resumen de Pagos[/]", header_style="header")
    table.add_column("ID", style="dim", width=10)
    table.add_column("Merchant", justify="center")
    table.add_column("Monto Orig.")
    table.add_column("Comisión")
    table.add_column("Final (USD)")
    table.add_column("Estado")

    total = 0.0
    for r in requests:
        total += r.final_amount
        status_color = {
            "pending": "yellow",
            "processing": "cyan",
            "completed": "green",
            "failed": "red",
        }.get(r.status.value, "white")

        table.add_row(
            r.request_id,
            str(r.merchant_id),
            r.display_amount,
            r.display_commission,
            r.display_final,
            f"[{status_color}]{r.status.value.upper()}[/]",
        )

    console.print(table)
    console.print(f"\n[amount]Total liquidado:[/] [success]{total:,.2f} USD[/]")
    console.print(f"[info]Tiempo total: {elapsed:.2f}s[/]")

    summary = Table(title="Balance por Merchant")
    summary.add_column("Merchant", style="merchant")
    summary.add_column("Saldo (USD)", style="amount")
    for mid in sorted(set(r.merchant_id for r in requests)):
        summary.add_row(str(mid), f"{pool.repo.get_balance(mid):,.2f}")

    console.print(summary)
    console.rule("[success]Milestone 1 completado[/]")


def _produce(pid: int, request: PaymentRequest, queue):
    queue.enqueue(request)
    console.log(
        f"[producer]Productor {pid}[/] encolando: "
        f"merchant [merchant]{request.merchant_id}[/] "
        f"[amount]{request.display_amount}[/]"
    )


if __name__ == "__main__":
    run_milestone1()
