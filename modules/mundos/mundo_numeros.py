import random
import time
import unicodedata
from models.modelos import rutas_numeros, obtener_ruta_por_categoria
from modules.ui_renderer import draw_text_with_background


class MundoNumerosAR:
    """
    🔢 Mundo de los Números — los números mágicos de Luminia cobran vida.
    Incluye los minijuegos: adivina, suma y mayor.
    """

    def __init__(self, ui_renderer, voice_system, game_state):
        self.ui = ui_renderer
        self.voice = voice_system
        self.state = game_state
        self.modelos_a_mostrar = []  # lista de tuplas: (categoria, numero, marker_id)

        self.juegos = {
            "adivina": self.juego_adivina,
            "suma": self.juego_suma,
            "mayor": self.juego_mayor
        }

        # Variables de sesión
        self.estrellas = 0
        self.ronda_actual = 0
        self.total_rondas = 3
        self.juego_en_curso = None
        self.respuesta_correcta = None
        self.numeros_usados = []  # Para evitar repetir números en el minijuego

    # ---------------------------------------------------
    # MÉTODOS AUXILIARES
    # ---------------------------------------------------
    def mostrar_mensaje(self, texto, pos=(50, 60), color=(255, 255, 255),
                         bg_color=(56, 118, 29), font_scale=0.7):
        if hasattr(self.state, "frame_actual") and self.state.frame_actual is not None:
            draw_text_with_background(self.state.frame_actual, texto, pos, font_scale, color, bg_color)
        else:
            print(f"[MundoNumerosAR] {texto}")

    def normalizar(self, texto):
        texto = texto.upper()
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                        if unicodedata.category(c) != 'Mn')
        return texto.replace(" ", "")

    # ---------------------------------------------------
    # INICIO DEL MUNDO
    # ---------------------------------------------------
    def iniciar(self):
        print("🔢 Bienvenido al Mundo de los Números.")
        print("Aprenderás jugando con números mágicos.")
        print("Di: 'adivina', 'suma' o 'mayor' para comenzar un minijuego.")
        print("O di 'salir' para regresar al menú principal.")
        self.state.fase = "mundo_numeros"

    # ---------------------------------------------------
    # INICIO DE MINIJUEGO
    # ---------------------------------------------------
    def iniciar_juego(self, tipo):
        tipo = tipo.lower()
        if tipo not in self.juegos:
            print("⚠️ No conozco ese minijuego. Prueba con 'adivina', 'suma' o 'mayor'.")
            return

        self.estrellas = 0
        self.ronda_actual = 0
        self.juego_en_curso = tipo
        self.numeros_usados.clear()
        self.state.fase = "jugando"
        self.modelos_a_mostrar.clear()

        print(f"🌟 ¡Comienza el minijuego {tipo.upper()}! 🌟")
        time.sleep(0.5)
        self.juegos[tipo]()

    # ---------------------------------------------------
    # PROCESAR COMANDO POR VOZ
    # ---------------------------------------------------
    # def procesar_comando(self, comando):
    #     if not self.juego_en_curso:
    #         print("🎮 Di 'adivina', 'suma' o 'mayor' para iniciar un minijuego.")
    #         return

    #     comando_norm = self.normalizar(comando)
    #     traducciones = {
    #         "cero": "0",
    #         "uno": "1",
    #         "dos": "2",
    #         "tres": "3",
    #         "cuatro": "4",
    #         "cinco": "5",
    #         "seis": "6",
    #         "siete": "7",
    #         "ocho": "8",
    #         "nueve": "9",
    #         "diez": "10"
    #     }
    #     comando_trad = traducciones.get(comando_norm.lower(), comando_norm)

    #     if comando_trad == self.respuesta_correcta:
    #         print("✅ ¡Muy bien! Has acertado.")
    #         self.estrellas += 1
    #     else:
    #         print(f"❌ No era '{comando}'. La respuesta correcta era '{self.respuesta_correcta}'.")

    #     # Avanzar ronda
    #     self.ronda_actual += 1
    #     if self.ronda_actual < self.total_rondas:
    #         print(f"⭐ Vamos con la ronda {self.ronda_actual + 1}...")
    #         time.sleep(0.8)
    #         self.juegos[self.juego_en_curso]()
    #     else:
    #         self._finalizar_juego()

    def procesar_comando(self, comando):
        """
        Procesa los comandos hablados en los minijuegos del mundo de números.
        Solo acepta comandos que empiecen con 'NUMERO'.
        """
        if not self.juego_en_curso:
            print("🎮 Di 'adivina', 'suma' o 'mayor' para iniciar un minijuego.")
            return

        # Normalizar
        comando = self.normalizar(comando)
        print(f"[MundoNumerosAR] Comando recibido: {comando}")

        # Comprobar que empieza con "NUMERO "
        if not comando.startswith("NUMERO "):
            print(f"⚠️ Debes decir el número empezando con 'número'.")
            return

        # Quitar el prefijo "NUMERO "
        comando_real = comando[7:].strip()

        # Separar caracteres para comparar
        comando_chars = list(comando_real.replace(" ", ""))
        respuesta_chars = list(self.respuesta_correcta.replace(" ", ""))

        # Comparar
        if comando_chars == respuesta_chars:
            print("✅ ¡Muy bien! Has acertado.")
            self.estrellas += 1
        else:
            print(f"❌ No era '{comando_real}'. La respuesta correcta era '{self.respuesta_correcta}'.")

        # Avanzar ronda
        self.ronda_actual += 1
        if self.ronda_actual < self.total_rondas:
            print(f"⭐ Vamos con la ronda {self.ronda_actual + 1}...")
            time.sleep(0.8)
            self.juegos[self.juego_en_curso]()
        else:
            self.modelos_a_mostrar = []
            # Termina minijuego
            print("🎉 ¡Has completado el minijuego!")
            print(f"Ganaste {self.estrellas} estrellas 🌟")

            # Registrar resultados
            if hasattr(self.state, "gestor_juegos"):
                self.state.gestor_juegos.registrar_resultado("numeros", self.juego_en_curso, self.estrellas)
            else:
                print("⚠️ No se pudo registrar el progreso (gestor no disponible).")

    # ---------------------------------------------------
    # MINIJUEGOS
    # ---------------------------------------------------
    def juego_adivina(self):
        """
        🎯 Minijuego de Adivinar Números
        - Ronda 1: 0-9
        - Ronda 2: 10-30
        - Ronda 3: 31-100
        """

        # Determinar el rango según la ronda
        if self.ronda_actual == 0:
            rango = (0, 9)
        elif self.ronda_actual == 1:
            rango = (10, 30)
        else:
            rango = (31, 100)

        # Elegir un número aleatorio dentro del rango, evitando repeticiones
        while True:
            numero = random.randint(rango[0], rango[1])
            if numero not in self.numeros_usados:
                self.numeros_usados.append(numero)
                break

        self.respuesta_correcta = str(numero)
        self.modelos_a_mostrar.clear()

        # Mostrar el número en un solo marcador
        marker_id = self.ronda_actual + 1  # marcadores consecutivos 1, 2, 3
        self.modelos_a_mostrar.append(("numeros", str(numero), marker_id))

        print(f"🔢 Mira el número mágico en el marcador {marker_id}...")
        print("Tina: '¿Qué número ves?'")


    def juego_suma(self):
        disponibles = [str(i) for i in range(0, 10) if str(i) not in self.numeros_usados]
        if len(disponibles) < 2:
            disponibles = [str(i) for i in range(0, 10)]
        num1, num2 = random.sample(disponibles, 2)
        self.numeros_usados.extend([num1, num2])
        self.respuesta_correcta = str(int(num1) + int(num2))
        self.modelos_a_mostrar.clear()

        print(f"➕ Tina: '¿Cuánto es {num1} + {num2}?'")
        self.modelos_a_mostrar.append(("numeros", num1, random.choice(range(1, 13))))
        self.modelos_a_mostrar.append(("numeros", num2, random.choice(range(1, 13))))

    def juego_mayor(self):
        disponibles = [str(i) for i in range(0, 10) if str(i) not in self.numeros_usados]
        if len(disponibles) < 3:
            disponibles = [str(i) for i in range(0, 10)]
        opciones = random.sample(disponibles, 3)
        self.numeros_usados.extend(opciones)
        self.respuesta_correcta = str(max(int(n) for n in opciones))
        self.modelos_a_mostrar.clear()

        print(f"🔍 Aparecen los números: {', '.join(opciones)}")
        print("Tina: '¿Cuál es el número mayor?'")

        for num in opciones:
            marker_id = random.choice(range(1, 13))
            self.modelos_a_mostrar.append(("numeros", num, marker_id))

    # ---------------------------------------------------
    # FINALIZACIÓN
    # ---------------------------------------------------
    def _finalizar_juego(self):
        print(f"🎉 ¡Has completado el minijuego! Ganaste {self.estrellas} estrellas 🌟")
        if hasattr(self.state, "gestor_juegos"):
            self.state.gestor_juegos.registrar_resultado("numeros", self.juego_en_curso, self.estrellas)
        self.state.fase = "mundo_numeros"
