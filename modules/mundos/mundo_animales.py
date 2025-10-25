import random
import time
from models.modelos import rutas_animales, obtener_ruta_por_categoria
from modules.ui_renderer import draw_text_with_background
import unicodedata


class MundoAnimalesAR:
    """
    🌿 Mundo de los Animales — descubre las criaturas mágicas de Luminia.
    Incluye los minijuegos: adivina, sonido y clasificar.
    """

    def __init__(self, ui_renderer, voice_system, game_state):
        self.ui = ui_renderer
        self.voice = voice_system
        self.state = game_state
        self.modelos_a_mostrar = []  # lista de tuplas: (categoria, animal, marker_id)

        self.juegos = {
            "adivina": self.juego_adivina_animal,
            "sonido": self.juego_sonido_misterioso,
            "clasificar": self.juego_clasificacion_animal
        }

        self.estrellas = 0
        self.ronda_actual = 0
        self.total_rondas = 3
        self.juego_en_curso = None
        self.respuesta_correcta = None

        self.animales = {
            "Cow": "mugido",
            "Dog": "ladrido",
            "Cat": "maullido",
            "Penguin": "canto",
            "Fishbowl": "ninguno",
            "Bird": "canto",
            "Frog": "croar",
            "BowheadWhale": "canto",
            "Harp_Seal": "gruñido",
            "Horse": "relincho",
            "Pig": "gruñido",
            "Sheep": "balido",
            "Hamster": "chirrido",
            "Reindeer": "gruñido",
            "Snail": "silencio",
            "Chicken": "cloqueo",
            "Bee": "zumbido",
            "Butterfly": "silencio",
            "Snowy_Owls": "ulular"
        }

    def mostrar_mensaje(self, texto, pos=(50, 60), color=(255, 255, 255), bg_color=(56, 118, 29), font_scale=0.7):
        if hasattr(self.state, "frame_actual") and self.state.frame_actual is not None:
            draw_text_with_background(self.state.frame_actual, texto, pos, font_scale, color, bg_color)
        else:
            print(f"[MundoLetrasAR] {texto}")

    def normalizar(self, texto):
        if texto is None:
            return ""
        texto = str(texto).upper()
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
        return texto.replace(" ", "")

    def _traducir_a_modelo(self, texto_usuario):
        clave = self.normalizar(texto_usuario)

        mapeo = {
            self.normalizar("vaca"): "Cow",
            self.normalizar("perro"): "Dog",
            self.normalizar("gato"): "Cat",
            self.normalizar("caballo"): "Horse",
            self.normalizar("cerdo"): "Pig",
            self.normalizar("oveja"): "Sheep",
            self.normalizar("hámster"): "Hamster",
            self.normalizar("hamster"): "Hamster",
            self.normalizar("reno"): "Reindeer",
            self.normalizar("ciervo"): "Reindeer",
            self.normalizar("caracol"): "Snail",
            self.normalizar("conejo"): "Rabbit",
            self.normalizar("pollo"): "Chicken",
            self.normalizar("ballena"): "BowheadWhale",
            self.normalizar("foca"): "Harp_Seal",
            self.normalizar("pingüino"): "Penguin",
            self.normalizar("pinguino"): "Penguin",
            self.normalizar("pajaro"): "Bird",
            self.normalizar("pájaro"): "Bird",
            self.normalizar("ave"): "Bird",
            self.normalizar("abeja"): "Bee",
            self.normalizar("mariposa"): "Butterfly",
            self.normalizar("buho"): "Snowy_Owls",
            self.normalizar("búho"): "Snowy_Owls",

            # Nuevos animales
            self.normalizar("beluga"): "Beluga_Whale",
            self.normalizar("cangrejo"): "Crab",
            self.normalizar("medusa"): "Jellyfish",
            self.normalizar("concha"): "Seashell",
            self.normalizar("estrella de mar"): "Starfish",
            self.normalizar("pez"): "Fish",
            self.normalizar("pescado"): "Fish",
        }


        clave_ing = self.normalizar(texto_usuario)
        if clave_ing in [self.normalizar(k) for k in self.animales.keys()]:
            for k in self.animales.keys():
                if self.normalizar(k) == clave_ing:
                    return k

        return mapeo.get(clave, None)

    def iniciar(self):
        print("🐾 Bienvenido al Mundo de los Animales.")
        print("Aquí conocerás a las criaturas mágicas de Luminia.")
        print("Puedes decir: 'adivina', 'sonido' o 'clasificar' para comenzar un minijuego.")
        print("O di 'salir' para regresar al menú principal.")
        self.state.fase = "mundo_animales"

    def iniciar_juego(self, tipo):
        tipo = tipo.lower()
        if tipo not in self.juegos:
            print("⚠️ No conozco ese minijuego. Prueba con 'adivina', 'sonido' o 'clasificar'.")
            return

        self.estrellas = 0
        self.ronda_actual = 0
        self.juego_en_curso = tipo
        self.state.fase = "jugando"

        print(f"🌟 ¡Comienza el minijuego {tipo.upper()}! 🌟")
        time.sleep(0.5)
        self.juegos[tipo]()

    def procesar_comando(self, comando):
        if not self.juego_en_curso:
            print("🎮 Di 'adivina', 'sonido' o 'clasificación' para iniciar un minijuego.")
            return

        comando_traducido = self._traducir_a_modelo(comando)
        comparable = self.normalizar(comando_traducido if comando_traducido else comando)
        respuesta_normalizada = self.normalizar(self.respuesta_correcta)

        if comparable == respuesta_normalizada:
            print("✅ ¡Muy bien! Has acertado.")
            self.estrellas += 1
        else:
            nombre_correcto_visible = self._nombre_visible(self.respuesta_correcta)
            print(f"❌ No era '{comando}'. La respuesta correcta era '{nombre_correcto_visible}' ({self.respuesta_correcta}).")

        self.ronda_actual += 1
        if self.ronda_actual < self.total_rondas:
            print(f"⭐ Vamos con la ronda {self.ronda_actual + 1}...")
            time.sleep(0.8)
            self.juegos[self.juego_en_curso]()
        else:
            print("🎉 ¡Has completado el minijuego!")
            print(f"Ganaste {self.estrellas} estrellas 🌟")
            if hasattr(self.state, "gestor_juegos"):
                self.state.gestor_juegos.registrar_resultado("animales", self.juego_en_curso, self.estrellas)

    def juego_adivina_animal(self):
        opciones = random.sample(list(rutas_animales.keys()), 1)
        self.respuesta_correcta = random.choice(opciones)

        print("Tina: '¿Qué animal ves sobre la mesa mágica?'")

        self.modelos_a_mostrar = []
        for animal in opciones:
            marker_id = random.randint(1, 12)
            self.modelos_a_mostrar.append(("animales", animal, marker_id))

    def juego_sonido_misterioso(self):
        animal, sonido = random.choice(list(self.animales.items()))
        self.respuesta_correcta = animal

        print("🔊 Escucha con atención...")
        time.sleep(1)
        print(f"🔉 (Se reproduce un {sonido})")
        print("Tina: '¿Qué animal hace ese sonido?'")

        self.modelos_a_mostrar = []
        marker_id = random.randint(1, 12)
        self.modelos_a_mostrar.append(("animales", animal, marker_id))

    def juego_clasificacion_animal(self):
        animales_terrestres = [
            "Cat", "Dog", "Horse", "Cow", "Pig", "Sheep", "Hamster", "Reindeer", "Snail", "Chicken"
        ]

        animales_acuaticos = [
            "BowheadWhale", "Harp_Seal", "Penguin", "Beluga_Whale", "Fish", "Crab", "Jellyfish", "Seashell", "Starfish"
        ]

        animales_voladores = [
            "Bird", "Bee", "Butterfly", "Snowy_Owls"
    ]


        # Para asegurar variedad, mezclamos animales de otras categorías como distractores
        todos_los_animales = animales_terrestres + animales_acuaticos + animales_voladores

        if self.ronda_actual == 0:
            lista_correctos = animales_terrestres
            mensaje = "🌍 Selecciona el animal que vive en tierra."
        elif self.ronda_actual == 1:
            lista_correctos = animales_acuaticos
            mensaje = "🌊 Selecciona el animal que vive en el agua."
        else:
            lista_correctos = animales_voladores
            mensaje = "🌬️ Selecciona el animal que puede volar."

        correcto = random.choice(lista_correctos)
        distractores = [a for a in todos_los_animales if a not in lista_correctos]
        opciones = [correcto] + random.sample(distractores, 3)
        random.shuffle(opciones)

        self.respuesta_correcta = correcto

        nombres_visibles = [self._nombre_visible(a) for a in opciones]
        print(f"{mensaje} Aparecen: {', '.join(nombres_visibles)}")

        self.modelos_a_mostrar = []
        marcadores_usados = random.sample(range(1, 13), len(opciones))
        for animal, marker_id in zip(opciones, marcadores_usados):
            self.modelos_a_mostrar.append(("animales", animal, marker_id))

    def _nombre_visible(self, key):
        nombres = {
            "Cow": "vaca",
            "Dog": "perro",
            "Cat": "gato",
            "Penguin": "pingüino",
            "Fishbowl": "pez",
            "Fish": "pez pequeño",
            "Bird": "pájaro",
            "Frog": "rana",
            "BowheadWhale": "ballena",
            "Beluga_Whale": "beluga",
            "Harp_Seal": "foca",
            "Bee": "abeja",
            "Butterfly": "mariposa",
            "Snowy_Owls": "búhos",
            "Horse": "caballo",
            "Reindeer": "reno",
            "Pig": "cerdo",
            "Sheep": "oveja",
            "Rabbit": "conejo",
            "Snail": "caracol",
            "Chicken": "pollo",
            "Hamster": "hámster",
            "Crab": "cangrejo",
            "Jellyfish": "medusa",
            "Seashell": "concha",
            "Starfish": "estrella de mar"
        }
        return nombres.get(key, key)

