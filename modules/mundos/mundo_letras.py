import random
import time
from models.modelosNuevo import obtener_ruta_por_categoria, rutas_letras

class MundoLetrasAR:
    def __init__(self, ui_renderer, voice_system, game_state):
        self.ui = ui_renderer
        self.voice = voice_system
        self.state = game_state

        self.juegos = {
            "adivina": self.juego_adivina_letra,
            "memoria": self.juego_memoria_letras,
            "secuencia": self.juego_secuencia_palabra
        }

        self.estrellas = 0
        self.ronda_actual = 0
        self.total_rondas = 3
        self.juego_en_curso = None
        self.palabras = ["GATO", "LUNA", "MESA", "ROSA", "SOL", "CASA"]

    def iniciar(self):
        self.ui.mostrar_mensaje("📖 Bienvenido al Mundo de las Letras.")
        self.ui.mostrar_mensaje("Aquí aprenderás jugando con las letras mágicas del alfabeto.")
        self.ui.mostrar_mensaje("Puedes decir: 'adivina', 'memoria' o 'secuencia' para comenzar un minijuego.")
        self.ui.mostrar_mensaje("O di 'salir' para regresar al menú principal.")
        # Mostrar castillo en marcador 1 (ya manejado en ui_renderer)

    def iniciar_juego(self, tipo):
        if tipo not in self.juegos:
            self.ui.mostrar_mensaje("⚠️ No conozco ese minijuego. Prueba con 'adivina', 'memoria' o 'secuencia'.")
            return

        self.estrellas = 0
        self.ronda_actual = 0
        self.juego_en_curso = tipo

        self.ui.mostrar_mensaje(f"🌟 Comenzamos el juego: {tipo.upper()} 🌟")
        self.juegos[tipo]()

    def procesar_comando(self, comando):
        if not self.juego_en_curso:
            self.ui.mostrar_mensaje("No hay un juego activo. Di 'adivina', 'memoria' o 'secuencia' para jugar.")
            return

        comando = comando.strip().upper()

        if comando == self.respuesta_correcta:
            self.ui.mostrar_mensaje("✅ ¡Muy bien! Has acertado.")
            self.estrellas += 1
        else:
            self.ui.mostrar_mensaje(f"❌ No era {comando}. La respuesta correcta era {self.respuesta_correcta}.")

        self.ronda_actual += 1
        if self.ronda_actual < self.total_rondas:
            self.ui.mostrar_mensaje(f"⭐ Vamos con la ronda {self.ronda_actual + 1}...")
            self.juegos[self.juego_en_curso]()
        else:
            self.ui.mostrar_mensaje("🎉 ¡Has completado el minijuego!")
            self.ui.mostrar_mensaje(f"Ganaste {self.estrellas} estrellas 🌟")
            self.state.gestor_juegos.registrar_resultado("letras", self.juego_en_curso, self.estrellas)

    def juego_adivina_letra(self):
        letras = random.sample(list(rutas_letras.keys()), 3)
        self.respuesta_correcta = random.choice(letras)

        self.ui.mostrar_mensaje(f"🔤 Aparecen las letras: {', '.join(letras)}")
        self.ui.mostrar_mensaje("Tina: 'Dime qué letras ves.'")
        self.ui.mostrar_mensaje("(Responde con una letra, por ejemplo: A, B, C...)")
        for letra in letras:
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])  # Todos menos 0
            self.ui.mostrar_modelo("letras", letra, marker_id)

    def juego_memoria_letras(self):
        secuencia = random.sample(list(rutas_letras.keys()), 3)
        self.respuesta_correcta = " ".join(secuencia)

        self.ui.mostrar_mensaje("✨ Observa con atención las letras mágicas...")
        for letra in secuencia:
            self.ui.mostrar_mensaje(f"💡 {letra}")
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])  # Todos menos 0
            self.ui.mostrar_modelo("letras", letra, marker_id)
            time.sleep(0.8)
        self.ui.mostrar_mensaje("Tina: '¿En qué orden se encendieron?' (di las letras separadas por espacio)")

    def juego_secuencia_palabra(self):
        palabra = random.choice(self.palabras)
        self.respuesta_correcta = " ".join(list(palabra))

        self.ui.mostrar_mensaje(f"Tina: 'Vamos a formar la palabra {palabra}. Di las letras en orden.'")
        self.ui.mostrar_mensaje("(Ejemplo: G A T O)")
        for letra in palabra:
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])  # Todos menos 0
            self.ui.mostrar_modelo("letras", letra, marker_id)