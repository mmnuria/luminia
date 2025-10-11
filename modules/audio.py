import pygame
import pyttsx3
import speech_recognition as sr
import threading
import time


class ControladorAudio:
    """Controla la reproducción de audio, TTS y reconocimiento de voz."""

    def __init__(self):
        # Inicialización de pygame mixer para audio
        pygame.mixer.init()
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 160)
        self.reconocedor = sr.Recognizer()
        self.microfono_listo = False
        self.esperando_respuesta = False
        self.ultima_respuesta = None
        self.hilo_escucha = None
        self._configurar_voz_inicial()

    def _configurar_voz_inicial(self):
        """Selecciona una voz por defecto."""
        voces = self.engine.getProperty('voices')
        if voces:
            self.engine.setProperty('voice', voces[0].id)

    # ------------------------------
    # Reproducción de audio pregrabado
    # ------------------------------
    def reproducir_audio(self, ruta_audio: str):
        """Reproduce un archivo de audio."""
        try:
            pygame.mixer.music.load(ruta_audio)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print(f"[Error] No se pudo reproducir el audio {ruta_audio}: {e}")

    # ------------------------------
    # Síntesis de voz (TTS)
    # ------------------------------
    def hablar(self, texto: str):
        """Convierte texto a voz con pyttsx3."""
        try:
            self.engine.say(texto)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[Error] al hablar: {e}")

    # ------------------------------
    # Reconocimiento de voz
    # ------------------------------
    def escuchar(self, idioma="es-ES", timeout=5, frase=""):
        """Escucha una respuesta de voz y la convierte a texto."""
        self.esperando_respuesta = True
        self.ultima_respuesta = None

        def _escuchar():
            with sr.Microphone() as source:
                print("🎤 Escuchando...")
                self.reconocedor.adjust_for_ambient_noise(source)
                try:
                    audio = self.reconocedor.listen(source, timeout=timeout)
                    texto = self.reconocedor.recognize_google(audio, language=idioma)
                    print(f"🗣️ Reconocido: {texto}")
                    self.ultima_respuesta = texto.lower()
                except sr.UnknownValueError:
                    print("❌ No se entendió lo que dijiste.")
                    self.ultima_respuesta = ""
                except Exception as e:
                    print(f"[Error en escucha]: {e}")
                finally:
                    self.esperando_respuesta = False

        self.hilo_escucha = threading.Thread(target=_escuchar, daemon=True)
        self.hilo_escucha.start()

    def obtener_respuesta(self):
        """Devuelve la última respuesta reconocida."""
        return self.ultima_respuesta
