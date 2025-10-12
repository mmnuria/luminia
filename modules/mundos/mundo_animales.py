import random
import time
from models.modelosNuevo import rutas_animales, obtener_ruta_por_categoria

class MundoAnimalesAR:
    def __init__(self, ui_renderer, voice_system, game_state):
        self.ui = ui_renderer
        self.voice = voice_system
        self.state = game_state

        self.juegos = {
            "adivina": self.juego_adivina_animal,
            "sonido": self.juego_sonido_misterioso,
            "clasificacion": self.juego_clasificacion_animal
        }

        self.estrellas = 0
        self.ronda_actual = 0
        self.total_rondas = 3
        self.juego_en_curso = None

        self.animales = {
            "Cow": "mugido",      # vaca
            "Dog": "ladrido",     # perro
            "Cat": "maullido",    # gato
            "Penguin": "canto",   # pingüino
            "Fishbowl": "ninguno",# pez
            "Bird": "canto",      # pájaro
            "Frog": "croar"       # rana (asumimos disponible o ajustar)
        }

        self.animales_acuaticos = ["Fishbowl", "BowheadWhale", "Harp_Seal"]  # pez, ballena, foca

    def iniciar(self):
        self.ui.mostrar_mensaje("🐾 Bienvenido al Mundo de los Animales.")
        self.ui.mostrar_mensaje("Aquí conocerás a las criaturas mágicas de Luminia.")
        self.ui.mostrar_mensaje("Puedes decir: 'adivina', 'sonido' o 'clasificación' para comenzar un minijuego.")
        self.ui.mostrar_mensaje("O di 'salir' para regresar al menú principal.")
        # Castillo en marcador 3 manejado por ui_renderer

    def iniciar_juego(self, tipo):
        if tipo not in self.juegos:
            self.ui.mostrar_mensaje("⚠️ No conozco ese minijuego. Prueba con 'adivina', 'sonido' o 'clasificación'.")
            return

        self.estrellas = 0
        self.ronda_actual = 0
        self.juego_en_curso = tipo

        self.ui.mostrar_mensaje(f"🌟 Comenzamos el juego: {tipo.upper()} 🌟")
        self.juegos[tipo]()

    def procesar_comando(self, comando):
        if not self.juego_en_curso:
            self.ui.mostrar_mensaje("No hay un juego activo. Di 'adivina', 'sonido' o 'clasificación' para jugar.")
            return

        comando = comando.strip().lower()

        traducciones = {
            "vaca": "Cow",
            "perro": "Dog",
            "gato": "Cat",
            "pingüino": "Penguin",
            "pez": "Fishbowl",
            "pájaro": "Bird",
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

        self.ronda_actual += 1
        if self.ronda_actual < self.total_rondas:
            self.ui.mostrar_mensaje(f"⭐ Vamos con la ronda {self.ronda_actual + 1}...")
            self.juegos[self.juego_en_curso]()
        else:
            self.ui.mostrar_mensaje("🎉 ¡Has completado el minijuego!")
            self.ui.mostrar_mensaje(f"Ganaste {self.estrellas} estrellas 🌟")
            self.state.gestor_juegos.registrar_resultado("animales", self.juego_en_curso, self.estrellas)

    def juego_adivina_animal(self):
        opciones = random.sample(list(rutas_animales.keys()), 3)
        self.respuesta_correcta = random.choice(opciones)

        self.ui.mostrar_mensaje(f"🦁 Aparecen los animales: {', '.join(opciones)}")
        self.ui.mostrar_mensaje("Tina: '¿Qué animal es este?'")
        self.ui.mostrar_mensaje("(Responde diciendo el nombre del animal correcto)")
        for animal in opciones:
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])  # Todos menos 0
            self.ui.mostrar_modelo("animales", animal, marker_id)

    def juego_sonido_misterioso(self):
        animal, sonido = random.choice(list(self.animales.items()))
        self.respuesta_correcta = animal

        self.ui.mostrar_mensaje("🔊 Escucha con atención...")
        time.sleep(1)
        self.ui.mostrar_mensaje(f"🔉 (Se reproduce un {sonido})")
        self.ui.mostrar_mensaje("Tina: '¿Qué animal hace ese sonido?'")
        marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])  # Todos menos 0
        self.ui.mostrar_modelo("animales", animal, marker_id)

    def juego_clasificacion_animal(self):
        opciones = random.sample(list(rutas_animales.keys()), 4)
        correctos = [a for a in opciones if a in self.animales_acuaticos]

        if correctos:
            self.respuesta_correcta = random.choice(correctos)
        else:
            self.respuesta_correcta = random.choice(opciones)

        self.ui.mostrar_mensaje(f"🌍 Aparecen los animales: {', '.join(opciones)}")
        self.ui.mostrar_mensaje("Tina: '¿Qué animales viven en el agua?'")
        self.ui.mostrar_mensaje("(Responde con el nombre de un animal acuático)")
        for animal in opciones:
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])  # Todos menos 0
            self.ui.mostrar_modelo("animales", animal, marker_id)