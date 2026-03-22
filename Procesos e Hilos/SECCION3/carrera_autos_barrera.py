# carrera_autos_barrera.py

import threading
import time
import random

def auto(id_auto, barrera):
    # Simular tiempo aleatorio para llegar a la pista
    tiempo_llegada = random.uniform(0.5, 2.0)
    time.sleep(tiempo_llegada)
    
    print(f"Auto {id_auto} llegó a la salida y está esperando.")
    
    try:
        # Los autos esperan aquí hasta que el contador de la barrera llegue a 5
        barrera.wait()
        
        # Acción después de que la barrera se libere
        print(f"Auto {id_auto} inició la carrera.")
    except threading.BrokenBarrierError:
        # Manejo de errores en caso de que un hilo falle o la barrera se resetee
        print(f"Auto {id_auto}: La carrera fue cancelada.")

# Crear una barrera para 5 hilos
# El parámetro 'action' es opcional y se ejecuta una sola vez cuando se libera la barrera
def anunciar_inicio():
    print("--- ¡CARRERA! ---")

NUM_AUTOS = 5
barrera_salida = threading.Barrier(NUM_AUTOS, action=anunciar_inicio)

# Iniciar los 5 hilos
autos_hilos = []
for i in range(1, NUM_AUTOS + 1):
    t = threading.Thread(target=auto, args=(i, barrera_salida))
    autos_hilos.append(t)
    t.start()

# Esperar a que todos terminen para cerrar el programa principal
for t in autos_hilos:
    t.join()