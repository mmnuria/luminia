import os
import cv2
import time
import speech_recognition as sr
import threading
from config.calibracion import cargar_calibracion
from ar.deteccion import crear_detector
from modules.cuia import bestBackend, myVideo
from modules.game_state import GameState, JUEGO_ACTUAL
from modules.tts_manager import TTSManager, speak_print
from modules.voice_recognition import inicializar_microfono, reconocimiento_voz
from modules.ui_renderer import realidad_mixta, render_ui
from modules.juegos import GestorJuegosAR
from models.modelos import MODELOS_FRUTAS_VERDURAS

def iniciar_juego(juego_id, state):
    global JUEGO_ACTUAL
    JUEGO_ACTUAL = juego_id
    state.fase = "escaneo_inicial"
    state.tiempo_escaneo = time.time()
    juego_data = state.usuario_data.get("juegos", {}).get(juego_id, {})
    state.marcadores_respondidos = set(juego_data.get("respondidos", []))
    state.puntuacion = juego_data.get("puntuacion", 0)
    print(f" Juego {juego_id} iniciado con progreso cargado")

def main():
    global tts_manager
    state = GameState()
    state.gestor_juegos = GestorJuegosAR()
    escenas = {}
    voice_thread_active = [True]  # Use list to allow modification in threads
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # Inicializar TTS
    try:
        tts_manager = TTSManager()
        audio_intro = "audios/introduccion.mp3"
        if os.path.exists(audio_intro):
            tts_manager.play_audio(audio_intro)
            print("Reproduciendo audio de introducción...")
        else:
            print(f"[TTS] No se encontró el audio: {audio_intro}")
    except Exception as e:
        print(f"[TTS init error] {e}")
        tts_manager = None

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

    hilo_microfono = threading.Thread(target=inicializar_microfono, args=(state, recognizer, microphone), daemon=True)
    hilo_microfono.start()
    hilo_voz = threading.Thread(target=reconocimiento_voz, args=(state, recognizer, microphone, voice_thread_active), daemon=True)
    hilo_voz.start()

    print("🎮 Kids&Veggies iniciado - Mira a la cámara para comenzar")
    print(" Marcadores disponibles:")
    for marker_id, info in MODELOS_FRUTAS_VERDURAS.items():
        print(f"   ID {marker_id}: {info['nombre']} ({info['tipo']})")

    try:
        while True:
            ret, frame = ar.read()
            if not ret:
                continue
            frame = render_ui(frame, state, detector, cameraMatrix, distCoeffs, escenas, tts_manager)
            cv2.imshow("Kids&Veggies - AR Learning Game", frame)
            if state.fase == "salir" or cv2.waitKey(1) == 27:
                break
    except KeyboardInterrupt:
        print("\n🛑 Aplicación interrumpida por el usuario")
    finally:
        voice_thread_active[0] = False
        if tts_manager:
            tts_manager.stop()
        ar.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()