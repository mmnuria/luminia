import random
import time
from models.modelos import obtener_ruta_por_categoria, rutas_letras
from modules.ui_renderer import draw_text_with_background
import unicodedata

class MundoLetrasAR:
    """
    Mundo de las Letras.
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
        self.palabras = ["GATO", "LUNA", "MESA", "ROSA", "SOL", "CASA",
                        "PERRO", "NUBE", "ARCO", "FLOR", "CIELO", "SILLA",
                        "LIBRO", "ESTRELLA", "AVION", "FRUTA", "ZAPATO", "PEZ",
                        "CAMION", "ARBOL", "VENTANA", "ESPEJO", "CAMA", "BALON",
                        "MANO", "OJO", "CORAZON", "CONEJO", "LEON", "TORO"]

    # ---------------------------------------------------
    # MÉTODO AUXILIAR: normalizar texto (quitando tildes, mayúsculas y espacios)
    # ---------------------------------------------------
    def normalizar(self, texto):
        texto = texto.upper()
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto) 
                        if unicodedata.category(c) != 'Mn')  # quita tildes
        return texto.replace(" ", "")

    # ---------------------------------------------------
    # FASE DE INICIO DEL MUNDO
    # ---------------------------------------------------
    def iniciar(self):
        """
        Inicia el mundo, muestra introducción y opciones.
        """
        print("📖 Bienvenido al 🌈 Mundo de las Letras 🌈")
        print("Aquí aprenderás jugando con las letras mágicas del alfabeto.")
        print("Puedes decir: 'adivina', 'memoria' o 'secuencia' para comenzar un minijuego.")
        print("O di 'salir' para regresar al menú principal.")
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
            print("⚠️ No conozco ese minijuego. Prueba con 'adivina', 'memoria' o 'secuencia'.")
            return

        self.estrellas = 0
        self.ronda_actual = 0
        self.juego_en_curso = tipo
        self.state.fase = "jugando"

         # Seleccionar palabras únicas si es secuencia
        if tipo == "secuencia":
            self.palabras_seleccionadas = random.sample(self.palabras, self.total_rondas)

        print(f"🌟 ¡Comienza el minijuego {tipo.upper()}! 🌟")
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
            print("🎮 Di 'adivina', 'memoria' o 'secuencia' para iniciar un minijuego.")
            return

        comando = comando.strip().upper()
        print(f"[MundoLetrasAR] Comando recibido: {comando}")

        # Quitar prefijos
        if comando.startswith("LETRA "):
            comando = comando[6:].strip()
        elif comando.startswith("LETRAS "):
            comando = comando[7:].strip()

        # Separar letras si vienen juntas (ej: "UCS" → ["U", "C", "S"])
        comando_letras = list(comando.replace(" ", ""))
        respuesta_letras = list(self.respuesta_correcta.replace(" ", ""))

        # Comparar secuencia
        if comando_letras == respuesta_letras:
            print("✅ ¡Muy bien! Has acertado.")
            self.estrellas += 1
            if hasattr(self.state, "gestor_juegos"):
                self.state.gestor_juegos.mostrar_mensaje_pantalla("¡RESPUESTA CORRECTA!")
                time.sleep(4)
        else:
            print(f"❌ No era '{comando}'. La respuesta correcta era '{self.respuesta_correcta}'.")
            if hasattr(self.state, "gestor_juegos"):
                self.state.gestor_juegos.mostrar_mensaje_pantalla("¡RESPUESTA INCORRECTA!")
                time.sleep(2)

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
            

            # Registrar resultados y volver al menú principal
            if hasattr(self.state, "gestor_juegos"):
                self.state.gestor_juegos.registrar_resultado("letras", self.juego_en_curso, self.estrellas)
                self.state.gestor_juegos.mostrar_mensaje_pantalla(
                    f" Has ganado {self.estrellas} estrellas y {self.estrellas} lumios",
                    duracion=4
                )
                time.sleep(4)
                
            else:
                print("⚠️ No se pudo registrar el progreso (gestor no disponible).")
            
            self.state.fase = "menu_principal"

    # ---------------------------------------------------
    # MINIJUEGOS
    # ---------------------------------------------------

    def juego_adivina_letra(self):
        """
        Muestra tres letras aleatorias y pide decir la correcta.
        """
        self.modelos_a_mostrar = []
        letras = random.sample(list(rutas_letras.keys()), 1)
        self.respuesta_correcta = random.choice(letras)

        print(f"🔤 Letras mágicas aparecieron: {', '.join(letras)}")
        print("Tina: 'Dime la respuesta diciendo: Letra A, Letra B, etc.'")
        
        for letra in letras:
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
            self.modelos_a_mostrar.append(("letras", letra.upper(), marker_id))
            time.sleep(4)

    def juego_memoria_letras(self):
        """
        Muestra una secuencia de letras que el jugador debe recordar.
        """
        self.modelos_a_mostrar = []
        secuencia = random.sample(list(rutas_letras.keys()), 3)
        self.respuesta_correcta = " ".join(secuencia)

        print("✨ Observa con atención las letras mágicas...")
        print("Tina: 'Di las letras en orden diciendo: Letras A B C ...'")
        
        for letra in secuencia:
            print(f"💡 {letra}")
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
            self.modelos_a_mostrar.append(("letras", letra.upper(), marker_id))
            time.sleep(4)

    def juego_secuencia_palabra(self):
        """
        Pide formar una palabra letra por letra.
        """
        self.modelos_a_mostrar = []
        palabra = self.palabras_seleccionadas[self.ronda_actual]
        self.respuesta_correcta = " ".join(list(palabra))

        print(f"Tina: 'Vamos a formar la palabra {palabra}. Di las letras en orden.'")

        time.sleep(2)
        for letra in palabra:
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
            self.modelos_a_mostrar.append(("letras", letra.upper(), marker_id))
            time.sleep(2)