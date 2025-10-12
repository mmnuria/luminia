import random
import time
from models.modelos import rutas_letras, rutas_animales, rutas_numeros, rutas_frutas, rutas_verduras, obtener_ruta_por_categoria

class MundoFinalAR:
    def __init__(self, ui_renderer, voice_system, game_state):
        self.ui = ui_renderer
        self.voice = voice_system
        self.state = game_state

        self.juegos = {
            "reto": self.juego_reto_mixto,
            "secuencia": self.juego_secuencia_mixta,
            "desafio": self.juego_desafio_final
        }

        self.estrellas = 0
        self.ronda_actual = 0
        self.total_rondas = 3
        self.juego_en_curso = None
        self.respuesta_correcta = None
        self.pregunta_actual = 0  # Para desafío final

    def iniciar(self):
        self.ui.mostrar_mensaje("🏆 Bienvenido al Mundo Final de Luminia.")
        self.ui.mostrar_mensaje("Aquí demostrarás todo lo que has aprendido.")
        self.ui.mostrar_mensaje("Puedes decir: 'reto', 'secuencia' o 'desafio' para comenzar.")
        self.ui.mostrar_mensaje("O di 'salir' para regresar al menú principal.")
        # Castillo en marcador 11 manejado por ui_renderer

    def iniciar_juego(self, tipo):
        if tipo not in self.juegos:
            self.ui.mostrar_mensaje("⚠️ No conozco ese minijuego. Prueba con 'reto', 'secuencia' o 'desafio'.")
            return

        self.estrellas = 0
        self.ronda_actual = 0
        self.juego_en_curso = tipo
        self.pregunta_actual = 0

        self.ui.mostrar_mensaje(f"🌟 Comenzamos el desafío: {tipo.upper()} 🌟")
        self.juegos[tipo]()

    def procesar_comando(self, comando):
        if not self.juego_en_curso:
            self.ui.mostrar_mensaje("No hay un juego activo. Di 'reto', 'secuencia' o 'desafio' para jugar.")
            return

        comando = comando.strip().lower()

        traducciones = {
            "manzana": "Apple",
            "vaca": "Cow",
            "perro": "Dog",
            "gato": "Cat",
            "pingüino": "Penguin",
            "pez": "Fishbowl",
            "pájaro": "Bird",
            "rana": "Frog",
            "ballena": "BowheadWhale",
            "foca": "Harp_Seal",
            "plátano": "Banana",
            "naranja": "Orange",
            "fresa": "Strawberry",
            "zanahoria": "Carrot",
            "pepino": "Cucumber",
            "tomate": "Tomato",
            "espinaca": "Spinach",
            "uva": "Grape",
            "uvas": "Grape",
            "cero": "0",
            "uno": "1",
            "dos": "2",
            "tres": "3",
            "cuatro": "4",
            "cinco": "5",
            "seis": "6",
            "siete": "7",
            "ocho": "8",
            "nueve": "9"
        }
        comando_traducido = traducciones.get(comando, comando)

        if self.juego_en_curso == "desafio" and self.pregunta_actual < len(self.retos):
            if comando_traducido == self.respuesta_correcta:
                self.ui.mostrar_mensaje("✅ ¡Correcto!")
                self.estrellas += 1
            else:
                self.ui.mostrar_mensaje(f"❌ No, era '{self.respuesta_correcta}'.")
            self.pregunta_actual += 1
            self._siguiente_pregunta_desafio()
        else:
            if comando_traducido == self.respuesta_correcta:
                self.ui.mostrar_mensaje("✅ ¡Excelente! Has acertado.")
                self.estrellas += 1
            else:
                self.ui.mostrar_mensaje(f"❌ No era '{comando}'. La respuesta correcta era '{self.respuesta_correcta}'.")

            self.ronda_actual += 1
            if self.ronda_actual < self.total_rondas:
                self.ui.mostrar_mensaje(f"⭐ Ronda {self.ronda_actual + 1}...")
                self.juegos[self.juego_en_curso]()
            else:
                self.ui.mostrar_mensaje("🏅 ¡Has completado el desafío final!")
                self.ui.mostrar_mensaje(f"Ganaste {self.estrellas} estrellas 🌟")
                self.state.gestor_juegos.registrar_resultado("final", self.juego_en_curso, self.estrellas)

    def juego_reto_mixto(self):
        preguntas = [
            ("Aparecen frutas. ¿Cuál empieza con la letra M?", "Apple", "frutas", "Apple"),
            ("¿Qué animal hace 'muuu'?", "Cow", "animales", "Cow"),
            ("¿Cuál es el número que viene después del 4?", "5", "numeros", "5"),
            ("¿Qué letra suena al inicio de 'Gato'?", "G", "letras", "G"),
        ]
        texto, respuesta, categoria, modelo = random.choice(preguntas)
        self.respuesta_correcta = respuesta.lower()

        self.ui.mostrar_mensaje("🔮 Tina: " + texto)
        marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        self.ui.mostrar_modelo(categoria, modelo, marker_id)
        self.ui.mostrar_mensaje("(Responde en voz alta)")

    def juego_secuencia_mixta(self):
        secuencias = [
            ["A", "Cow", "2"],
            ["B", "Dog", "4"],
            ["C", "Apple", "1"],
        ]
        secuencia = random.choice(secuencias)
        self.respuesta_correcta = ", ".join([s.lower() for s in secuencia])

        self.ui.mostrar_mensaje("✨ Tina: Recuerda esta secuencia:")
        for item in secuencia:
            if item in rutas_letras:
                categoria = "letras"
            elif item in rutas_animales:
                categoria = "animales"
            elif item in rutas_numeros:
                categoria = "numeros"
            elif item in rutas_frutas:
                categoria = "frutas"
            elif item in rutas_verduras:
                categoria = "verduras"
            marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
            self.ui.mostrar_modelo(categoria, item, marker_id)
            self.ui.mostrar_mensaje(f"💡 {item}")
            time.sleep(0.8)
        self.ui.mostrar_mensaje("Ahora repítela en el mismo orden (ejemplo: 'a, gato, dos').")

    def juego_desafio_final(self):
        self.retos = [
            ("¿Qué animal dice 'miau'?", "Cat", "animales", "Cat"),
            ("¿Cuántas letras tiene la palabra 'sol'?", "3", "numeros", "3"),
            ("¿Qué número es mayor, 7 o 9?", "9", "numeros", "9")
        ]
        self.pregunta_actual = 0
        self._siguiente_pregunta_desafio()

    def _siguiente_pregunta_desafio(self):
        if self.pregunta_actual >= len(self.retos):
            self.ronda_actual += 1
            if self.ronda_actual < self.total_rondas:
                self.ui.mostrar_mensaje(f"⭐ Ronda {self.ronda_actual + 1}...")
                self.juego_desafio_final()
            else:
                self.ui.mostrar_mensaje("🏅 ¡Has completado el desafío final!")
                self.ui.mostrar_mensaje(f"Ganaste {self.estrellas} estrellas 🌟")
                self.state.gestor_juegos.registrar_resultado("final", self.juego_en_curso, self.estrellas)
            return

        texto, respuesta, categoria, modelo = self.retos[self.pregunta_actual]
        self.respuesta_correcta = respuesta.lower()

        self.ui.mostrar_mensaje(f"Tina: {texto}")
        marker_id = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        self.ui.mostrar_modelo(categoria, modelo, marker_id)
        self.ui.mostrar_mensaje("(Responde...)")
        self.state.esperando_voz = True