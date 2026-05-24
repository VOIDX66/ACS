#!/usr/bin/env python3
"""
Milestone 3: End-of-Day Liquidators — threading.Barrier
3 hilos convierten EUR, GBP, JPY a USD. Al sincronizar en barrera,
el hilo principal imprime el total consolidado.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import threading
import time
import random

from rich.panel import Panel
from rich.table import Table
from rich.live import Live

from src.core.console import console
from src.infrastructure.sync.payment_config import payment_config


AMOUNTS = {
    "EUR": [150.00, 320.50, 89.99, 1200.00],
    "GBP": [200.00, 450.75, 67.30],
    "JPY": [25000, 18000, 9500, 3200],
}

converted: dict[str, list[float]] = {}
results_lock = threading.Lock()

barrier = threading.Barrier(3)


def run_milestone3():
    console.rule("[header]Milestone 3: Liquidación de Fin de Día — Barrier[/]")

    table = Table(title="Montos por Moneda")
    table.add_column("Moneda", style="currency")
    table.add_column("Montos")
    table.add_column("Tasa (USD)", style="amount")

    rates = payment_config.rates
    for cur, amounts in AMOUNTS.items():
        table.add_row(cur, str(amounts), f"{rates.get(cur, 1.0):.4f}")

    console.print(table)

    start = time.time()

    threads = []
    for currency in ["EUR", "GBP", "JPY"]:
        t = threading.Thread(
            target=_liquidator,
            args=(currency, AMOUNTS[currency]),
            daemon=True,
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    elapsed = time.time() - start

    total_usd = 0.0
    summary = Table(title="[header]Consolidado Final (USD)[/]", header_style="header")
    summary.add_column("Moneda", style="currency")
    summary.add_column("Montos Originales")
    summary.add_column("Convertidos (USD)", style="amount")
    summary.add_column("Subtotal (USD)", style="amount")

    for currency in ["EUR", "GBP", "JPY"]:
        originals = AMOUNTS[currency]
        convs = converted.get(currency, [])
        subtotal = sum(convs) if convs else 0
        total_usd += subtotal
        summary.add_row(
            currency,
            str([f"{a:,.2f}" for a in originals]),
            str([f"{c:,.2f}" for c in convs]),
            f"{subtotal:,.2f}",
        )

    summary.add_section()
    summary.add_row(
        "[success]TOTAL[/]",
        "",
        "",
        f"[success]{total_usd:,.2f}[/]",
    )

    console.print(summary)
    console.print(f"\n[info]Tiempo total: {elapsed:.2f}s[/]")
    console.rule("[success]Milestone 3 completado[/]")


def _liquidator(currency: str, amounts: list[float]):
    rate = payment_config.get_rate(currency)

    for amount in amounts:
        delay = random.uniform(0.1, 0.4)
        time.sleep(delay)
        usd = round(amount * rate, 2)
        console.log(
            f"[barrier]Liquidador {currency}[/] convirtiendo "
            f"[amount]{amount:,.2f} {currency}[/] → "
            f"[amount]{usd:,.2f} USD[/] (delay={delay:.2f}s)"
        )

    converted_local = [round(a * rate, 2) for a in amounts]
    with results_lock:
        converted[currency] = converted_local

    console.log(f"[barrier]Liquidador {currency}[/] esperando en [warning]barrera[/]...")
    barrier.wait()
    console.log(f"[barrier]Liquidador {currency}[/] [success]pasó la barrera[/]")


if __name__ == "__main__":
    run_milestone3()
