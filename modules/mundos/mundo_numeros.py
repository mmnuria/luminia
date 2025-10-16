import random
import time
from models.modelos import rutas_numeros, obtener_ruta_por_categoria


class MundoNumerosAR:
    """
    🔢 Mundo de los Números — donde los números mágicos de Luminia cobran vida.
    Incluye los minijuegos: contar, suma y mayor.
    """

    def __init__(self, ui_renderer, voice_system, game_state):
        self.ui = ui_renderer
        self.voice = voice_system
        self.state = game_state
        self.modelos_a_mostrar = []  # lista de tuplas: (categoria, numero, marker_id)

        self.juegos = {
            "contar": self.juego_contar,
            "suma": self.juego_suma,
            "mayor": self.juego_mayor
        }

        self.estrellas = 0
        self.ronda_actual = 0
        self.total_rondas = 3
        self.juego_en_curso = None
        self.respuesta_correcta = None

    # ---------------------------------------------------
    # INICIO DEL MUNDO
    # ---------------------------------------------------
    def iniciar(self):
        self.ui.mostrar_mensaje("🔢 Bienvenido al Mundo de los Números.")
        self.ui.mostrar_mensaje("Aquí aprenderás jugando con los números mágicos de Luminia.")
        self.ui.mostrar_mensaje("Puedes decir: 'contar', 'suma' o 'mayor' para comenzar un minijuego.")
        self.ui.mostrar_mensaje("O di 'salir' para regresar al menú principal.")
        self.state.fase = "mundo_numeros"

    # ---------------------------------------------------
    # INICIO DE MINIJUEGO
    # ---------------------------------------------------
    def iniciar_juego(self, tipo):
        tipo = tipo.lower()
        if tipo not in self.juegos:
            self.ui.mostrar_mensaje("⚠️ No conozco ese minijuego. Prueba con 'contar', 'suma' o 'mayor'.")
            return

        self.estrellas = 0
        self.ronda_actual = 0
        self.juego_en_curso = tipo
        self.state.fase = "jugando"

        self.ui.mostrar_mensaje(f"🌟 Comienza el minijuego {tipo.upper()} 🌟")
        time.sleep(0.5)
        self.juegos[tipo]()

    # ---------------------------------------------------
    # PROCESAR RESPUESTA POR VOZ
    # ---------------------------------------------------
    def procesar_comando(self, comando):
        if not self.juego_en_curso:
            self.ui.mostrar_mensaje("🎮 Di 'contar', 'suma' o 'mayor' para iniciar un minijuego.")
            return

        comando = comando.strip().lower()

        traducciones = {
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
            "diez": "10"
        }
        comando_traducido = traducciones.get(comando, comando)

        # Validar respuesta
        if comando_traducido == self.respuesta_correcta:
            self.ui.mostrar_mensaje("✅ ¡Muy bien! Has acertado.")
            self.estrellas += 1
        else:
            self.ui.mostrar_mensaje(f"❌ No era '{comando}'. La respuesta correcta era '{self.respuesta_correcta}'.")

        # Avanzar ronda o terminar
        self.ronda_actual += 1
        if self.ronda_actual < self.total_rondas:
            self.ui.mostrar_mensaje(f"⭐ Vamos con la ronda {self.ronda_actual + 1}...")
            time.sleep(0.8)
            self.juegos[self.juego_en_curso]()
        else:
            self._finalizar_juego()

    # ---------------------------------------------------
    # MINIJUEGOS
    # ---------------------------------------------------

    def juego_contar(self):
        """
        Muestra una cantidad aleatoria de números y pide contarlos.
        """
        cantidad = random.randint(1, 4)
        self.respuesta_correcta = str(cantidad)
        objetos = random.sample(list(rutas_numeros.keys()), cantidad)

        self.ui.mostrar_mensaje(f"🔢 Aparecen {cantidad} números mágicos...")
        self.ui.mostrar_mensaje("Tina: '¿Cuántos números ves?'")

        for num in objetos:
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
            self.modelos_a_mostrar.append(("numeros", num, marker_id))

    def juego_suma(self):
        """
        Muestra dos números y pide decir su suma.
        """
        numeros = random.sample([str(i) for i in range(0, 10)], 2)
        num1, num2 = numeros
        self.respuesta_correcta = str(int(num1) + int(num2))

        self.ui.mostrar_mensaje(f"➕ Tina: '¿Cuánto es {num1} + {num2}?'")

        marker_id1 = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        marker_id2 = random.choice([m for m in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] if m != marker_id1])
        self.modelos_a_mostrar.append(("numeros", num1, marker_id1))
        self.modelos_a_mostrar.append(("numeros", num2, marker_id2))

    def juego_mayor(self):
        """
        Muestra tres números y pide identificar el más grande.
        """
        opciones = random.sample([str(i) for i in range(0, 10)], 3)
        self.respuesta_correcta = str(max(int(n) for n in opciones))

        self.ui.mostrar_mensaje(f"🔍 Aparecen los números: {', '.join(opciones)}")
        self.ui.mostrar_mensaje("Tina: '¿Cuál es el número mayor?'")

        for num in opciones:
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
            self.modelos_a_mostrar.append(("numeros", num, marker_id))

    # ---------------------------------------------------
    # FINALIZACIÓN
    # ---------------------------------------------------
    def _finalizar_juego(self):
        self.ui.mostrar_mensaje("🎉 ¡Has completado el minijuego!")
        self.ui.mostrar_mensaje(f"Ganaste {self.estrellas} estrellas 🌟")
        if hasattr(self.state, "gestor_juegos"):
            self.state.gestor_juegos.registrar_resultado("numeros", self.juego_en_curso, self.estrellas)
        self.state.fase = "mundo_numeros"
