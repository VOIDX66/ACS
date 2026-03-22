"""
Sistema de Procesamiento de Vídeos con Prioridades
====================================================
Punto de entrada.
"""

import random
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from server import VideoTranscodingServer


if __name__ == "__main__":
    random.seed(42)   # reproducibilidad para pruebas; quitar en producción

    server = VideoTranscodingServer(
        num_workers            = 3,
        max_consecutive_premium= 3,   # fuerza un Gratuito cada 3 Premiums consecutivos
    )

    # Agregar clientes Premium (3)
    for i in range(1, 4):
        server.add_client("premium", f"Cliente-Premium-{i}")

    # Agregar clientes Gratuitos (5)
    for i in range(1, 6):
        server.add_client("free", f"Cliente-Gratis-{i}")

    server.start()