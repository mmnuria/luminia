import random
from models.modelos import rutas_frutas, rutas_verduras, obtener_ruta_por_categoria


class MundoFrutayverduraAR:
    """
    🍎🥕 Mundo de las Frutas y Verduras — descubre los sabores mágicos de Luminia.
    Incluye los minijuegos: adivina, color y clasifica.
    """

    def __init__(self, ui_renderer, voice_system, game_state):
        self.ui = ui_renderer
        self.voice = voice_system
        self.state = game_state
        self.modelos_a_mostrar = []  # lista de tuplas: (categoria, fruta_verdura, marker_id)

        # Base de datos ajustada para coincidir con los modelos
        self.alimentos = [
            {"nombre": "Apple", "tipo": "fruta", "color": "rojo"},
            {"nombre": "Banana", "tipo": "fruta", "color": "amarillo"},
            {"nombre": "Orange", "tipo": "fruta", "color": "naranja"},
            {"nombre": "Strawberry", "tipo": "fruta", "color": "rojo"},
            {"nombre": "Carrot", "tipo": "verdura", "color": "naranja"},
            {"nombre": "Cucumber", "tipo": "verdura", "color": "verde"},
            {"nombre": "Tomato", "tipo": "fruta", "color": "rojo"},
            {"nombre": "Spinach", "tipo": "verdura", "color": "verde"},
            {"nombre": "Grape", "tipo": "fruta", "color": "morado"},
        ]

        # Variables de sesión
        self.juego_actual = None
        self.ronda = 0
        self.aciertos = 0
        self.en_juego = False
        self.color_pedido = None
        self.alimento_actual = None
        self.opciones = []

    # ---------------------------------------------------
    # INICIO DEL MUNDO
    # ---------------------------------------------------
    def iniciar(self):
        self.ui.mostrar_mensaje("🍎🥕 Bienvenido al Mundo de las Frutas y Verduras.")
        self.ui.mostrar_mensaje("Aquí aprenderás a reconocer alimentos mágicos por su color, forma y tipo.")
        self.ui.mostrar_mensaje("Puedes decir: 'adivina', 'color' o 'clasifica' para comenzar un minijuego.")
        self.ui.mostrar_mensaje("O di 'salir' para regresar al menú principal.")
        self.state.fase = "mundo_fruta_y_verdura"

    # ---------------------------------------------------
    # INICIO DE MINIJUEGO
    # ---------------------------------------------------
    def iniciar_juego(self, tipo):
        tipo = tipo.lower()
        if tipo not in ["adivina", "color", "clasifica"]:
            self.ui.mostrar_mensaje("⚠️ No conozco ese minijuego. Prueba con 'adivina', 'color' o 'clasifica'.")
            return

        self.juego_actual = tipo
        self.ronda = 0
        self.aciertos = 0
        self.en_juego = True
        self.state.fase = "jugando"

        self.ui.mostrar_mensaje(f"🌟 Comenzamos el minijuego '{self.juego_actual.title()}' 🌟")
        if tipo == "adivina":
            self._siguiente_ronda_adivina()
        elif tipo == "color":
            self._siguiente_ronda_color()
        elif tipo == "clasifica":
            self._siguiente_ronda_tipo()

    # ---------------------------------------------------
    # PROCESAMIENTO DE COMANDO POR VOZ
    # ---------------------------------------------------
    def procesar_comando(self, comando):
        if not self.en_juego:
            self.ui.mostrar_mensaje("🎮 Di 'adivina', 'color' o 'clasifica' para iniciar un minijuego.")
            return

        comando = comando.lower().strip()
        traducciones = {
            "manzana": "Apple",
            "plátano": "Banana",
            "platano": "Banana",
            "naranja": "Orange",
            "fresa": "Strawberry",
            "zanahoria": "Carrot",
            "pepino": "Cucumber",
            "tomate": "Tomato",
            "espinaca": "Spinach",
            "uva": "Grape",
            "uvas": "Grape",
        }
        comando_traducido = traducciones.get(comando, comando)

        if self.juego_actual == "adivina":
            correcto = self.alimento_actual["nombre"]
            if comando_traducido == correcto:
                self.aciertos += 1
                self.ui.mostrar_mensaje(f"✅ ¡Correcto! Era una {comando} 🍎")
            else:
                self.ui.mostrar_mensaje(f"❌ No, era una {self._nombre_visible(correcto)}.")
            self._siguiente_ronda_adivina()

        elif self.juego_actual == "color":
            correctos = [a["nombre"] for a in self.opciones if a["color"] == self.color_pedido]
            if comando_traducido in correctos:
                self.aciertos += 1
                self.ui.mostrar_mensaje(f"✅ ¡Muy bien! Ese color es {self.color_pedido} 🌈")
            else:
                self.ui.mostrar_mensaje(f"❌ No es de color {self.color_pedido}.")
            self._siguiente_ronda_color()

        elif self.juego_actual == "clasifica":
            correcto = self.alimento_actual["tipo"]
            if comando == correcto:
                self.aciertos += 1
                self.ui.mostrar_mensaje(f"✅ ¡Exacto! Es una {correcto} 🥦")
            else:
                self.ui.mostrar_mensaje(f"❌ No, en realidad es una {correcto}.")
            self._siguiente_ronda_tipo()

    # ---------------------------------------------------
    # RONDAS
    # ---------------------------------------------------
    def _siguiente_ronda_adivina(self):
        self.ronda += 1
        if self.ronda > 3:
            self._finalizar_juego()
            return

        self.alimento_actual = random.choice(self.alimentos)
        categoria = "frutas" if self.alimento_actual["tipo"] == "fruta" else "verduras"
        marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

        self.modelos_a_mostrar.append(categoria, self.alimento_actual["nombre"], marker_id)
        self.ui.mostrar_mensaje(f"🍏 Ronda {self.ronda}: ¿Qué alimento es este?")
        self.state.esperando_voz = True

    def _siguiente_ronda_color(self):
        self.ronda += 1
        if self.ronda > 3:
            self._finalizar_juego()
            return

        colores = ["rojo", "verde", "naranja", "amarillo", "morado"]
        self.color_pedido = random.choice(colores)
        self.opciones = random.sample(self.alimentos, 4)

        for alimento in self.opciones:
            categoria = "frutas" if alimento["tipo"] == "fruta" else "verduras"
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
            self.modelos_a_mostrar.append(categoria, alimento["nombre"], marker_id)

        self.ui.mostrar_mensaje(f"🎨 ¿Qué alimentos son de color {self.color_pedido}?")
        self.state.esperando_voz = True

    def _siguiente_ronda_tipo(self):
        self.ronda += 1
        if self.ronda > 3:
            self._finalizar_juego()
            return

        self.alimento_actual = random.choice(self.alimentos)
        categoria = "frutas" if self.alimento_actual["tipo"] == "fruta" else "verduras"
        marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

        self.modelos_a_mostrar.append(categoria, self.alimento_actual["nombre"], marker_id)
        self.ui.mostrar_mensaje("🥦 ¿Es fruta o verdura?")
        self.state.esperando_voz = True

    # ---------------------------------------------------
    # FINALIZAR JUEGO
    # ---------------------------------------------------
    def _finalizar_juego(self):
        self.en_juego = False
        estrellas = min(round((self.aciertos / 3) * 3), 3)
        self.ui.mostrar_mensaje(f"🎉 ¡Juego terminado! Has conseguido {estrellas} estrellas ⭐ ({self.aciertos}/3 aciertos)")

        if hasattr(self.state, "gestor_juegos") and self.state.gestor_juegos:
            self.state.gestor_juegos.registrar_resultado("fruta_y_verdura", self.juego_actual, estrellas)

    # ---------------------------------------------------
    # UTILIDAD
    # ---------------------------------------------------
    def _nombre_visible(self, key):
        """
        Traduce los nombres internos al español para mostrar en mensajes.
        """
        nombres = {
            "Apple": "manzana",
            "Banana": "plátano",
            "Orange": "naranja",
            "Strawberry": "fresa",
            "Carrot": "zanahoria",
            "Cucumber": "pepino",
            "Tomato": "tomate",
            "Spinach": "espinaca",
            "Grape": "uva"
        }
        return nombres.get(key, key)
