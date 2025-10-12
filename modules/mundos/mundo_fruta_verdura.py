import random
from models.modelosNuevo import rutas_frutas, rutas_verduras, obtener_ruta_por_categoria

class MundoFrutayverduraAR:
    def __init__(self, ui_renderer, voice_system, game_state):
        self.ui = ui_renderer
        self.voice = voice_system
        self.state = game_state

        # Base de datos ajustada para coincidir con rutas_frutas y rutas_verduras
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

        self.juego_actual = None
        self.ronda = 0
        self.aciertos = 0
        self.en_juego = False

    def iniciar(self):
        self.ui.mostrar_mensaje("🍎🥕 Bienvenido al Mundo de las Frutas y Verduras.")
        self.ui.mostrar_mensaje("Puedes jugar a: 'adivina', 'color' o 'clasifica'.")
        self.ui.mostrar_mensaje("Di el nombre del minijuego para empezar.")
        # Castillo en marcador 4 manejado por ui_renderer

    def iniciar_juego(self, tipo):
        self.juego_actual = tipo.lower()
        if self.juego_actual not in ["adivina", "color", "clasifica"]:
            self.ui.mostrar_mensaje("⚠️ No conozco ese minijuego. Prueba con 'adivina', 'color' o 'clasifica'.")
            return

        self.ronda = 0
        self.aciertos = 0
        self.en_juego = True

        self.ui.mostrar_mensaje(f"🌟 Comenzamos con '{self.juego_actual.title()}' 🌟")
        if self.juego_actual == "adivina":
            self._siguiente_ronda_adivina()
        elif self.juego_actual == "color":
            self._siguiente_ronda_color()
        elif self.juego_actual == "clasifica":
            self._siguiente_ronda_tipo()

    def procesar_comando(self, comando):
        if not self.en_juego:
            self.ui.mostrar_mensaje("No hay un juego activo. Di 'adivina', 'color' o 'clasifica' para jugar.")
            return

        comando = comando.lower().strip()

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
            "uvas": "Grape"
        }
        comando_traducido = traducciones.get(comando, comando)

        if self.juego_actual == "adivina":
            correcto = self.alimento_actual["nombre"]
            if comando_traducido == correcto:
                self.aciertos += 1
                self.ui.mostrar_mensaje(f"✅ ¡Correcto! Es una {comando} 🍎")
            else:
                self.ui.mostrar_mensaje(f"❌ No, era una {correcto}.")
            self._siguiente_ronda_adivina()

        elif self.juego_actual == "color":
            correctos = [a["nombre"] for a in self.opciones if a["color"] == self.color_pedido]
            if comando_traducido in correctos:
                self.aciertos += 1
                self.ui.mostrar_mensaje("✅ ¡Muy bien! Ese color es correcto 🌈")
            else:
                self.ui.mostrar_mensaje("❌ No es de ese color.")
            self._siguiente_ronda_color()

        elif self.juego_actual == "clasifica":
            correcto = self.alimento_actual["tipo"]
            if comando == correcto:
                self.aciertos += 1
                self.ui.mostrar_mensaje(f"✅ ¡Exacto! Es una {correcto} 🥦")
            else:
                self.ui.mostrar_mensaje(f"❌ No, en realidad es una {correcto}.")
            self._siguiente_ronda_tipo()

    def _siguiente_ronda_adivina(self):
        self.ronda += 1
        if self.ronda > 3:
            self._finalizar_juego()
            return

        self.alimento_actual = random.choice(self.alimentos)
        categoria = "frutas" if self.alimento_actual["tipo"] == "fruta" else "verduras"
        marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])  # Todos menos 0
        self.ui.mostrar_modelo(categoria, self.alimento_actual["nombre"], marker_id)
        self.ui.mostrar_mensaje(f"Ronda {self.ronda}: ¿Qué es esto?")
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
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])  # Todos menos 0
            self.ui.mostrar_modelo(categoria, alimento["nombre"], marker_id)
        self.ui.mostrar_mensaje(f"¿Qué alimentos son de color {self.color_pedido}?")
        self.state.esperando_voz = True

    def _siguiente_ronda_tipo(self):
        self.ronda += 1
        if self.ronda > 3:
            self._finalizar_juego()
            return

        self.alimento_actual = random.choice(self.alimentos)
        categoria = "frutas" if self.alimento_actual["tipo"] == "fruta" else "verduras"
        marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])  # Todos menos 0
        self.ui.mostrar_modelo(categoria, self.alimento_actual["nombre"], marker_id)
        self.ui.mostrar_mensaje("¿Es fruta o verdura?")
        self.state.esperando_voz = True

    def _finalizar_juego(self):
        self.en_juego = False
        nota = (self.aciertos / 3) * 3
        estrellas = round(nota)
        if estrellas > 3:
            estrellas = 3
        self.ui.mostrar_mensaje(f"Has conseguido {estrellas} estrellas ⭐ ({self.aciertos}/3 aciertos)")
        if self.state.gestor_juegos:
            self.state.gestor_juegos.registrar_resultado("fruta_y_verdura", self.juego_actual, estrellas)