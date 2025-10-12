import pyttsx3
import pygame
import queue
import threading
import time
import os

class TTSManager:
    """Motor TTS y reproductor de audio que corre en un hilo y usa una queue para no bloquear el main loop."""
    def __init__(self, rate=170, volume=1.0, min_interval=1.5):
        # Inicializar pygame para audio
        pygame.mixer.init()
        # Inicializar pyttsx3 para TTS
        self.engine = pyttsx3.init()
        for voice in self.engine.getProperty('voices'):
            if "spanish" in voice.name.lower() or "monica" in voice.name.lower() or "jorge" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        self.queue = queue.Queue()
        self.last_spoken = {}
        self.min_interval = min_interval
        self._running = True
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def _worker(self):
        while self._running:
            item = self.queue.get()
            if item is None:
                break
            try:
                if isinstance(item, tuple) and item[0] == "audio_file":
                    # Reproducir archivo de audio
                    audio_file = item[1]
                    if os.path.exists(audio_file):
                        pygame.mixer.music.load(audio_file)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
                    else:
                        print(f"[TTS] Audio no encontrado: {audio_file}")
                else:
                    # Usar TTS para texto
                    text = item
                    self.engine.say(text)
                    self.engine.runAndWait()
            except Exception as e:
                print(f"[TTS error] {e}")
            finally:
                self.queue.task_done()

    def speak(self, text):
        """Enqueue texto para TTS."""
        self.queue.put(text)

    def play_audio(self, audio_file):
        """Enqueue archivo de audio para reproducción."""
        self.queue.put(("audio_file", audio_file))

    def announce(self, text, key=None, min_interval=None):
        """Enqueue texto pero evita repetirlo continuamente."""
        if key is None:
            key = text
        if min_interval is None:
            min_interval = self.min_interval
        last = self.last_spoken.get(key)
        now = time.time()
        if last and last[0] == text and (now - last[1]) < min_interval:
            return
        self.last_spoken[key] = (text, now)
        self.speak(text)

    def stop(self):
        self._running = False
        self.queue.put(None)
        pygame.mixer.music.stop()
        self.thread.join(timeout=1)

def speak_print(text, key=None):
    print(text)
    tts_manager = globals().get('tts_manager')
    if tts_manager:
        tts_manager.announce(text, key=key)