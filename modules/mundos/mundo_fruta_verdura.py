import random
import time
import unicodedata
from models.modelos import obtener_ruta_por_categoria
from modules.ui_renderer import draw_text_with_background


class MundoFrutayverduraAR:
    """
    🍎🥕 Mundo de las Frutas y Verduras — descubre los sabores mágicos de Luminia.
    Incluye los minijuegos: adivina, color y clasifica.
    """

    def __init__(self, ui_renderer, voice_system, game_state):
        self.ui = ui_renderer
        self.voice = voice_system
        self.state = game_state
        self.modelos_a_mostrar = []  # lista de tuplas: (categoria, alimento, marker_id)

        # Base de datos de alimentos con modelos disponibles
        self.alimentos = [
            {"nombre": "Apple", "tipo": "fruta", "color": "rojo"},
            {"nombre": "Banana", "tipo": "fruta", "color": "amarillo"},
            {"nombre": "Blueberry", "tipo": "fruta", "color": "morado"},
            {"nombre": "Cherry", "tipo": "fruta", "color": "rojo"},
            {"nombre": "Grape", "tipo": "fruta", "color": "morado"},
            {"nombre": "Kiwi", "tipo": "fruta", "color": "verde"},
            {"nombre": "Lemon", "tipo": "fruta", "color": "amarillo"},
            {"nombre": "Mango", "tipo": "fruta", "color": "naranja"},
            {"nombre": "Melon", "tipo": "fruta", "color": "verde"},
            {"nombre": "Orange", "tipo": "fruta", "color": "naranja"},
            {"nombre": "Papaya", "tipo": "fruta", "color": "naranja"},
            {"nombre": "Pear", "tipo": "fruta", "color": "verde"},
            {"nombre": "Pineapple", "tipo": "fruta", "color": "amarillo"},
            {"nombre": "Strawberry", "tipo": "fruta", "color": "rojo"},
            {"nombre": "Watermelon", "tipo": "fruta", "color": "verde"},
            {"nombre": "Carrot", "tipo": "verdura", "color": "naranja"},
            {"nombre": "Broccoli", "tipo": "verdura", "color": "verde"},
            {"nombre": "Cauliflower", "tipo": "verdura", "color": "blanco"},
            {"nombre": "Cucumber", "tipo": "verdura", "color": "verde"},
            {"nombre": "Corn", "tipo": "verdura", "color": "amarillo"},
            {"nombre": "Green_Peas", "tipo": "verdura", "color": "verde"},
            {"nombre": "Green_Leek", "tipo": "verdura", "color": "verde"},
            {"nombre": "Mushroom", "tipo": "verdura", "color": "marron"},
            {"nombre": "Onion", "tipo": "verdura", "color": "blanco"},
            {"nombre": "Pumpkin", "tipo": "verdura", "color": "naranja"},
            {"nombre": "Spinach", "tipo": "verdura", "color": "verde"},
            {"nombre": "Vegetable", "tipo": "verdura", "color": "verde"}
        ]

        # Minijuegos
        self.juegos = {
            "adivina": self.juego_adivina,
            "color": self.juego_color,
            "clasifica": self.juego_clasifica
        }

        # Variables de sesión
        self.estrellas = 0
        self.ronda_actual = 0
        self.total_rondas = 3
        self.juego_en_curso = None
        self.respuesta_correcta = None
        self.alimento_actual = None
        self.opciones = []
        self.color_pedido = None

    # ---------------------------------------------------
    # MÉTODO AUXILIAR: mostrar mensaje
    # ---------------------------------------------------
    def mostrar_mensaje(self, texto, pos=(50, 60), color=(255, 255, 255),
                         bg_color=(56, 118, 29), font_scale=0.7):
        if hasattr(self.state, "frame_actual") and self.state.frame_actual is not None:
            draw_text_with_background(self.state.frame_actual, texto, pos, font_scale, color, bg_color)
        else:
            print(f"[MundoFrutayverduraAR] {texto}")

    # ---------------------------------------------------
    # MÉTODO AUXILIAR: normalizar texto (tildes y espacios)
    # ---------------------------------------------------
    def normalizar(self, texto):
        texto = texto.upper()
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                        if unicodedata.category(c) != 'Mn')
        return texto.replace(" ", "")

    # ---------------------------------------------------
    # INICIO DEL MUNDO
    # ---------------------------------------------------
    def iniciar(self):
        print("🍎🥕 Bienvenido al Mundo de las Frutas y Verduras.")
        print("Aprenderás a reconocer alimentos mágicos por su color, forma y tipo.")
        print("Di: 'adivina', 'color' o 'clasifica' para comenzar un minijuego.")
        print("O di 'salir' para regresar al menú principal.")
        self.state.fase = "mundo_fruta_y_verdura"

    # ---------------------------------------------------
    # INICIO DE MINIJUEGO
    # ---------------------------------------------------
    def iniciar_juego(self, tipo):
        tipo = tipo.lower()
        if tipo not in self.juegos:
            print("⚠️ No conozco ese minijuego. Prueba con 'adivina', 'color' o 'clasifica'.")
            return

        # Reiniciar variables de juego
        self.estrellas = 0
        self.ronda_actual = 0
        self.juego_en_curso = tipo
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
    #         print("🎮 Di 'adivina', 'color' o 'clasifica' para iniciar un minijuego.")
    #         return

    #     comando_norm = self.normalizar(comando)
    #     traducciones = {
    #         "manzana": "Apple",
    #         "platano": "Banana",
    #         "plátano": "Banana",
    #         "arándano": "Blueberry",
    #         "fresa": "Strawberry",
    #         "cereza": "Cherry",
    #         "uva": "Grape",
    #         "kiwi": "Kiwi",
    #         "limon": "Lemon",
    #         "mango": "Mango",
    #         "melon": "Melon",
    #         "naranja": "Orange",
    #         "papaya": "Papaya",
    #         "pera": "Pear",
    #         "piña": "Pineapple",
    #         "sandia": "Watermelon",
    #         "zanahoria": "Carrot",
    #         "brocoli": "Broccoli",
    #         "coliflor": "Cauliflower",
    #         "pepino": "Cucumber",
    #         "maiz": "Corn",
    #         "guisantes": "Green_Peas",
    #         "puerro": "Green_Leek",
    #         "champinon": "Mushroom",
    #         "cebolla": "Onion",
    #         "calabaza": "Pumpkin",
    #         "espinaca": "Spinach",
    #         "verdura": "Vegetable"
    #     }
    #     comando_trad = traducciones.get(comando_norm.lower(), comando_norm)

    #     # Evaluar respuesta
    #     if self.juego_en_curso == "adivina":
    #         correcto = self.alimento_actual["nombre"]
    #         if comando_trad == correcto:
    #             print(f"✅ ¡Correcto! Era {self._nombre_visible(correcto)} 🍎")
    #             self.estrellas += 1
    #         else:
    #             print(f"❌ No, era {self._nombre_visible(correcto)}.")

    #     elif self.juego_en_curso == "color":
    #         correctos = [a["nombre"] for a in self.opciones if a["color"] == self.color_pedido]
    #         if comando_trad in correctos:
    #             print(f"✅ ¡Muy bien! Ese color es {self.color_pedido} 🌈")
    #             self.estrellas += 1
    #         else:
    #             print(f"❌ No es de color {self.color_pedido}.")

    #     elif self.juego_en_curso == "clasifica":
    #         correcto = self.alimento_actual["tipo"]
    #         if comando_norm == correcto.upper():
    #             print(f"✅ ¡Exacto! Es una {correcto} 🥦")
    #             self.estrellas += 1
    #         else:
    #             print(f"❌ No, en realidad es una {correcto}.")

    #     # Avanzar ronda
    #     self.ronda_actual += 1
    #     if self.ronda_actual < self.total_rondas:
    #         time.sleep(0.8)
    #         self.juegos[self.juego_en_curso]()
    #     else:
    #         print(f"🎉 ¡Has completado el minijuego! Ganaste {self.estrellas} estrellas 🌟")
    #         # Registrar resultado
    #         if hasattr(self.state, "gestor_juegos"):
    #             self.state.gestor_juegos.registrar_resultado("fruta_y_verdura", self.juego_en_curso, self.estrellas)


    # ---------------------------------------------------
    # PROCESAR COMANDO POR VOZ
    # ---------------------------------------------------
    def procesar_comando(self, comando):
        if not self.juego_en_curso:
            print("🎮 Di 'adivina', 'color' o 'clasifica' para iniciar un minijuego.")
            return

        comando_modelo = self._traducir_a_modelo(comando)
        comando_norm = self.normalizar(comando)

        # Evaluar respuesta según minijuego
        if self.juego_en_curso == "adivina":
            correcto = self.alimento_actual["nombre"]
            if comando_modelo == correcto:
                print(f"✅ ¡Correcto! Era {self._nombre_visible(correcto)} 🍎")
                self.estrellas += 1
            else:
                print(f"❌ No, era {self._nombre_visible(correcto)}.")

        elif self.juego_en_curso == "color":
            correctos = [a["nombre"] for a in self.opciones if a["color"] == self.color_pedido]
            if comando_modelo in correctos:
                print(f"✅ ¡Muy bien! Ese color es {self.color_pedido} 🌈")
                self.estrellas += 1
            else:
                print(f"❌ No es de color {self.color_pedido}.")

        elif self.juego_en_curso == "clasifica":
            correcto = self.alimento_actual["tipo"]
            if comando_norm in ["FRUTA", "FRUTAS"] and correcto == "fruta":
                print("✅ ¡Exacto! Es una fruta 🍉")
                self.estrellas += 1
            elif comando_norm in ["VERDURA", "VERDURAS"] and correcto == "verdura":
                print("✅ ¡Exacto! Es una verdura 🥦")
                self.estrellas += 1
            else:
                print(f"❌ No, en realidad es una {correcto}.")

        # Avanzar ronda
        self.ronda_actual += 1
        if self.ronda_actual < self.total_rondas:
            time.sleep(0.8)
            self.juegos[self.juego_en_curso]()
        else:
            print(f"🎉 ¡Has completado el minijuego! Ganaste {self.estrellas} estrellas 🌟")
            if hasattr(self.state, "gestor_juegos"):
                self.state.gestor_juegos.registrar_resultado("frutas_verduras", self.juego_en_curso, self.estrellas)


    # ---------------------------------------------------
    # TRADUCTOR DE COMANDOS EN ESPAÑOL → MODELOS
    # ---------------------------------------------------
    def _traducir_a_modelo(self, texto_usuario):
        texto = self.normalizar(texto_usuario)

        traducciones = {
            "MANZANA": "Apple",
            "PLATANO": "Banana", "PLATANOS": "Banana", "BANANA": "Banana",
            "ARANDANO": "Blueberry", "ARANDANOS": "Blueberry",
            "CEREZA": "Cherry", "CEREZAS": "Cherry",
            "UVA": "Grape", "UVAS": "Grape",
            "KIWI": "Kiwi",
            "LIMON": "Lemon", "LIMONES": "Lemon",
            "MANGO": "Mango",
            "MELON": "Melon", "MELONES": "Melon",
            "NARANJA": "Orange", "NARANJAS": "Orange",
            "PAPAYA": "Papaya",
            "PERA": "Pear", "PERAS": "Pear",
            "PINA": "Pineapple", "PINIA": "Pineapple",
            "FRESA": "Strawberry", "FRESAS": "Strawberry",
            "SANDIA": "Watermelon", "SANDIAS": "Watermelon",
            "ZANAHORIA": "Carrot", "ZANAHORIAS": "Carrot",
            "BROCOLI": "Broccoli",
            "COLIFLOR": "Cauliflower",
            "PEPINO": "Cucumber", "PEPINOS": "Cucumber",
            "MAIZ": "Corn", "ELOTE": "Corn",
            "GUISANTE": "Green_Peas", "GUISANTES": "Green_Peas",
            "PUERRO": "Green_Leek", "PUERROS": "Green_Leek",
            "CHAMPINON": "Mushroom", "CHAMPIÑON": "Mushroom",
            "CEBOLLA": "Onion", "CEBOLLAS": "Onion",
            "CALABAZA": "Pumpkin", "CALABAZAS": "Pumpkin",
            "ESPINACA": "Spinach", "ESPINACAS": "Spinach",
            "VERDURA": "Vegetable", "VERDURAS": "Vegetable"
        }

        return traducciones.get(texto, texto)


    # ---------------------------------------------------
    # MINIJUEGOS
    # ---------------------------------------------------
    def juego_adivina(self):
        self.alimento_actual = random.choice(self.alimentos)
        self.respuesta_correcta = self.alimento_actual["nombre"]
        self.modelos_a_mostrar.clear()
        marker_id = random.choice(range(1, 13))
        categoria = "frutas" if self.alimento_actual["tipo"] == "fruta" else "verduras"
        self.modelos_a_mostrar.append((categoria, self.alimento_actual["nombre"], marker_id))

        print(f"🍏 Ronda {self.ronda_actual + 1}: ¿Qué alimento es este?")
        self.state.esperando_voz = True

    def juego_color(self):
        self.color_pedido = random.choice(["rojo", "verde", "naranja", "amarillo", "morado", "blanco", "marron"])
        self.opciones = random.sample(self.alimentos, 4)
        self.modelos_a_mostrar.clear()

        for alimento in self.opciones:
            marker_id = random.choice(range(1, 13))
            categoria = "frutas" if alimento["tipo"] == "fruta" else "verduras"
            self.modelos_a_mostrar.append((categoria, alimento["nombre"], marker_id))

        print(f"🎨 ¿Qué alimentos son de color {self.color_pedido}?")
        self.state.esperando_voz = True

    def juego_clasifica(self):
        self.alimento_actual = random.choice(self.alimentos)
        self.respuesta_correcta = self.alimento_actual["tipo"]
        self.modelos_a_mostrar.clear()
        marker_id = random.choice(range(1, 13))
        categoria = "frutas" if self.alimento_actual["tipo"] == "fruta" else "verduras"
        self.modelos_a_mostrar.append((categoria, self.alimento_actual["nombre"], marker_id))

        print("🥦 ¿Es fruta o verdura?")
        self.state.esperando_voz = True

    # ---------------------------------------------------
    # UTILIDAD
    # ---------------------------------------------------
    def _nombre_visible(self, key):
        nombres = {
            "Apple": "manzana",
            "Banana": "plátano",
            "Blueberry": "arándano",
            "Cherry": "cereza",
            "Grape": "uva",
            "Kiwi": "kiwi",
            "Lemon": "limón",
            "Mango": "mango",
            "Melon": "melón",
            "Orange": "naranja",
            "Papaya": "papaya",
            "Pear": "pera",
            "Pineapple": "piña",
            "Strawberry": "fresa",
            "Watermelon": "sandía",
            "Carrot": "zanahoria",
            "Broccoli": "brócoli",
            "Cauliflower": "coliflor",
            "Cucumber": "pepino",
            "Corn": "maíz",
            "Green_Peas": "guisantes",
            "Green_Leek": "puerro",
            "Mushroom": "champiñón",
            "Onion": "cebolla",
            "Pumpkin": "calabaza",
            "Spinach": "espinaca",
            "Vegetable": "verdura"
        }
        return nombres.get(key, key)
