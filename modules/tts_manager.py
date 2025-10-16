import pygame
import queue
import threading
import time
import os

class TTSManager:
    """
    Gestor de audio para Tina.
    Reproduce audios usando pygame.mixer y pausa el micrófono mientras habla.
    """

    def __init__(self, min_interval=1.5, on_talk_start=None, on_talk_end=None):
        pygame.mixer.init()
        self.queue = queue.Queue()
        self.last_spoken = {}
        self.min_interval = min_interval
        self._running = True

        # Callbacks (para controlar el estado del micro)
        self.on_talk_start = on_talk_start
        self.on_talk_end = on_talk_end

        # Hilo que procesa la cola de audios
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    # -----------------------------------------------------
    # Bucle del hilo que reproduce los audios
    # -----------------------------------------------------
    # def _worker(self):
    #     while self._running:
    #         item = self.queue.get()
    #         if item is None:
    #             break

    #         try:
    #             if isinstance(item, tuple) and item[0] == "audio_file":
    #                 audio_file = item[1]
    #                 if os.path.exists(audio_file):
    #                     if self.on_talk_start:
    #                         self.on_talk_start()

    #                     pygame.mixer.music.load(audio_file)
    #                     pygame.mixer.music.play()

    #                     while pygame.mixer.music.get_busy() and self._running:
    #                         time.sleep(0.1)

    #                     if self.on_talk_end:
    #                         self.on_talk_end()
    #                 else:
    #                     print(f"[TTS] ⚠️ Audio no encontrado: {audio_file}")
    #             else:
    #                 print(f"[TTS] ⚠️ Entrada no válida en la cola: {item}")
    #         except Exception as e:
    #             print(f"[TTS error] {e}")
    #         finally:
    #             self.queue.task_done()
    def _worker(self):
        while self._running:
            item = self.queue.get()
            if item is None:
                break

            try:
                if isinstance(item, tuple) and item[0] == "audio_file":
                    audio_file = item[1]
                    if os.path.exists(audio_file):
                        if self.on_talk_start:
                            self.on_talk_start()

                        pygame.mixer.music.load(audio_file)
                        pygame.mixer.music.play()

                        # 🕒 Control de timeout para evitar bloqueos
                        start_time = time.time()
                        max_duracion = 60  # seguridad: 1 minuto máx por audio
                        while pygame.mixer.music.get_busy() and self._running:
                            time.sleep(0.1)
                            # Si el audio dura demasiado (p. ej. error), forzamos salida
                            if time.time() - start_time > max_duracion:
                                print(f"[TTS] ⏰ Audio excede tiempo límite ({audio_file})")
                                break

                        # 🩵 Forzamos detener mixer y ejecutar callback final
                        pygame.mixer.music.stop()
                        if self.on_talk_end:
                            self.on_talk_end()
                    else:
                        print(f"[TTS] ⚠️ Audio no encontrado: {audio_file}")
                else:
                    print(f"[TTS] ⚠️ Entrada no válida en la cola: {item}")

            except Exception as e:
                print(f"[TTS error] {e}")
                # 🔄 Aseguramos restaurar el micro aunque haya fallos
                if self.on_talk_end:
                    self.on_talk_end()
            finally:
                self.queue.task_done()


    # -----------------------------------------------------
    # Reproduce un archivo de audio
    # -----------------------------------------------------
    def play_audio(self, audio_file):
        self.queue.put(("audio_file", audio_file))

    # -----------------------------------------------------
    # Previene repeticiones demasiado frecuentes
    # -----------------------------------------------------
    def announce(self, audio_file, key=None, min_interval=None):
        if key is None:
            key = audio_file
        if min_interval is None:
            min_interval = self.min_interval
        last = self.last_spoken.get(key)
        now = time.time()
        if last and (now - last) < min_interval:
            return
        self.last_spoken[key] = now
        self.play_audio(audio_file)

    # -----------------------------------------------------
    # Detiene todo
    # -----------------------------------------------------
    def stop(self):
        self._running = False
        pygame.mixer.music.stop()
        self.queue.put(None)
        self.thread.join(timeout=1)
