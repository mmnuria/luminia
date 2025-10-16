import random
import time
from models.modelos import (
    rutas_letras,
    rutas_animales,
    rutas_numeros,
    rutas_frutas,
    rutas_verduras,
    obtener_ruta_por_categoria
)


class MundoFinalAR:
    """
    🏆 Mundo Final de Luminia.
    Combina desafíos de todos los mundos anteriores: letras, animales, frutas y verduras, y números.
    Minijuegos: reto, secuencia y desafío final.
    """

    def __init__(self, ui_renderer, voice_system, game_state):
        self.ui = ui_renderer
        self.voice = voice_system
        self.state = game_state
        self.modelos_a_mostrar = []  # lista de tuplas: (categoria, objeto, marker_id)

        self.juegos = {
            "reto": self.juego_reto_mixto,
            "secuencia": self.juego_secuencia_mixta,
            "desafio": self.juego_desafio_final
        }

        self.estrellas = 0
        self.ronda_actual = 0
        self.total_rondas = 3
        self.juego_en_curso = None
        self.respuesta_correcta = None
        self.pregunta_actual = 0  # Para el desafío final
        self.retos = []

    # ---------------------------------------------------
    # INICIO DEL MUNDO FINAL
    # ---------------------------------------------------
    def iniciar(self):
        self.ui.mostrar_mensaje("🏆 Bienvenido al Mundo Final de Luminia.")
        self.ui.mostrar_mensaje("Aquí demostrarás todo lo que has aprendido en los otros mundos.")
        self.ui.mostrar_mensaje("Puedes decir: 'reto', 'secuencia' o 'desafio' para comenzar.")
        self.ui.mostrar_mensaje("O di 'salir' para regresar al menú principal.")
        self.state.fase = "mundo_final"

    # ---------------------------------------------------
    # INICIO DE JUEGO
    # ---------------------------------------------------
    def iniciar_juego(self, tipo):
        tipo = tipo.lower()
        if tipo not in self.juegos:
            self.ui.mostrar_mensaje("⚠️ No conozco ese minijuego. Prueba con 'reto', 'secuencia' o 'desafio'.")
            return

        self.estrellas = 0
        self.ronda_actual = 0
        self.juego_en_curso = tipo
        self.pregunta_actual = 0
        self.state.fase = "jugando"

        self.ui.mostrar_mensaje(f"🌟 Comienza el desafío {tipo.upper()} 🌟")
        time.sleep(0.6)
        self.juegos[tipo]()

    # ---------------------------------------------------
    # PROCESAMIENTO DE RESPUESTAS
    # ---------------------------------------------------
    def procesar_comando(self, comando):
        if not self.juego_en_curso:
            self.ui.mostrar_mensaje("🎮 No hay un juego activo. Di 'reto', 'secuencia' o 'desafio'.")
            return

        comando = comando.strip().lower()

        # Traducciones comunes
        traducciones = {
            "manzana": "Apple",
            "plátano": "Banana",
            "naranja": "Orange",
            "fresa": "Strawberry",
            "zanahoria": "Carrot",
            "pepino": "Cucumber",
            "tomate": "Tomato",
            "espinaca": "Spinach",
            "uva": "Grape",
            "uvas": "Grape",
            "vaca": "Cow",
            "perro": "Dog",
            "gato": "Cat",
            "pingüino": "Penguin",
            "pez": "Fishbowl",
            "pájaro": "Bird",
            "rana": "Frog",
            "ballena": "BowheadWhale",
            "foca": "Harp_Seal",
            "cero": "0",
            "uno": "1",
            "dos": "2",
            "tres": "3",
            "cuatro": "4",
            "cinco": "5",
            "seis": "6",
            "siete": "7",
            "ocho": "8",
            "nueve": "9",
            "diez": "10",
        }
        comando_traducido = traducciones.get(comando, comando)

        # Si estamos en el juego “desafío final”
        if self.juego_en_curso == "desafio" and self.pregunta_actual < len(self.retos):
            if comando_traducido == self.respuesta_correcta:
                self.ui.mostrar_mensaje("✅ ¡Correcto!")
                self.estrellas += 1
            else:
                self.ui.mostrar_mensaje(f"❌ No, la respuesta correcta era '{self.respuesta_correcta}'.")
            self.pregunta_actual += 1
            self._siguiente_pregunta_desafio()
            return

        # Para los otros dos juegos
        if comando_traducido == self.respuesta_correcta:
            self.ui.mostrar_mensaje("✅ ¡Excelente! Has acertado.")
            self.estrellas += 1
        else:
            self.ui.mostrar_mensaje(f"❌ No era '{comando}'. La respuesta correcta era '{self.respuesta_correcta}'.")

        # Avanzar o terminar
        self.ronda_actual += 1
        if self.ronda_actual < self.total_rondas:
            self.ui.mostrar_mensaje(f"⭐ Vamos con la ronda {self.ronda_actual + 1}...")
            time.sleep(1)
            self.juegos[self.juego_en_curso]()
        else:
            self._finalizar_juego()

    # ---------------------------------------------------
    # MINIJUEGOS
    # ---------------------------------------------------

    def juego_reto_mixto(self):
        preguntas = [
            ("🍎 ¿Cuál de estas frutas empieza con la letra M?", "Apple", "frutas", "Apple"),
            ("🐮 ¿Qué animal hace 'muuu'?", "Cow", "animales", "Cow"),
            ("🔢 ¿Qué número viene después del 4?", "5", "numeros", "5"),
            ("🔤 ¿Qué letra suena al inicio de 'Gato'?", "G", "letras", "G"),
        ]
        texto, respuesta, categoria, modelo = random.choice(preguntas)
        self.respuesta_correcta = respuesta.lower()

        self.ui.mostrar_mensaje(f"Tina: {texto}")
        marker_id = random.choice(range(1, 13))
        self.modelos_a_mostrar.append((categoria, modelo, marker_id))
        self.state.esperando_voz = True

    def juego_secuencia_mixta(self):
        secuencias = [
            ["A", "Dog", "2"],
            ["B", "Apple", "3"],
            ["C", "Cow", "5"]
        ]
        secuencia = random.choice(secuencias)
        self.respuesta_correcta = " ".join([s.lower() for s in secuencia])

        self.ui.mostrar_mensaje("✨ Tina: Recuerda esta secuencia:")
        for item in secuencia:
            categoria = self._detectar_categoria(item)
            if categoria:
                marker_id = random.choice(range(1, 13))
                self.modelos_a_mostrar.append((categoria, item, marker_id))
                self.ui.mostrar_mensaje(f"💡 {item}")
                time.sleep(0.7)
        self.ui.mostrar_mensaje("Ahora repítela en orden (ejemplo: 'a perro dos').")
        self.state.esperando_voz = True

    def juego_desafio_final(self):
        self.retos = [
            ("🐱 ¿Qué animal dice 'miau'?", "Cat", "animales", "Cat"),
            ("☀️ ¿Cuántas letras tiene la palabra 'sol'?", "3", "numeros", "3"),
            ("🔢 ¿Qué número es mayor, 7 o 9?", "9", "numeros", "9"),
        ]
        self.pregunta_actual = 0
        self._siguiente_pregunta_desafio()

    # ---------------------------------------------------
    # CONTROL INTERNO
    # ---------------------------------------------------
    def _siguiente_pregunta_desafio(self):
        if self.pregunta_actual >= len(self.retos):
            self._finalizar_juego()
            return

        texto, respuesta, categoria, modelo = self.retos[self.pregunta_actual]
        self.respuesta_correcta = respuesta.lower()
        self.ui.mostrar_mensaje(f"Tina: {texto}")
        marker_id = random.choice(range(1, 13))
        self.modelos_a_mostrar.append((categoria, modelo, marker_id))
        self.ui.mostrar_mensaje("(Responde...)")
        self.state.esperando_voz = True

    def _finalizar_juego(self):
        self.ui.mostrar_mensaje("🏅 ¡Has completado el desafío final!")
        self.ui.mostrar_mensaje(f"Has ganado {self.estrellas} estrellas 🌟")
        if hasattr(self.state, "gestor_juegos"):
            self.state.gestor_juegos.registrar_resultado("final", self.juego_en_curso, self.estrellas)
        self.state.fase = "mundo_final"

    def _detectar_categoria(self, item):
        if item in rutas_letras:
            return "letras"
        if item in rutas_animales:
            return "animales"
        if item in rutas_numeros:
            return "numeros"
        if item in rutas_frutas:
            return "frutas"
        if item in rutas_verduras:
            return "verduras"
        return None
