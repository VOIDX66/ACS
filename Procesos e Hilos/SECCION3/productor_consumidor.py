# productor_consumidor.py

import random
import threading
import time


class BufferCompartido:
    def __init__(self, capacidad):
        self.buffer = []
        self.capacidad = capacidad
        # Semáforos para control de flujo
        self.empty = threading.Semaphore(capacidad)
        self.full = threading.Semaphore(0)
        # Lock para exclusión mutua en la lista
        self.mutex = threading.Lock()

    def add_task(self, tarea, productor_id):
        self.empty.acquire()  # Espera si no hay espacio
        with self.mutex:
            self.buffer.append(tarea)
            print(f"Productor: Tarea {tarea} añadida. Buffer: {self.buffer}")
        self.full.release()  # Notifica que hay un item nuevo

    def take_task(self, consumidor_id):
        # Intentamos adquirir 'full'. Si está en 0, el consumidor duerme.
        self.full.acquire()
        with self.mutex:
            tarea = self.buffer.pop(0)
            print(
                f"Consumidor-{consumidor_id}: Tomó tarea {tarea}. Buffer: {self.buffer}"
            )
        self.empty.release()  # Notifica que hay un espacio libre
        return tarea


def productor(buffer_obj, total_tareas):
    for i in range(1, total_tareas + 1):
        time.sleep(random.uniform(0.1, 0.3))  # Simula tiempo de generación
        buffer_obj.add_task(i, "P1")


def consumidor(buffer_obj, id_cons, total_esperado, tareas_procesadas_global):
    while True:
        tarea = buffer_obj.take_task(id_cons)

        # Simular procesamiento de imagen
        time.sleep(random.uniform(0.5, 1.0))

        with threading.Lock():  # Para impresión limpia
            print(f"Consumidor-{id_cons}: Procesó tarea {tarea}.")
            tareas_procesadas_global.append(tarea)

        # Condición de salida: si ya procesamos las 20 tareas entre todos
        if len(tareas_procesadas_global) == total_esperado:
            break


# Configuración inicial
N = 10
TOTAL_TAREAS = 20
buffer_compartido = BufferCompartido(N)
procesadas = []

# Crear hilos
hilo_prod = threading.Thread(target=productor, args=(buffer_compartido, TOTAL_TAREAS))
hilos_cons = [
    threading.Thread(
        target=consumidor,
        args=(buffer_compartido, i + 1, TOTAL_TAREAS, procesadas),
        daemon=True,
    )
    for i in range(2)
]

# Iniciar
hilo_prod.start()
for c in hilos_cons:
    c.start()

# Esperar a que el productor termine y a que los consumidores procesen todo
hilo_prod.join()

# Pequeña espera para que los últimos consumidores impriman
while len(procesadas) < TOTAL_TAREAS:
    time.sleep(0.1)

print("Todas las tareas fueron procesadas.")