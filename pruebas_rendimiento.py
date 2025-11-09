import time
import csv
import psutil
import cv2
import numpy as np
import speech_recognition as sr

# ==========================
# CONFIGURACIÓN
# ==========================
CSV_FILE = "resultados_rendimiento.csv"
DURACION_TEST = 30  # segundos para medir FPS
MUESTRAS_VOZ = ["letras", "adivina", "animales"]

# ==========================
# FUNCIONES DE MEDICIÓN
# ==========================

def medir_latencia_voz(comando_esperado="letras"):
    """Mide el tiempo desde el inicio de escucha hasta la respuesta procesada."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n Diga el comando:", comando_esperado)
        inicio = time.time()
        audio = recognizer.listen(source)
        fin_escucha = time.time()
        try:
            texto = recognizer.recognize_google(audio, language="es-ES")
        except sr.UnknownValueError:
            texto = "No reconocido"
        fin_total = time.time()

    latencia_escucha = fin_escucha - inicio
    latencia_total = fin_total - inicio

    print(f"Reconocido: {texto}")
    print(f"Latencia escucha: {latencia_escucha:.2f}s | Latencia total: {latencia_total:.2f}s")

    return latencia_escucha, latencia_total, texto


def medir_fps(duracion=DURACION_TEST):
    """Simula renderizado y mide FPS promedio usando OpenCV."""
    print("\n Iniciando prueba de FPS...")
    start = time.time()
    frame_count = 0

    while time.time() - start < duracion:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, f"Frame {frame_count}", (50, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow("Luminia - Prueba FPS", frame)
        frame_count += 1

        if cv2.waitKey(1) == ord('q'):
            break

    end = time.time()
    fps = frame_count / (end - start)
    cv2.destroyAllWindows()
    print(f"FPS promedio: {fps:.2f}")
    return fps


def medir_recursos():
    """Obtiene uso actual de CPU y memoria."""
    cpu = psutil.cpu_percent(interval=1)
    memoria = psutil.virtual_memory().percent
    print(f"CPU: {cpu:.1f}% | RAM: {memoria:.1f}%")
    return cpu, memoria


# ==========================
# EJECUCIÓN PRINCIPAL
# ==========================
if __name__ == "__main__":
    print("\n Iniciando pruebas de rendimiento del sistema Luminia")

    # Cabecera CSV
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Comando", "Latencia_escucha_s", "Latencia_total_s",
                         "Texto_reconocido", "FPS_promedio", "CPU_%", "Memoria_%"])

    for comando in MUESTRAS_VOZ:
        lat_escucha, lat_total, texto = medir_latencia_voz(comando)
        fps = medir_fps()
        cpu, mem = medir_recursos()

        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([comando, lat_escucha, lat_total, texto, fps, cpu, mem])

    print(f"\n Resultados guardados en: {CSV_FILE}")
    print(" Pruebas finalizadas con éxito.")
