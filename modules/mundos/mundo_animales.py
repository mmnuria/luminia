import random
import time
from models.modelos import rutas_animales, obtener_ruta_por_categoria


class MundoAnimalesAR:
    """
    🌿 Mundo de los Animales — descubre las criaturas mágicas de Luminia.
    Incluye los minijuegos: adivina, sonido y clasificación.
    """

    def __init__(self, ui_renderer, voice_system, game_state):
        self.ui = ui_renderer
        self.voice = voice_system
        self.state = game_state
        self.modelos_a_mostrar = []  # lista de tuplas: (categoria, animal, marker_id)

        self.juegos = {
            "adivina": self.juego_adivina_animal,
            "sonido": self.juego_sonido_misterioso,
            "clasificacion": self.juego_clasificacion_animal
        }

        self.estrellas = 0
        self.ronda_actual = 0
        self.total_rondas = 3
        self.juego_en_curso = None
        self.respuesta_correcta = None

        self.animales = {
            "Cow": "mugido",       # vaca
            "Dog": "ladrido",      # perro
            "Cat": "maullido",     # gato
            "Penguin": "canto",    # pingüino
            "Fishbowl": "ninguno", # pez
            "Bird": "canto",       # pájaro
            "Frog": "croar",       # rana
        }

        self.animales_acuaticos = ["Fishbowl", "BowheadWhale", "Harp_Seal"]

    # ---------------------------------------------------
    # INICIO DEL MUNDO
    # ---------------------------------------------------
    def iniciar(self):
        self.ui.mostrar_mensaje("🐾 Bienvenido al Mundo de los Animales.")
        self.ui.mostrar_mensaje("Aquí conocerás a las criaturas mágicas de Luminia.")
        self.ui.mostrar_mensaje("Puedes decir: 'adivina', 'sonido' o 'clasificación' para comenzar un minijuego.")
        self.ui.mostrar_mensaje("O di 'salir' para regresar al menú principal.")
        self.state.fase = "mundo_animales"

    # ---------------------------------------------------
    # INICIO DE MINIJUEGO
    # ---------------------------------------------------
    def iniciar_juego(self, tipo):
        tipo = tipo.lower()
        if tipo not in self.juegos:
            self.ui.mostrar_mensaje("⚠️ No conozco ese minijuego. Prueba con 'adivina', 'sonido' o 'clasificación'.")
            return

        self.estrellas = 0
        self.ronda_actual = 0
        self.juego_en_curso = tipo
        self.state.fase = "jugando"

        self.ui.mostrar_mensaje(f"🌟 ¡Comienza el minijuego {tipo.upper()}! 🌟")
        time.sleep(0.5)
        self.juegos[tipo]()

    # ---------------------------------------------------
    # PROCESAMIENTO DE COMANDOS
    # ---------------------------------------------------
    def procesar_comando(self, comando):
        if not self.juego_en_curso:
            self.ui.mostrar_mensaje("🎮 Di 'adivina', 'sonido' o 'clasificación' para iniciar un minijuego.")
            return

        comando = comando.strip().lower()

        traducciones = {
            "vaca": "Cow",
            "perro": "Dog",
            "gato": "Cat",
            "pingüino": "Penguin",
            "pinguino": "Penguin",
            "pez": "Fishbowl",
            "pájaro": "Bird",
            "pajaro": "Bird",
            "rana": "Frog",
            "ballena": "BowheadWhale",
            "foca": "Harp_Seal"
        }
        comando_traducido = traducciones.get(comando, comando)

        if comando_traducido == self.respuesta_correcta:
            self.ui.mostrar_mensaje("✅ ¡Muy bien! Has acertado.")
            self.estrellas += 1
        else:
            self.ui.mostrar_mensaje(f"❌ No era '{comando}'. La respuesta correcta era '{self.respuesta_correcta}'.")

        # Siguiente ronda o fin
        self.ronda_actual += 1
        if self.ronda_actual < self.total_rondas:
            self.ui.mostrar_mensaje(f"⭐ Vamos con la ronda {self.ronda_actual + 1}...")
            time.sleep(0.8)
            self.juegos[self.juego_en_curso]()
        else:
            self.ui.mostrar_mensaje("🎉 ¡Has completado el minijuego!")
            self.ui.mostrar_mensaje(f"Ganaste {self.estrellas} estrellas 🌟")
            if hasattr(self.state, "gestor_juegos"):
                self.state.gestor_juegos.registrar_resultado("animales", self.juego_en_curso, self.estrellas)

    # ---------------------------------------------------
    # MINIJUEGOS
    # ---------------------------------------------------

    def juego_adivina_animal(self):
        """
        Muestra tres animales y pide identificar el correcto.
        """
        opciones = random.sample(list(rutas_animales.keys()), 3)
        self.respuesta_correcta = random.choice(opciones)

        nombres_visibles = [self._nombre_visible(a) for a in opciones]
        self.ui.mostrar_mensaje(f"🦁 Aparecen los animales: {', '.join(nombres_visibles)}")
        self.ui.mostrar_mensaje("Tina: '¿Qué animal ves sobre la mesa mágica?'")

        for animal in opciones:
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
            self.modelos_a_mostrar.append(("animales", animal, marker_id))

    def juego_sonido_misterioso(self):
        """
        Reproduce un sonido y pide identificar al animal.
        """
        animal, sonido = random.choice(list(self.animales.items()))
        self.respuesta_correcta = animal

        self.ui.mostrar_mensaje("🔊 Escucha con atención...")
        time.sleep(1)
        self.ui.mostrar_mensaje(f"🔉 (Se reproduce un {sonido})")
        self.ui.mostrar_mensaje("Tina: '¿Qué animal hace ese sonido?'")

        marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        self.modelos_a_mostrar.append(("animales", animal, marker_id))

    def juego_clasificacion_animal(self):
        """
        Pide seleccionar qué animal vive en el agua.
        """
        opciones = random.sample(list(rutas_animales.keys()), 4)
        correctos = [a for a in opciones if a in self.animales_acuaticos]

        self.respuesta_correcta = random.choice(correctos) if correctos else random.choice(opciones)
        nombres_visibles = [self._nombre_visible(a) for a in opciones]

        self.ui.mostrar_mensaje(f"🌍 Aparecen los animales: {', '.join(nombres_visibles)}")
        self.ui.mostrar_mensaje("Tina: '¿Cuál de estos animales vive en el agua?'")

        for animal in opciones:
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
            self.modelos_a_mostrar.append(("animales", animal, marker_id))

    # ---------------------------------------------------
    # UTILIDAD INTERNA
    # ---------------------------------------------------
    def _nombre_visible(self, key):
        """
        Traduce claves de modelo a nombres legibles para mensajes.
        """
        nombres = {
            "Cow": "vaca",
            "Dog": "perro",
            "Cat": "gato",
            "Penguin": "pingüino",
            "Fishbowl": "pez",
            "Bird": "pájaro",
            "Frog": "rana",
            "BowheadWhale": "ballena",
            "Harp_Seal": "foca"
        }
        return nombres.get(key, key)
