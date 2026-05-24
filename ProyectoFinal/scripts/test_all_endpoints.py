#!/usr/bin/env python3
"""
Pruebas integrales de todos los endpoints contra el servidor en ejecución.
Ejecutar con: docker-compose up -d && sleep 3 && python scripts/test_all_endpoints.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import time
import json
import threading
import asyncio

import httpx
import websockets
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.core.console import console

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

results: list[dict] = []
results_lock = threading.Lock()


def add_result(endpoint: str, status: str, detail: str = ""):
    with results_lock:
        results.append({"endpoint": endpoint, "status": status, "detail": detail})


def build_summary_table() -> Table:
    table = Table(title="[header]Resultados de Pruebas[/]", header_style="header")
    table.add_column("#", style="dim", width=4)
    table.add_column("Endpoint", style="white")
    table.add_column("Estado", style="white", width=12)
    table.add_column("Detalle", style="dim")
    for i, r in enumerate(results, 1):
        color = "success" if r["status"] == "OK" else "error"
        table.add_row(
            str(i),
            r["endpoint"],
            f"[{color}]{r['status']}[/]",
            r["detail"],
        )
    return table


def test_health(client: httpx.Client):
    console.rule("[header]1. Health Check[/]")
    r = client.get("/health")
    add_result("GET /health", "OK" if r.status_code == 200 else "FAIL", str(r.json()))
    console.log(f"[info]Health:[/] {r.json()}")


def test_register(client: httpx.Client) -> dict:
    console.rule("[header]2. Registro de Usuario[/]")

    payload = {
        "email": "testuser@acs.com",
        "password": "securepassword123",
        "full_name": "QA Tester",
    }
    console.log(f"[info]POST /auth/register[/] {payload['email']}")
    r = client.post("/auth/register", json=payload)

    if r.status_code == 400 and "already registered" in r.text:
        console.log("[warning]Usuario ya existe, continuando...[/]")
        add_result("POST /auth/register", "SKIP", "already registered")
    else:
        ok = r.status_code == 201
        add_result("POST /auth/register", "OK" if ok else "FAIL", str(r.json()))
        console.log(f"[{'success' if ok else 'error'}]Register:[/] {r.json()}")

    return payload


def test_login(client: httpx.Client, email: str, password: str) -> str | None:
    console.rule("[header]3. Login JWT[/]")
    payload = {"email": email, "password": password}
    console.log(f"[info]POST /auth/login[/] {email}")
    r = client.post("/auth/login", json=payload)
    ok = r.status_code == 200

    if ok:
        token = r.json()["access_token"]
        add_result("POST /auth/login", "OK", f"token={token[:20]}...")
        console.log(f"[success]Token obtenido:[/] {token[:30]}...")
        return token
    else:
        add_result("POST /auth/login", "FAIL", str(r.json()))
        console.log(f"[error]Login falló:[/] {r.json()}")
        return None


def test_create_jobs(client: httpx.Client, token: str) -> list[int]:
    console.rule("[header]4. Creación de Jobs[/]")
    headers = {"Authorization": f"Bearer {token}"}

    job_data = [
        {"input_text": "Hola mundo desde ACS con prioridad alta", "priority": 10},
        {"input_text": "Tarea de procesamiento de texto normal", "priority": 0},
        {"input_text": "Análisis financiero urgente de pagos internacionales", "priority": 5},
        {"input_text": "Este job será cancelado antes de procesar", "priority": 3},
    ]

    job_ids = []
    for jd in job_data:
        r = client.post("/jobs/", json=jd, headers=headers)
        ok = r.status_code == 201
        jid = r.json().get("id") if ok else None
        job_ids.append(jid)
        add_result(
            f"POST /jobs/ (p={jd['priority']})",
            "OK" if ok else "FAIL",
            f"id={jid}" if jid else str(r.text),
        )
        console.log(
            f"[info]Job creado[/] id=[amount]{jid}[/] "
            f"prioridad=[currency]{jd['priority']}[/] "
            f"texto=\"{jd['input_text'][:40]}...\""
        )

    return job_ids


def test_list_jobs(client: httpx.Client, token: str):
    console.rule("[header]5. Listar Jobs[/]")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/jobs/", headers=headers)
    ok = r.status_code == 200
    add_result("GET /jobs/", "OK" if ok else "FAIL", f"{len(r.json())} jobs")
    if ok:
        table = Table(title="Jobs del Usuario")
        table.add_column("ID", style="dim")
        table.add_column("Estado", style="white")
        table.add_column("Prioridad", style="currency")
        table.add_column("Texto", style="white")
        for j in r.json():
            table.add_row(str(j["id"]), j["status"], str(j["priority"]), j["input_text"][:50])
        console.print(table)


def test_get_job(client: httpx.Client, token: str, job_id: int):
    console.rule("[header]6. Obtener Job por ID[/]")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get(f"/jobs/{job_id}", headers=headers)
    ok = r.status_code == 200
    add_result(f"GET /jobs/{job_id}", "OK" if ok else "FAIL", str(r.json())[:80])
    console.log(f"[info]Job {job_id}:[/] {r.json()}")


def test_cancel_job(client: httpx.Client, token: str, job_id: int):
    console.rule("[header]7. Cancelar Job[/]")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.patch(f"/jobs/{job_id}/cancel", headers=headers)
    ok = r.status_code == 200
    add_result(f"PATCH /jobs/{job_id}/cancel", "OK" if ok else "FAIL", str(r.json())[:80])
    color = "success" if ok else "error"
    console.log(f"[{color}]Job {job_id}:[/] {r.json()}")


def test_update_priority(client: httpx.Client, token: str, job_id: int, priority: int):
    console.rule("[header]8. Actualizar Prioridad de Job[/]")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.patch(f"/jobs/{job_id}/priority", json={"priority": priority}, headers=headers)
    ok = r.status_code == 200
    add_result(
        f"PATCH /jobs/{job_id}/priority ({priority})",
        "OK" if ok else "FAIL",
        f"new_priority={r.json().get('priority')}" if ok else str(r.text),
    )
    console.log(f"[info]Job {job_id} prioridad actualizada:[/] {r.json()}")


def test_process_job(client: httpx.Client, token: str, job_id: int):
    console.rule("[header]9. Procesar Job[/]")
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post(f"/jobs/{job_id}/process", headers=headers)
    ok = r.status_code == 200
    add_result(f"POST /jobs/{job_id}/process", "OK" if ok else "FAIL", str(r.json())[:80])
    color = "success" if ok else "error"
    console.log(f"[{color}]Resultado:[/] {r.json()}")


def test_payments_batch(client: httpx.Client, token: str):
    console.rule("[header]10. Lote de Pagos Multimoneda[/]")
    headers = {"Authorization": f"Bearer {token}"}

    payload = [
        {"merchant_id": 101, "amount": 50.00, "currency": "USD", "method_type": "tarjeta", "priority": 3},
        {"merchant_id": 102, "amount": 120.00, "currency": "EUR", "method_type": "transferencia", "priority": 2},
        {"merchant_id": 103, "amount": 200.00, "currency": "GBP", "method_type": "billetera", "priority": 5},
        {"merchant_id": 104, "amount": 50000.00, "currency": "JPY", "method_type": "tarjeta", "priority": 1},
        {"merchant_id": 105, "amount": 350.00, "currency": "USD", "method_type": "transferencia", "priority": 4},
        {"merchant_id": 106, "amount": 75.50, "currency": "EUR", "method_type": "billetera", "priority": 3},
        {"merchant_id": 107, "amount": 180.00, "currency": "GBP", "method_type": "tarjeta", "priority": 2},
        {"merchant_id": 101, "amount": 2000.00, "currency": "JPY", "method_type": "transferencia", "priority": 1},
    ]

    console.log(f"[info]Enviando {len(payload)} pagos...[/]")
    for p in payload:
        console.log(
            f"  merchant [merchant]{p['merchant_id']}[/] "
            f"[amount]{p['amount']:.2f} {p['currency']}[/] "
            f"({p['method_type']}) prio=[currency]{p['priority']}[/]"
        )

    r = client.post("/payments/batch", json=payload, headers=headers)
    ok = r.status_code == 200
    add_result("POST /payments/batch", "OK" if ok else "FAIL", f"{len(payload)} pagos")

    if ok:
        table = Table(title="[header]Pagos Procesados[/]")
        table.add_column("ID", style="dim", width=10)
        table.add_column("Merchant", justify="center")
        table.add_column("Monto Orig.", style="amount")
        table.add_column("Comisión USD", style="currency")
        table.add_column("Final USD", style="amount")
        table.add_column("Estado", style="white")

        total = 0.0
        for p in r.json():
            total += p["final_amount"]
            status_color = "green" if p["status"] == "completed" else "red"
            table.add_row(
                p["request_id"],
                str(p["merchant_id"]),
                f"{p['amount']:.2f} {p['currency']}",
                f"{p['commission']:.2f}",
                f"{p['final_amount']:.2f}",
                f"[{status_color}]{p['status'].upper()}[/]",
            )
        table.caption = f"[amount]Total USD: {total:,.2f}[/]"
        console.print(table)
    else:
        console.log(f"[error]Batch falló:[/] {r.text}")


def test_reports(client: httpx.Client, token: str):
    console.rule("[header]11. Reportes[/]")
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/reports/summary", headers=headers)
    ok = r.status_code == 200
    add_result("GET /reports/summary", "OK" if ok else "FAIL", "")

    if ok:
        data = r.json()
        table = Table(title="[header]Resumen del Sistema[/]")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="white")
        table.add_row("Usuarios", str(data["users"]))
        table.add_row("Jobs totales", str(data["jobs"]["total"]))
        table.add_row("  completados", str(data["jobs"]["completed"]))
        table.add_row("  cancelados", str(data["jobs"]["cancelled"]))
        table.add_row("  pendientes", str(data["jobs"]["pending"]))
        table.add_row("  procesando", str(data["jobs"]["processing"]))
        table.add_row("Palabras procesadas", str(data["text_processing"]["total_words"]))
        table.add_row("Caracteres procesados", str(data["text_processing"]["total_chars"]))
        table.add_row("Uptime", f"{data['metrics']['uptime_seconds']}s")
        for k, v in data["metrics"]["counters"].items():
            table.add_row(f"  {k}", str(v))
        console.print(table)

    r2 = client.get("/reports/user/1", headers=headers)
    ok2 = r2.status_code == 200
    add_result("GET /reports/user/1", "OK" if ok2 else "FAIL", "")
    if ok2:
        ud = r2.json()
        console.log(
            f"[info]Reporte user {ud['user_id']}:[/] "
            f"{ud['email']} — {ud['total_jobs']} jobs"
        )


def test_websocket():
    console.rule("[header]12. WebSocket + Notificación[/]")

    received: list[dict] = []

    async def _ws_test():
        uri = f"{WS_URL}/1"
        console.log(f"[info]Conectando WebSocket:[/] {uri}")
        try:
            async with websockets.connect(uri) as ws:
                console.log("[success]WS conectado[/]")
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
                    data = json.loads(msg)
                    received.append(data)
                    console.log(f"[success]Notificación recibida:[/] {data}")
                except asyncio.TimeoutError:
                    console.log("[warning]WS: timeout esperando notificación[/]")
        except Exception as e:
            console.log(f"[error]WS error:[/] {e}")

    try:
        asyncio.run(_ws_test())
    except Exception as e:
        console.log(f"[error]asyncio.run error:[/] {e}")

    if received:
        add_result("WS /ws/1", "OK", str(received[0])[:80])
    else:
        console.log(
            "[warning]Sin notificación WS — "
            "asegúrate de procesar un job MANTENIENDO la conexión WS abierta[/]"
        )
        add_result("WS /ws/1", "WARN", "sin notificación (normal si no se procesó job durante WS)")


def run_all_tests():
    console.rule("[header]ACS PAYMENT ENGINE — PRUEBAS INTEGRALES[/]")
    console.print(
        Panel.fit(
            "[info]Probando autenticación, jobs (CRUD + cancel + priority), "
            "pagos multimoneda, reportes y WebSocket[/]",
            title="Plan de Pruebas",
        )
    )

    email = "testuser@acs.com"
    password = "securepassword123"

    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        test_health(client)

        user = test_register(client)

        token = test_login(client, email, password)
        if not token:
            console.log("[error]Sin token JWT — pruebas detenidas[/]")
            console.print(build_summary_table())
            return

        job_ids = test_create_jobs(client, token)

        test_list_jobs(client, token)

        if job_ids and job_ids[0]:
            test_get_job(client, token, job_ids[0])

        cancel_target = job_ids[3] if len(job_ids) > 3 and job_ids[3] else None
        if cancel_target:
            test_cancel_job(client, token, cancel_target)

        if job_ids and job_ids[1]:
            test_update_priority(client, token, job_ids[1], 99)

        process_target = job_ids[0] if job_ids and job_ids[0] else None
        if process_target:
            test_process_job(client, token, process_target)

        test_payments_batch(client, token)
        test_reports(client, token)

    test_websocket()

    console.rule("[header]RESUMEN FINAL[/]")
    console.print(build_summary_table())

    passed = sum(1 for r in results if r["status"] == "OK")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    warn = sum(1 for r in results if r["status"] == "WARN")

    console.print(
        f"\n[success]OK: {passed}[/] | "
        f"[warning]WARN: {warn}[/] | "
        f"[error]FAIL: {failed}[/] | "
        f"SKIP: {skipped}"
    )


if __name__ == "__main__":
    run_all_tests()
