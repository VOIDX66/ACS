# temporizador_con_timeout.py

import threading
import time
import random

# Simular la conexión al servicio
def conectar_a_servicio(evento_cancelacion):
    tiempo_espera = random.randint(1, 5)
    print(f"Intentando conectar (tiempo estimado: {tiempo_espera}s)...")
    
    # Simulamos el trabajo en pequeños intervalos para poder reaccionar al evento
    # de cancelación casi en tiempo real.
    paso = 0.1
    acumulado = 0
    while acumulado < tiempo_espera:
        if evento_cancelacion.is_set():
            return None # Operación abortada
        time.sleep(paso)
        acumulado += paso
        
    return "Conectado"

# Función que ejecuta el Timer si el tiempo se agota
def timeout_expirado(evento_cancelacion):
    print("\n[TIMEOUT] El tiempo límite de 2 segundos ha expirado.")
    evento_cancelacion.set()

# Lógica principal (Main)
def ejecutar_monitoreo():
    # Creamos el evento de control
    evento_cancelacion = threading.Event()
    
    # Iniciamos el temporizador de 2 segundos
    temporizador = threading.Timer(2.0, timeout_expirado, args=(evento_cancelacion,))
    temporizador.start()
    
    # Intentamos la conexión
    resultado = conectar_a_servicio(evento_cancelacion)
    
    # Si la conexión terminó antes que el timer, lo cancelamos
    if temporizador.is_alive():
        temporizador.cancel()
    
    # Verificación final
    if evento_cancelacion.is_set() or resultado is None:
        print("Resultado: Operación cancelada por timeout.")
    else:
        print(f"Resultado: Conexión exitosa: {resultado}")

if __name__ == "__main__":
    ejecutar_monitoreo()