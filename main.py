# main.py
import os
import cv2
import time
import threading
import speech_recognition as sr
from modules.data_manager import MongoDBManager

# --- Configuración y AR ---
from config.calibracion import cargar_calibracion
from ar.deteccion import crear_detector
from utils.operaciones import bestBackend, myVideo

# --- Núcleo del juego ---
from modules.game_state import GameState
from modules.audio_manager import AudioManager
from modules.voice_recognition import inicializar_microfono, reconocimiento_voz
from modules.ui_renderer import realidad_mixta, render_ui
from modules.gestor_juegos import GestorJuegosAR

# --- Modelos disponibles ---
from models.modelos import rutas_frutas, rutas_letras, rutas_animales, rutas_verduras, rutas_numeros


def main():
    print("\nIniciando Mundo de Luminia")

    # --- Estado global ---
    mongo = MongoDBManager()
    state = GameState()
    escenas = {}
    voice_thread_active = [True]

    # Conectar a MongoDB
    try:
        mongo.conectar()
        print("Conexión a MongoDB establecida correctamente")
    except Exception as e:
        print(f"Error crítico al conectar con MongoDB: {e}")
        return

    # --- Inicializar Audios ---
    try:
        audio_manager = AudioManager(
            on_talk_start=lambda: setattr(state, "microfono_listo", False),
            on_talk_end=lambda: (
                setattr(state, "microfono_listo", True),
                setattr(state, "intro_terminada", True)
            )
        )
        state.audio = audio_manager

        intro_audio = "audios/introduccion.mp3"
        if os.path.exists(intro_audio):
            print("Reproduciendo introducción de Tina...")
            audio_manager.play_audio(intro_audio)
        else:
            print("[audio] No se encontró audio de introducción.")

    except Exception as e:
        print(f"[audio Error] {e}")
        audio_manager = None

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
    gestor = GestorJuegosAR(ui_renderer=None, voice_system=audio_manager, game_state=state)
    state.gestor_juegos = gestor

    # --- Inicializar reconocimiento de voz ---
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    hilo_microfono = threading.Thread(target=inicializar_microfono, args=(state, recognizer, microphone), daemon=True)
    hilo_voz = threading.Thread(target=reconocimiento_voz, args=(state, recognizer, microphone, voice_thread_active), daemon=True)
    hilo_microfono.start()
    hilo_voz.start()

    print("Cámara lista — mira a la cámara para comenzar")
    print(" Marcadores disponibles:")
    print(f" Letras: {len(rutas_letras)} | Animales: {len(rutas_animales)} | Frutas: {len(rutas_frutas)} | Verduras: {len(rutas_verduras)} | Números: {len(rutas_numeros)}")

    # --- Estado inicial ---
    state.fase = "inicio"
    state.esperando_voz = False
    state.microfono_listo = False
    state.intro_terminada = False

    try:
        while True:
            ret, frame = ar.read()
            if not ret:
                continue

            # Render principal (UI + AR + Tina)
            frame = render_ui(frame, state, detector, cameraMatrix, distCoeffs, escenas, audio_manager)
            cv2.imshow("- Luminia -", frame)

            # Salida manual
            if state.fase == "salir" or cv2.waitKey(1) == 27:
                print("🛑 Cerrando aplicación...")
                break

            if state.fase == "inicio":
                if state.intro_terminada:
                    audio_manager.announce("Vamos a comenzar con el reconocimiento facial.")
                    state.intro_terminada = False
                    state.esperando_voz = True
                    state.microfono_listo = True
                    state.fase = "reconocimiento_facial"



    except KeyboardInterrupt:
        print("\n🛑 Interrupción manual del usuario")

    finally:
        voice_thread_active[0] = False
        if audio_manager:
            audio_manager.stop()
        ar.release()
        cv2.destroyAllWindows()
        mongo.desconectar()
        print("✅ Luminia cerrado correctamente")


if __name__ == "__main__":
    main()
