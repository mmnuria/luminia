import random
import time
import unicodedata
from models.modelos import rutas_numeros, obtener_ruta_por_categoria
from modules.ui_renderer import draw_text_with_background


class MundoNumerosAR:
    """
    Mundo de los Números.
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
    # MÉTODO AUXILIAR
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
    
    def procesar_comando(self, comando):
        if not self.juego_en_curso:
            print("🎮 Di 'adivina', 'suma' o 'mayor' para iniciar un minijuego.")
            return

        comando = self.normalizar(comando)
        print(f"[MundoNumerosAR] Comando recibido: {comando}")

        if not comando.startswith("NUMERO"):
            print(f"⚠️ Debes decir el número empezando con 'número'.")
            return

        comando_real = comando[6:].strip()
        if comando_real.startswith(" "):
            comando_real = comando_real[1:]

        # ------------------------------
        # Traducción dinámica de texto a número
        # ------------------------------
        def texto_a_numero(texto):
            unidades = {
                "CERO": 0, "UNO": 1, "DOS": 2, "TRES": 3, "CUATRO": 4, "CINCO": 5,
                "SEIS": 6, "SIETE": 7, "OCHO": 8, "NUEVE": 9
            }
            especiales = {
                "DIEZ": 10, "ONCE": 11, "DOCE": 12, "TRECE": 13, "CATORCE": 14,
                "QUINCE": 15, "DIECISEIS": 16, "DIECISIETE": 17, "DIECIOCHO": 18,
                "DIECINUEVE": 19
            }
            decenas = {
                "VEINTE": 20, "TREINTA": 30, "CUARENTA": 40, "CINCUENTA": 50,
                "SESENTA": 60, "SETENTA": 70, "OCHENTA": 80, "NOVENTA": 90
            }

            # Si ya es un número (ej. "42"), lo devolvemos directo
            if texto.isdigit():
                return texto

            # Si está en las listas directas
            if texto in unidades:
                return str(unidades[texto])
            if texto in especiales:
                return str(especiales[texto])
            if texto in decenas:
                return str(decenas[texto])

            # Manejar combinaciones tipo "TREINTAYDOS" o "CUARENTAYOCHO"
            for nombre_decena, valor_decena in decenas.items():
                if texto.startswith(nombre_decena + "Y"):
                    resto = texto.replace(nombre_decena + "Y", "")
                    if resto in unidades:
                        return str(valor_decena + unidades[resto])
            
            # Si no se reconoció, lo devolvemos tal cual (para depuración)
            return texto

        comando_traducido = texto_a_numero(comando_real)

        # ------------------------------
        # Comparar
        # ------------------------------
        comando_chars = list(str(comando_traducido).replace(" ", ""))
        respuesta_chars = list(str(self.respuesta_correcta).replace(" ", ""))

        if comando_chars == respuesta_chars:
            print("✅ ¡Muy bien! Has acertado.")
            self.estrellas += 1
            if hasattr(self.state, "gestor_juegos"):
                self.state.gestor_juegos.mostrar_mensaje_pantalla("RESPUESTA CORRECTA!")
                time.sleep(4)
        else:
            print(f"❌ No era '{comando_real}'. La respuesta correcta era '{self.respuesta_correcta}'.")
            if hasattr(self.state, "gestor_juegos"):
                self.state.gestor_juegos.mostrar_mensaje_pantalla("RESPUESTA INCORRECTA!")
                time.sleep(2)        
        # ------------------------------
        # Avanzar ronda
        # ------------------------------
        self.ronda_actual += 1
        if self.ronda_actual < self.total_rondas:
            print(f"⭐ Vamos con la ronda {self.ronda_actual + 1}...")
            time.sleep(0.8)
            self.juegos[self.juego_en_curso]()
        else:
            self.modelos_a_mostrar = []
            print("🎉 ¡Has completado el minijuego!")
            print(f"Ganaste {self.estrellas} estrellas 🌟")

            if hasattr(self.state, "gestor_juegos"):
                self.state.gestor_juegos.registrar_resultado("numeros", self.juego_en_curso, self.estrellas)
                self.state.gestor_juegos.mostrar_mensaje_pantalla(
                    f" Has ganado {self.estrellas} estrellas y {self.estrellas} lumios",
                    duracion=4
                )
                time.sleep(4)
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
        self.modelos_a_mostrar = []

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
        time.sleep(1.5)

        # ----------------------------
        # Manejar números con más de un dígito
        # ----------------------------
        numero_str = str(numero)
        marker_base = self.ronda_actual * 2 + 1  # ej: ronda 0→1, ronda 1→3, ronda 2→5

        if len(numero_str) == 1:
            # Número de un solo dígito → un marcador
            self.modelos_a_mostrar.append(("numeros", numero_str, marker_base))
            time.sleep(2.5)
        else:
            # Número de dos dígitos → usar dos marcadores consecutivos
            for i, digito in enumerate(numero_str):
                marker_id = marker_base + i
                self.modelos_a_mostrar.append(("numeros", digito, marker_id))
            time.sleep(2.5)

        # ----------------------------
        # Mostrar mensaje
        # ----------------------------
        print(f"🔢 Mira el número mágico en el marcador {marker_base}..."
            f"{' y ' + str(marker_base + 1) if len(numero_str) > 1 else ''}")
        print("Tina: '¿Qué número ves?'")


    def juego_suma(self):
        self.modelos_a_mostrar = []
        disponibles = [str(i) for i in range(0, 10) if str(i) not in self.numeros_usados]
        if len(disponibles) < 2:
            disponibles = [str(i) for i in range(0, 10)]
        num1, num2 = random.sample(disponibles, 2)
        self.numeros_usados.extend([num1, num2])
        self.respuesta_correcta = str(int(num1) + int(num2))
        time.sleep(1.5)

        print(f"➕ Tina: '¿Cuánto es {num1} + {num2}?'")
        self.modelos_a_mostrar.append(("numeros", num1, random.choice(range(1, 13))))
        self.modelos_a_mostrar.append(("numeros", num2, random.choice(range(1, 13))))
        time.sleep(2.5)

    def juego_mayor(self):
        self.modelos_a_mostrar = []
        disponibles = [str(i) for i in range(0, 10) if str(i) not in self.numeros_usados]
        if len(disponibles) < 3:
            disponibles = [str(i) for i in range(0, 10)]
        opciones = random.sample(disponibles, 3)
        self.numeros_usados.extend(opciones)
        self.respuesta_correcta = str(max(int(n) for n in opciones))
        time.sleep(1.5)

        print(f"🔍 Aparecen los números: {', '.join(opciones)}")
        print("Tina: '¿Cuál es el número mayor?'")

        for num in opciones:
            marker_id = random.choice(range(1, 13))
            self.modelos_a_mostrar.append(("numeros", num, marker_id))

    # ---------------------------------------------------
    # FINALIZACIÓN
    # ---------------------------------------------------
    def _finalizar_juego(self):
        self.modelos_a_mostrar = []
        print(f"🎉 ¡Has completado el minijuego! Ganaste {self.estrellas} estrellas 🌟")
        if hasattr(self.state, "gestor_juegos"):
            self.state.gestor_juegos.registrar_resultado("numeros", self.juego_en_curso, self.estrellas)
            self.state.gestor_juegos.mostrar_mensaje_pantalla(
                    f" Has ganado {self.estrellas} estrellas y {self.estrellas} lumios",
                    duracion=4
                )
        self.state.fase = "menu_principal"
