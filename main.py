# main.py
import os
import cv2
import time
import threading
import speech_recognition as sr

# --- Configuración y AR ---
from config.calibracion import cargar_calibracion
from ar.deteccion import crear_detector
from modules.cuia import bestBackend, myVideo

# --- Núcleo del juego ---
from modules.game_state import GameState
from modules.tts_manager import TTSManager
from modules.voice_recognition import inicializar_microfono, reconocimiento_voz
from modules.ui_renderer import realidad_mixta, render_ui
from modules.gestorJuegos import GestorJuegosAR

# --- Modelos disponibles ---
from models.modelos import rutas_frutas, rutas_letras, rutas_animales, rutas_verduras, rutas_numeros


def main():
    print("\n🌈 Iniciando Kids&Veggies - Mundo de Luminia 🌟")

    # --- Estado global ---
    state = GameState()
    escenas = {}
    voice_thread_active = [True]

    # --- Inicializar TTS ---
    try:
        tts_manager = TTSManager(
            on_talk_start=lambda: setattr(state, "microfono_listo", False),
            on_talk_end=lambda: setattr(state, "microfono_listo", True)
        )
        state.tts = tts_manager

        intro_audio = "audios/introduccion.mp3"
        if os.path.exists(intro_audio):
            print("🔊 Reproduciendo introducción de Tina...")
            tts_manager.play_audio(intro_audio)
        else:
            print("[TTS] ⚠️ No se encontró audio de introducción.")

    except Exception as e:
        print(f"[TTS Error] {e}")
        tts_manager = None

    # --- Inicializar cámara y AR ---
    cam = 0
    bk = bestBackend(cam)
    webcam = cv2.VideoCapture(cam, bk)
    ancho = int(webcam.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(webcam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    webcam.release()

    cameraMatrix, distCoeffs = cargar_calibracion(ancho, alto)
    detector = crear_detector()

    ar = myVideo(cam, bk)
    ar.process = lambda frame: realidad_mixta(frame.copy(), detector, cameraMatrix, distCoeffs, state, escenas)

    # --- Inicializar Gestor de Juegos ---
    gestor = GestorJuegosAR(ui_renderer=None, voice_system=tts_manager, game_state=state)
    state.gestor_juegos = gestor

    # --- Inicializar reconocimiento de voz ---
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    hilo_microfono = threading.Thread(target=inicializar_microfono, args=(state, recognizer, microphone), daemon=True)
    hilo_voz = threading.Thread(target=reconocimiento_voz, args=(state, recognizer, microphone, voice_thread_active), daemon=True)
    hilo_microfono.start()
    hilo_voz.start()

    print("📸 Cámara lista — mira a la cámara para comenzar")
    print(" Marcadores disponibles:")
    print(f" Letras: {len(rutas_letras)} | Animales: {len(rutas_animales)} | Frutas: {len(rutas_frutas)} | Verduras: {len(rutas_verduras)} | Números: {len(rutas_numeros)}")

    # --- Estado inicial ---
    state.fase = "inicio"
    state.esperando_voz = True
    state.microfono_listo = True

    try:
        while True:
            ret, frame = ar.read()
            if not ret:
                continue

            # Render principal (UI + AR + Tina)
            frame = render_ui(frame, state, detector, cameraMatrix, distCoeffs, escenas, tts_manager)
            cv2.imshow("Kids&Veggies - Luminia", frame)

            # Salida manual
            if state.fase == "salir" or cv2.waitKey(1) == 27:
                print("🛑 Cerrando aplicación...")
                break

            # Flujo inicial automatizado
            if state.fase == "inicio":
                time.sleep(2)
                tts_manager.announce("Vamos a comenzar con el reconocimiento facial.")
                state.fase = "reconocimiento_facial"

    except KeyboardInterrupt:
        print("\n🛑 Interrupción manual del usuario")

    finally:
        voice_thread_active[0] = False
        if tts_manager:
            tts_manager.stop()
        ar.release()
        cv2.destroyAllWindows()
        print("✅ Kids&Veggies cerrado correctamente")


if __name__ == "__main__":
    main()
