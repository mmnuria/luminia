import importlib
import time
from modules.game_state import GameState
from modules.mundos.mundo_letras import MundoLetrasAR
from modules.mundos.mundo_animales import MundoAnimalesAR
from modules.mundos.mundo_fruta_verdura import MundoFrutayverduraAR
from modules.mundos.mundo_numeros import MundoNumerosAR
from modules.mundos.mundo_final import MundoFinalAR
from modules.data_manager import MongoDBManager

mongo = MongoDBManager()

class GestorJuegosAR:
    """
    Controla el flujo general de los mundos y minijuegos en Luminia.
    Se comunica con el sistema de voz, UI y el estado global del juego.
    """

    def __init__(self, ui_renderer, voice_system, game_state: GameState):
        self.voice_system = voice_system
        self.state = game_state
        self.ui_renderer = ui_renderer
        
        # Mapeo de mundos con sus módulos
        self.mundos_disponibles = {
            "letras": "modules.mundos.mundo_letras",
            "animales": "modules.mundos.mundo_animales",
            "fruta_y_verdura": "modules.mundos.mundo_fruta_verdura",
            "numeros": "modules.mundos.mundo_numeros",
            "final": "modules.mundos.mundo_final",
        }
        self.traduccion_mascotas = {
            "Bear": "Oso",
            "Cat": "Gato",
            "Chicken": "Pollo",
            "Crocodile": "Cocodrilo",
            "Deer": "Ciervo",
            "Dragon": "Dragon",
            "Duck": "Pato",
            "Eagle": "Aguila",
            "Fish": "Pez",
            "Flamingo": "Flamenco",
            "Fox": "Zorro",
            "Giraffe": "Jirafa",
            "Gorilla": "Gorila",
            "Hippo": "Hipopotamo",
            "Koala": "Koala",
            "Lion": "Leon",
            "Monkey": "Mono",
            "Octopus": "Pulpo",
            "Owl": "Buho",
            "Panda": "Panda",
            "Penguin": "Pinguino",
            "Raccoon": "Mapache",
            "Rabbit": "Conejo",
            "Rat": "Rata",
            "Seel": "Foca",
            "Shark": "Tiburon",
            "Tiger": "Tigre",
            "Zebra": "Cebra",
            "tina_unicornio": "Unicornio",
            "Bee": "Abeja",
            "Butterfly": "Mariposa",
            "Horn_beetle": "Escarabajo",
        }


        self.mundo_actual = None
        self.juego_actual = None

        # Mensaje inicial
        self._mostrar("Bienvenido a Luminia, la tierra del aprendizaje mágico")
        self._mostrar("Dime el mundo que quieres visitar (si está desbloqueado).")

    # ----------------------------------------------------------
    # UTILIDAD
    # ----------------------------------------------------------
    def _mostrar(self, texto):
        """Guarda un mensaje para mostrarlo desde render_ui."""
        print(f"[Gestor] {texto}")  # debug por consola
    # ----------------------------------------------------------
    # FUNCIONES DE MENÚ
    # ----------------------------------------------------------

    def _mostrar_perfil(self):
        """Muestra información del usuario actual."""
        nombre_usuario = self.state.usuario_actual
        if not nombre_usuario:
            self._mostrar("⚠️ No hay usuario activo.")
            return

        datos = mongo.obtener_datos_usuario(nombre_usuario)
        if not datos:
            self._mostrar("⚠️ No se pudo obtener el perfil del usuario.")
            return

        nombre = datos.get("nombre", "Desconocido")
        idioma = datos.get("idioma", "No especificado")
        lumios = datos.get("lumios", 0)
        estrellas = datos.get("estrellas_totales", 0)
        fecha = datos.get("fecha_registro", "N/A")
        mundo_actual = datos.get("mundo_actual", "No definido")
        minijuego_actual = datos.get("minijuego_actual", "No definido")

        mensaje = (
            f"🌟 PERFIL DE USUARIO 🌟\n\n"
            f"👤 Nombre: {nombre}\n"
            f"🆔 ID: {datos.get('id')}\n"
            f"🗣️ Idioma: {idioma}\n"
            f"✨ Estrellas totales: {estrellas}\n"
            f"💎 Lumios: {lumios}\n"
            f"🏰 Mundo actual: {mundo_actual}\n"
            f"🎮 Minijuego actual: {minijuego_actual}\n"
            f"📅 Fecha de registro: {fecha}"
        )

        self._mostrar(mensaje)
        self.state.fase = "perfil"
        self.state.datos_perfil = datos


    def _mostrar_progreso(self):
        """Muestra el resumen de progreso por mundo y minijuego."""
        if not self.state.usuario_actual:
            self._mostrar("⚠️ No hay usuario activo.")
            return

        progreso = mongo.obtener_progreso_completo(self.state.usuario_actual)
        if not progreso:
            self._mostrar("⚠️ No se pudo obtener el progreso.")
            return

        mensaje = "📊 PROGRESO DEL USUARIO 📊\n\n"
        estrellas_totales = progreso.pop("estrellas_totales", 0)

        for mundo, datos_mundo in progreso.items():
            if isinstance(datos_mundo, dict):
                mensaje += f"🏰 {mundo.capitalize()}:\n"
                for minijuego, valor in datos_mundo.items():
                    if minijuego != "total_estrellas":
                        mensaje += f"   🎯 {minijuego}: {valor} estrellas\n"
                mensaje += f"   ⭐ Total estrellas: {datos_mundo.get('total_estrellas', 0)}\n\n"

        mensaje += f"🌟 Estrellas totales: {estrellas_totales}"
        self._mostrar(mensaje)

        self.state.fase = "progreso"
        self.state.datos_progreso = progreso


    def _mostrar_disfraces(self):
        """Muestra los disfraces comprados y disponibles."""
        if not self.state.usuario_actual:
            self._mostrar("⚠️ No hay usuario activo.")
            return

        disfraces = mongo.obtener_disfraces_usuario(self.state.usuario_actual)
        if not disfraces:
            self._mostrar("⚠️ No se pudieron obtener los disfraces.")
            return

        comprados = disfraces.get("comprados", [])
        disponibles = disfraces.get("disponibles", [])
        equipado = disfraces.get("equipado")

        mensaje = "🧥 DISFRACES DEL USUARIO 🧥\n\n"
        mensaje += f"👗 Equipado actualmente: {equipado if equipado else 'Ninguno'}\n\n"

        mensaje += "🛍️ Comprados:\n"
        if comprados:
            for d in comprados:
                mensaje += f"   ✅ {d}\n"
        else:
            mensaje += "   Ninguno\n"

        mensaje += "\n🎁 Disponibles para comprar:\n"
        if disponibles:
            for d in disponibles:
                mensaje += f"   ✨ {d}\n"
        else:
            mensaje += "   Ninguno\n"

        self._mostrar(mensaje)
        self.state.fase = "disfraces"
        self.state.datos_disfraces = disfraces

    def _equipar_disfraz(self, nombre_interno):
        """
        Equipa un disfraz y actualiza el estado local para que la UI y el 3D se actualicen inmediatamente.
        """
        if not self.state.usuario_actual:
            return

        # Actualizar estado local
        if "disponibles" not in self.state.datos_disfraces:
            self.state.datos_disfraces["disponibles"] = []
        if nombre_interno not in self.state.datos_disfraces["disponibles"]:
            self.state.datos_disfraces["disponibles"].append(nombre_interno)

        self.state.datos_disfraces["equipado"] = nombre_interno

        # También actualizar en la base de datos
        usuario_id = self.state.usuario_actual
        mongo.collection.update_one(
            {"_id": usuario_id},
            {"$addToSet": {"disfraces.disponibles": nombre_interno},  # asegura que no haya duplicados
            "$set": {"disfraces.equipado": nombre_interno}}
        )


    # ----------------------------------------------------------
    # PROCESAMIENTO DE VOZ GENERAL
    # ----------------------------------------------------------
    def procesar_comando_disfraces(self, comando):
        if not self.state.usuario_actual:
            self._mostrar("⚠️ No hay usuario activo.")
            return

        usuario_id = self.state.usuario_actual
        datos_usuario = mongo.obtener_datos_usuario(usuario_id)
        disfraces = datos_usuario.get("disfraces", {})
        lumios = datos_usuario.get("lumios", 0)

        cmd = comando.lower().strip()

        # -----------------------------
        # Comprar un disfraz
        # -----------------------------
        if cmd.startswith("comprar "):
            nombre = cmd.replace("comprar ", "").strip()
            nombre_interno = next((k for k,v in self.traduccion_mascotas.items() if v.lower() == nombre), None)
            if not nombre_interno:
                self._mostrar(f"⚠️ Disfraz '{nombre}' no existe.")
                return

            costo = 20
            if lumios < costo:
                self._mostrar("⚠️ No tienes lumios suficientes.")
                return

            # Verificar si ya está en disponibles
            if nombre_interno in disfraces.get("disponibles", []):
                self._mostrar("⚠️ Ya tienes este disfraz.")
                return

            # Actualizar MongoDB: restar lumios, añadir a disponibles y equipar
            mongo.collection.update_one(
                {"_id": usuario_id},
                {
                    "$inc": {"lumios": -costo},
                    "$push": {"disfraces.disponibles": nombre_interno},
                    "$set": {"disfraces.equipado": nombre_interno}
                }
            )

            # Actualizar estado local
            self.state.datos_disfraces["disponibles"].append(nombre_interno)
            self.state.datos_disfraces["equipado"] = nombre_interno

            # Renderizar inmediatamente
            self._equipar_disfraz(nombre_interno)
            self._mostrar(f"✅ Disfraz '{nombre}' comprado y equipado.")

            return

        # -----------------------------
        # Equipar un disfraz existente
        # -----------------------------
        if cmd.startswith("equipar "):
            nombre = cmd.replace("equipar ", "").strip()
            nombre_interno = next((k for k,v in self.traduccion_mascotas.items() if v.lower() == nombre), None)
            if not nombre_interno:
                self._mostrar(f"⚠️ Disfraz '{nombre}' no existe.")
                return

            if nombre_interno not in disfraces.get("disponibles", []):
                self._mostrar("⚠️ No puedes equipar un disfraz que no tienes.")
                return

            # Actualizar MongoDB
            mongo.collection.update_one(
                {"_id": usuario_id},
                {"$set": {"disfraces.equipado": nombre_interno}}
            )

            # Actualizar estado local y renderizar
            self.state.datos_disfraces["equipado"] = nombre_interno
            self._equipar_disfraz(nombre_interno)
            self._mostrar(f"✅ Disfraz '{nombre}' equipado.")

            return


    def procesar_comando_voz(self, comando: str):
        comando = comando.lower().strip()
        
        if comando == "perfil":
            print("[gestor] comando 'perfil'")
            self._mostrar_perfil()
            return

        elif comando == "progreso":
            print("[gestor] comando 'progreso'")
            self._mostrar_progreso()
            return

        elif comando in ["disfraz", "disfraces"]:
            print("[gestor] comando 'disfraces'")
            self._mostrar_disfraces()
            return
       
        elif comando.startswith("comprar ") or comando.startswith("equipar "):
            print("[gestor] comprando/equipando")
            self.procesar_comando_disfraces(comando)

        
        if self.state.fase == "menu_principal":
            self._manejar_eleccion_mundo(comando)
        elif self.state.fase.startswith("mundo_") and self.mundo_actual:
            self._manejar_comando_mundo(comando)
        elif self.state.fase == "jugando" and self.mundo_actual:
            self.mundo_actual.procesar_comando(comando)
        elif comando in ["salir", "menú", "menu"]:
            self._salir_mundo()
        else:
            self._mostrar("No entendí ese comando. Prueba con: letras, animales, frutas y verduras, números o final.")

    def mostrar_mensaje_pantalla(self, texto, duracion=2.5):
        """Guarda un mensaje para mostrarlo temporalmente en pantalla."""
        self.state.mensaje_pantalla = texto
        self.state.tiempo_mensaje = time.time() + duracion

    # ----------------------------------------------------------
    # MANEJO DE MUNDOS
    # ----------------------------------------------------------
    def _manejar_eleccion_mundo(self, comando):
        if comando in self.mundos_disponibles:
            # El _id del usuario ya está en GameState
            if self.state.usuario_actual:
                nombre_usuario = self.state.usuario_actual  # string / _id en MongoDB

                # Usamos las funciones de data_manager
                mundos = mongo.mundos_desbloqueados_usuario(nombre_usuario)

                if mundos.get(comando, True):
                    self._cargar_mundo(comando)
                else:
                    self._mostrar(
                        "Todavía no has desbloqueado este mundo. ¡Consigue más estrellas para avanzar! "
                    )
            else:
                self._mostrar("Usuario no definido o no encontrado en la base de datos.")
        else:
            self._mostrar(
                "Mundo no reconocido. Di: letras, animales, frutas y verduras, números o final."
            )

    def _cargar_mundo(self, nombre_mundo):
        modulo_nombre = self.mundos_disponibles[nombre_mundo]
        try:
            modulo = importlib.import_module(modulo_nombre)
            clase_nombre = f"Mundo{nombre_mundo.replace('_', '').capitalize()}AR"
            clase_mundo = getattr(modulo, clase_nombre)

            # Crear instancia del mundo
            instancia = clase_mundo(self.ui_renderer, self.voice_system, self.state)

            # Guardar en el estado global (para que realidad_mixta lo encuentre)
            setattr(self.state, f"instancia_mundo_{nombre_mundo}", instancia)

            # Establecer fase y mundo actual
            self.mundo_actual = instancia
            self.state.establecer_fase(f"mundo_{nombre_mundo}", mundo=nombre_mundo)

            self._mostrar(f"Entrando al Mundo de las {nombre_mundo.replace('_', ' ').capitalize()}...")
            instancia.iniciar()

            print(f"[GestorJuegosAR] Mundo '{nombre_mundo}' cargado y guardado en GameState.")

        except Exception as e:
            self._mostrar(f"Error al cargar el mundo {nombre_mundo}: {e}")

    # ----------------------------------------------------------
    # MANEJO DE MINIJUEGOS
    # ----------------------------------------------------------
    def _manejar_comando_mundo(self, comando):
        comando = comando.lower().strip()
        juegos_validos = [
            "adivina", "memoria", "secuencia",
            "contar", "deletreo",
            "sonido", "clasificar","adivina", "suma", "mayor", "color", "clasifica"
        ]

        if comando in juegos_validos:
            self._iniciar_minijuego(comando)
        elif comando == "salir":
            self._salir_mundo()
        else:
            self._mostrar("🎮 Comando no reconocido. Prueba con los minijuegos disponibles en este mundo.")

    def _iniciar_minijuego(self, tipo_juego):
        # Si no hay un mundo actual, lo creamos en función del tipo
        if not self.mundo_actual:
            if tipo_juego == "letras":
                self.mundo_actual = MundoLetrasAR(self.state)
            elif tipo_juego == "animales":
                self.mundo_actual = MundoAnimalesAR(self.state)
            elif tipo_juego in ["frutas", "verduras"]:
                self.mundo_actual = MundoFrutayverduraAR(self.state)
            elif tipo_juego == "numeros":
                self.mundo_actual = MundoNumerosAR(self.state)
            elif tipo_juego == "final":
                self.mundo_actual = MundoFinalAR(self.state)
            else:
                self._mostrar(f"⚠️ No se reconoce el tipo de juego: {tipo_juego}")
                return

        # Cambiamos la fase del estado global
        self.state.establecer_fase("jugando", minijuego=tipo_juego)
        self.juego_actual = tipo_juego

        self._mostrar(f"Iniciando minijuego: {tipo_juego.title()}...")

        try:
            self.mundo_actual.iniciar_juego(tipo_juego)
        except Exception as e:
            self._mostrar(f"Error al iniciar el minijuego '{tipo_juego}': {e}")

    # ----------------------------------------------------------
    # SALIDA Y PROGRESO
    # ----------------------------------------------------------
    def _salir_mundo(self):
        if self.mundo_actual:
            self._mostrar("🏰 Regresando al menú principal...")
        self.mundo_actual = None
        self.state.establecer_fase("menu_principal")

    def registrar_resultado(self, mundo, minijuego, estrellas):
        """
        Registra los resultados del jugador tras un minijuego
        y verifica desbloqueos de nuevos mundos.
        """
        self.state.registrar_resultado(mundo, minijuego, estrellas)

        total_categoria = sum(
            v for k, v in self.state.obtener_progreso(mundo).items() if k != "total_estrellas"
        )

        total_general = self.state.usuario_data["estrellas_totales"]

        self._mostrar(f"Has ganado {estrellas} estrellas en '{minijuego}' del mundo {mundo.capitalize()}!")
        self._mostrar(f"Total en {mundo.capitalize()}: {total_categoria} ⭐ | General: {total_general} ⭐")

        self.state._verificar_desbloqueos()
        self._salir_mundo()
