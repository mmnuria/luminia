import random
import time
import unicodedata
from models.modelos import (
    rutas_letras,
    rutas_animales,
    rutas_numeros,
    rutas_frutas,
    rutas_verduras,
    obtener_ruta_por_categoria
)


class MundoFinalAR:
    """
    Mundo Final de Luminia.
    Combina desafíos de todos los mundos anteriores: letras, animales, frutas y verduras, y números.
    Minijuegos: contar, secuencia y deletreo.
    """

    def __init__(self, ui_renderer, voice_system, game_state):
        self.ui = ui_renderer
        self.voice = voice_system
        self.state = game_state
        self.modelos_a_mostrar = []

        self.juegos = {
            "contar": self.juego_contar_objetos,
            "secuencia": self.juego_secuencia_mixta,
            "deletreo": self.juego_desafio_deletreo
        }

        self.estrellas = 0
        self.ronda_actual = 0
        self.total_rondas = 3
        self.juego_en_curso = None
        self.respuesta_correcta = None
        self.pregunta_actual = 0
        self.retos = []

        # Diccionarios de traducción
        self.traduccion_es_a_en = {
            "MANZANA": "Apple", "PLÁTANO": "Banana", "PLATANO": "Banana", "BANANA": "Banana",
            "ARÁNDANO": "Blueberry", "ARANDANO": "Blueberry", "CEREZA": "Cherry",
            "UVA": "Grape", "KIWI": "Kiwi", "LIMÓN": "Lemon", "LIMON": "Lemon",
            "MANGO": "Mango", "MELÓN": "Melon", "MELON": "Melon", "NARANJA": "Orange",
            "PAPAYA": "Papaya", "PERA": "Pear", "PIÑA": "Pineapple", "PINA": "Pineapple",
            "FRESA": "Strawberry", "SANDÍA": "Watermelon", "SANDIA": "Watermelon",
            "ZANAHORIA": "Carrot", "BRÓCOLI": "Broccoli", "BROCOLI": "Broccoli",
            "COLIFLOR": "Cauliflower", "PEPINO": "Cucumber", "MAÍZ": "Corn", "MAIZ": "Corn",
            "GUISANTE": "Green_Peas", "PUERRO": "Green_Leek", "CHAMPIÑÓN": "Mushroom", "CHAMPINON": "Mushroom",
            "CEBOLLA": "Onion", "CALABAZA": "Pumpkin", "ESPINACA": "Spinach",
            "PERRO": "Dog", "GATO": "Cat", "VACA": "Cow", "CABALLO": "Horse",
            "CERDO": "Pig", "OVEJA": "Sheep", "ELEFANTE": "Elephant", "LEÓN": "Lion", "LEON": "Lion",
            "TIGRE": "Tiger", "PATO": "Duck", "RATÓN": "Mouse", "RATON": "Mouse", "POLLO": "Chicken",
            "PEZ": "Fish", "MONO": "Monkey", "OSO": "Bear", "CONEJO": "Rabbit",
        }

        self.traduccion_en_a_es = {v: k.lower().replace("_", " ") for k, v in self.traduccion_es_a_en.items()}
        self.traduccion_en_a_es.update({
            "Apple": "manzana", "Banana": "plátano", "Blueberry": "arándano", "Cherry": "cereza",
            "Grape": "uva", "Kiwi": "kiwi", "Lemon": "limón", "Mango": "mango", "Melon": "melón",
            "Orange": "naranja", "Papaya": "papaya", "Pear": "pera", "Pineapple": "piña",
            "Strawberry": "fresa", "Watermelon": "sandía", "Carrot": "zanahoria",
            "Broccoli": "brócoli", "Cauliflower": "coliflor", "Cucumber": "pepino",
            "Corn": "maíz", "Green_Peas": "guisantes", "Green_Leek": "puerro",
            "Mushroom": "champiñón", "Onion": "cebolla", "Pumpkin": "calabaza",
            "Spinach": "espinaca", "Dog": "perro", "Cat": "gato", "Cow": "vaca",
            "Horse": "caballo", "Pig": "cerdo", "Sheep": "oveja", "Chicken": "pollo",
            "Fish": "pez"
        })

        self.numeros_voz = {
            "cero": "0", "uno": "1", "una": "1", "dos": "2", "tres": "3",
            "cuatro": "4", "cinco": "5", "seis": "6", "siete": "7",
            "ocho": "8", "nueve": "9", "diez": "10", "once": "11", "doce": "12"
        }

    # ---------------------------------------------------
    # UTILIDADES
    # ---------------------------------------------------
    def normalizar(self, texto):
        if texto is None:
            return ""
        texto = str(texto).upper()
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                        if unicodedata.category(c) != 'Mn')
        return texto.strip()

    def limpiar_modelos(self):
        """💧 Limpia los modelos actuales del mundo y las escenas AR renderizadas."""
        self.modelos_a_mostrar.clear()
        if hasattr(self.ui, "escenas"):
            try:
                self.ui.escenas.clear()
                print("[MundoFinalAR] Escena limpiada correctamente.")
            except Exception as e:
                print(f"[MundoFinalAR] Error al limpiar escena: {e}")
        if hasattr(self.state, "escenas"):
            try:
                self.state.escenas.clear()
            except Exception:
                pass

    def _traducir_es_a_modelo(self, token):
        if not token:
            return token
        if token.lower() in self.numeros_voz:
            return self.numeros_voz[token.lower()]
        if token in self.traduccion_es_a_en:
            return self.traduccion_es_a_en[token].lower()
        return token.capitalize().lower()

    def _mostrar_nombre_en_es(self, clave_modelo):
        if clave_modelo is None:
            return clave_modelo
        clave_cap = clave_modelo[0].upper() + clave_modelo[1:] if len(clave_modelo) > 0 else clave_modelo
        return self.traduccion_en_a_es.get(clave_cap, clave_modelo.replace("_", " "))

    # ---------------------------------------------------
    # INICIO DEL MUNDO FINAL
    # ---------------------------------------------------
    def iniciar(self):
        self.limpiar_modelos()
        print("🏆 Bienvenido al Mundo Final de Luminia.")
        print("Aquí demostrarás todo lo que has aprendido en los otros mundos.")
        print("Puedes decir: 'contar', 'secuencia' o 'deletreo' para comenzar.")
        print("O di 'salir' para regresar al menú principal.")
        self.state.fase = "mundo_final"

    # ---------------------------------------------------
    # INICIO DE JUEGO
    # ---------------------------------------------------
    def iniciar_juego(self, tipo):
        tipo = tipo.lower()
        if tipo not in self.juegos:
            print("⚠️ No conozco ese minijuego. Prueba con 'contar', 'secuencia' o 'deletreo'.")
            return

        self.estrellas = 0
        self.ronda_actual = 0
        self.juego_en_curso = tipo
        self.pregunta_actual = 0
        self.state.fase = "jugando"

        self.limpiar_modelos()
        time.sleep(2.5)

        print(f"🌟 Comienza el desafío {tipo.upper()} 🌟")
        time.sleep(0.6)
        self.juegos[tipo]()

    # ---------------------------------------------------
    # PROCESAR RESPUESTAS
    # ---------------------------------------------------
    def procesar_comando(self, comando):
        if not self.juego_en_curso:
            print("🎮 No hay un juego activo. Di 'contar', 'secuencia' o 'deletreo'.")
            return

        comando_norm = (comando or "").strip().lower()
        print(f"[MundoFinalAR] Comando recibido: {comando_norm}")

        if self.juego_en_curso == "deletreo":
            solo_letras = "".join(ch for ch in comando_norm if ch.isalpha())
            comando_traducido = "-".join(list(solo_letras.lower()))
        elif self.juego_en_curso == "contar":
            if comando_norm.startswith("hay "):
                cantidad = comando_norm[4:].strip()
                comando_traducido = self.numeros_voz.get(cantidad, cantidad)
            else:
                print("🤔 Di 'hay [número]'. Ejemplo: 'Hay tres'")
                return
        elif self.juego_en_curso == "secuencia":
            tokens = comando_norm.split()
            comando_traducido = " ".join([self._traducir_es_a_modelo(self.normalizar(t)) for t in tokens])
        else:
            comando_traducido = comando_norm

        correcto = (comando_traducido == (self.respuesta_correcta or "").lower())

        if correcto:
            print("✅ ¡Correcto!")
            self.estrellas += 1
            if hasattr(self.state, "gestor_juegos"):
                self.state.gestor_juegos.mostrar_mensaje_pantalla("RESPUESTA CORRECTA!")
                time.sleep(4)
        else:
            print(f"❌ No era correcto. La respuesta correcta era '{self.respuesta_correcta}'.")
            if hasattr(self.state, "gestor_juegos"):
                self.state.gestor_juegos.mostrar_mensaje_pantalla("RESPUESTA INCORRECTA!")
                time.sleep(2)
        self.ronda_actual += 1

        if self.ronda_actual < self.total_rondas:
            print(f"⭐ Ronda {self.ronda_actual + 1}...")
            time.sleep(1)

            self.modelos_a_mostrar = []
            self.juegos[self.juego_en_curso]()
        else:
            self._finalizar_juego()
            

    # ---------------------------------------------------
    # MINIJUEGOS
    # ---------------------------------------------------
    def juego_contar_objetos(self):
        self.modelos_a_mostrar = []
        categorias = ["animales", "frutas", "verduras"]
        cat1, cat2 = random.sample(categorias, 2)

        def elegir_obj(categoria):
            if categoria == "animales": return random.choice(list(rutas_animales.keys()))
            if categoria == "frutas": return random.choice(list(rutas_frutas.keys()))
            return random.choice(list(rutas_verduras.keys()))

        obj1, obj2 = elegir_obj(cat1), elegir_obj(cat2)
        cant1, cant2 = random.randint(1, 4), random.randint(1, 4)

        time.sleep(2.5)
        marcadores = list(range(1, 13))

        for _ in range(cant1):
            self.modelos_a_mostrar.append((cat1, obj1, marcadores.pop(0)))
            time.sleep(2.5)
        for _ in range(cant2):
            self.modelos_a_mostrar.append((cat2, obj2, marcadores.pop(0)))
            time.sleep(2.5)

        elegido = random.choice([(cat1, obj1, cant1), (cat2, obj2, cant2)])
        self.respuesta_correcta = str(elegido[2])

        print("🔢 Observa los objetos...")
        print(f"Tina: ¿Cuántos {self._mostrar_nombre_en_es(elegido[1])} hay?")
        self.state.esperando_voz = True

    def juego_secuencia_mixta(self):
        self.modelos_a_mostrar = []

        categorias = ["letras", "numeros", "animales", "frutas", "verduras"]
        secuencia = [(random.choice(categorias), None) for _ in range(4)]

        for i, (categoria, _) in enumerate(secuencia):
            if categoria == "letras": objeto = random.choice(list(rutas_letras.keys()))
            elif categoria == "numeros": objeto = random.choice(list(rutas_numeros.keys()))
            elif categoria == "animales": objeto = random.choice(list(rutas_animales.keys()))
            elif categoria == "frutas": objeto = random.choice(list(rutas_frutas.keys()))
            else: objeto = random.choice(list(rutas_verduras.keys()))
            secuencia[i] = (categoria, objeto)

        self.respuesta_correcta = " ".join([obj[1].lower() for obj in secuencia])

        time.sleep(2.5)
        marcadores = list(range(1, 13))

        print("✨ Observa la secuencia...")
        for categoria, objeto in secuencia:
            marker = marcadores.pop(0)
            self.modelos_a_mostrar.append((categoria, objeto, marker))
            print(f"💡 {self._mostrar_nombre_en_es(objeto)}")
            time.sleep(2.5)

        print("Repite la secuencia en orden (ejemplo: 'manzana perro dos plátano').")
        self.state.esperando_voz = True

    def juego_desafio_deletreo(self):
        self.modelos_a_mostrar = []
        
        categorias = ["letras", "numeros", "animales", "frutas", "verduras"]
        categoria = random.choice(categorias)
        if categoria == "letras": objeto = random.choice(list(rutas_letras.keys()))
        elif categoria == "numeros": objeto = random.choice(list(rutas_numeros.keys()))
        elif categoria == "animales": objeto = random.choice(list(rutas_animales.keys()))
        elif categoria == "frutas": objeto = random.choice(list(rutas_frutas.keys()))
        else: objeto = random.choice(list(rutas_verduras.keys()))

        self.respuesta_correcta = "-".join(list(objeto.lower()))

        time.sleep(2.5)

        marker_id = random.randint(1, 12)
        self.modelos_a_mostrar.append((categoria, objeto, marker_id))

        print(f"🔤 Deletrea el nombre del objeto {self._mostrar_nombre_en_es(objeto)}.")
        print(f"Pista: Empieza con '{objeto[0].upper()}' y tiene {len(objeto)} letras.")
        self.state.esperando_voz = True

    # ---------------------------------------------------
    # FINAL DEL JUEGO
    # ---------------------------------------------------
    def _finalizar_juego(self):
        self.modelos_a_mostrar = []
        print("🏅 ¡Has completado el desafío final!")
        print(f"Has ganado {self.estrellas} estrellas 🌟")
        
        if hasattr(self.state, "gestor_juegos"):
            try:
                self.state.gestor_juegos.registrar_resultado(
                    "final", self.juego_en_curso, self.estrellas
                )
                self.state.gestor_juegos.mostrar_mensaje_pantalla(
                    f" Has ganado {self.estrellas} estrellas y {self.estrellas} lumios",
                    duracion=4
                )
                time.sleep(4)
            except Exception:
                pass
        self.state.fase = "menu_principal"
