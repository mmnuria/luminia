import random
import time
from models.modelos import obtener_ruta_por_categoria, rutas_letras
from modules.ui_renderer import draw_text_with_background


class MundoLetrasAR:
    """
    Mundo de las Letras — uno de los mundos mágicos de Luminia.
    Contiene varios minijuegos: adivina, memoria y secuencia.
    """
    def __init__(self, ui_renderer, voice_system, game_state):
        self.ui = ui_renderer
        self.voice = voice_system
        self.state = game_state
        self.modelos_a_mostrar = []  # lista de tuplas: (categoria, letra, marker_id)

        self.juegos = {
            "adivina": self.juego_adivina_letra,
            "memoria": self.juego_memoria_letras,
            "secuencia": self.juego_secuencia_palabra
        }

        # Variables de sesión
        self.estrellas = 0
        self.ronda_actual = 0
        self.total_rondas = 3
        self.juego_en_curso = None
        self.respuesta_correcta = None

        # Recursos del mundo
        self.palabras = ["GATO", "LUNA", "MESA", "ROSA", "SOL", "CASA"]

    # ---------------------------------------------------
    # MÉTODO AUXILIAR: mostrar mensaje en pantalla
    # ---------------------------------------------------
    def mostrar_mensaje(self, texto, pos=(50, 60), color=(255, 255, 255), bg_color=(56, 118, 29), font_scale=0.7):
        """
        Dibuja un mensaje en el frame actual usando draw_text_with_background.
        """
        if hasattr(self.state, "frame_actual") and self.state.frame_actual is not None:
            draw_text_with_background(self.state.frame_actual, texto, pos, font_scale, color, bg_color)
        else:
            print(f"[MundoLetrasAR] {texto}")  # fallback por consola si no hay frame

    # ---------------------------------------------------
    # FASE DE INICIO DEL MUNDO
    # ---------------------------------------------------
    def iniciar(self):
        """
        Inicia el mundo, muestra introducción y opciones.
        """
        self.mostrar_mensaje("📖 Bienvenido al 🌈 Mundo de las Letras 🌈")
        self.mostrar_mensaje("Aquí aprenderás jugando con las letras mágicas del alfabeto.", pos=(50, 100))
        self.mostrar_mensaje("Puedes decir: 'adivina', 'memoria' o 'secuencia' para comenzar un minijuego.", pos=(50, 140))
        self.mostrar_mensaje("O di 'salir' para regresar al menú principal.", pos=(50, 180))
        self.state.fase = "mundo_letras"

    # ---------------------------------------------------
    # INICIO DE UN MINIJUEGO
    # ---------------------------------------------------
    def iniciar_juego(self, tipo):
        """
        Inicia uno de los minijuegos disponibles en este mundo.
        """
        # Limpiar escenas de castillos y modelos previos
        if hasattr(self.state, "escenas"):
            self.state.escenas.clear()

        tipo = tipo.lower()
        if tipo not in self.juegos:
            self.mostrar_mensaje("⚠️ No conozco ese minijuego. Prueba con 'adivina', 'memoria' o 'secuencia'.")
            return

        self.estrellas = 0
        self.ronda_actual = 0
        self.juego_en_curso = tipo
        self.state.fase = "jugando"

        self.mostrar_mensaje(f"🌟 ¡Comienza el minijuego {tipo.upper()}! 🌟")
        time.sleep(0.5)
        self.juegos[tipo]()

    # ---------------------------------------------------
    # PROCESAMIENTO DE RESPUESTAS POR VOZ
    # ---------------------------------------------------
    def procesar_comando(self, comando):
        """
        Procesa los comandos o respuestas habladas del jugador.
        """
        if not self.juego_en_curso:
            self.mostrar_mensaje("🎮 Di 'adivina', 'memoria' o 'secuencia' para iniciar un minijuego.")
            return

        comando = comando.strip().upper()
        print(f"[MundoLetrasAR] Comando recibido: {comando}")

        # Comparar respuesta
        if comando == self.respuesta_correcta or comando.replace(" ", "") == self.respuesta_correcta.replace(" ", ""):
            self.mostrar_mensaje("✅ ¡Muy bien! Has acertado.")
            self.estrellas += 1
        else:
            self.mostrar_mensaje(f"❌ No era '{comando}'. La respuesta correcta era '{self.respuesta_correcta}'.")

        # Avanzar ronda
        self.ronda_actual += 1
        if self.ronda_actual < self.total_rondas:
            self.mostrar_mensaje(f"⭐ Vamos con la ronda {self.ronda_actual + 1}...", pos=(50, 100))
            time.sleep(0.8)
            self.juegos[self.juego_en_curso]()
        else:
            # Termina minijuego
            self.mostrar_mensaje("🎉 ¡Has completado el minijuego!", pos=(50, 100))
            self.mostrar_mensaje(f"Ganaste {self.estrellas} estrellas 🌟", pos=(50, 140))

            # Registrar resultados y volver al menú principal
            if hasattr(self.state, "gestor_juegos"):
                self.state.gestor_juegos.registrar_resultado("letras", self.juego_en_curso, self.estrellas)
            else:
                self.mostrar_mensaje("⚠️ No se pudo registrar el progreso (gestor no disponible).", pos=(50, 180))

    # ---------------------------------------------------
    # MINIJUEGOS
    # ---------------------------------------------------

    def juego_adivina_letra(self):
        """
        Muestra tres letras aleatorias y pide decir la correcta.
        """
        letras = random.sample(list(rutas_letras.keys()), 3)
        self.respuesta_correcta = random.choice(letras)

        self.mostrar_mensaje(f"🔤 Letras mágicas aparecieron: {', '.join(letras)}", pos=(50, 60))
        self.mostrar_mensaje("Tina: 'Dime cuál de estas letras ves flotando sobre la mesa mágica.'", pos=(50, 100))

        self.modelos_a_mostrar = []
        for letra in letras:
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
            self.modelos_a_mostrar.append(("letras", letra, marker_id))

    def juego_memoria_letras(self):
        """
        Muestra una secuencia de letras que el jugador debe recordar.
        """
        secuencia = random.sample(list(rutas_letras.keys()), 3)
        self.respuesta_correcta = " ".join(secuencia)

        self.mostrar_mensaje("✨ Observa con atención las letras mágicas...", pos=(50, 60))
        for letra in secuencia:
            self.mostrar_mensaje(f"💡 {letra}", pos=(50, 100))
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
            self.modelos_a_mostrar.append(("letras", letra, marker_id))
            time.sleep(0.8)

        self.mostrar_mensaje("Tina: '¿En qué orden se encendieron? Di las letras separadas por espacio.'", pos=(50, 140))

    def juego_secuencia_palabra(self):
        """
        Pide formar una palabra letra por letra.
        """
        palabra = random.choice(self.palabras)
        self.respuesta_correcta = " ".join(list(palabra))

        self.mostrar_mensaje(f"Tina: 'Vamos a formar la palabra {palabra}. Di las letras en orden.'", pos=(50, 60))
        self.mostrar_mensaje("Ejemplo: G A T O", pos=(50, 100))

        for letra in palabra:
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
            self.modelos_a_mostrar.append(("letras", letra, marker_id))
