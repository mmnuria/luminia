import importlib
from modules.game_state import GameState
from modules.mundos.mundo_letras import MundoLetrasAR
from modules.mundos.mundo_animales import MundoAnimalesAR
from modules.mundos.mundo_fruta_verdura import MundoFrutayverduraAR
from modules.mundos.mundo_numeros import MundoNumerosAR
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

        self.mundo_actual = None
        self.juego_actual = None

        # Mensaje inicial
        self._mostrar("✨ Bienvenido a Luminia, la tierra del aprendizaje mágico ✨")
        self._mostrar("Dime el mundo que quieres visitar (si está desbloqueado).")

        
    # ----------------------------------------------------------
    # UTILIDAD
    # ----------------------------------------------------------
    def _mostrar(self, texto):
        """Guarda un mensaje para mostrarlo desde render_ui."""
        self.state.mensaje_actual = texto
        print(f"[Gestor] {texto}")  # debug por consola

    # ----------------------------------------------------------
    # PROCESAMIENTO DE VOZ GENERAL
    # ----------------------------------------------------------
    def procesar_comando_voz(self, comando: str):
        comando = comando.lower().strip()

        if self.state.fase == "menu_principal":
            self._manejar_eleccion_mundo(comando)
        elif self.state.fase.startswith("mundo_") and self.mundo_actual:
            self._manejar_comando_mundo(comando)
        elif self.state.fase == "jugando" and self.mundo_actual:
            self.mundo_actual.procesar_comando(comando)
        elif comando in ["salir", "menú", "menu"]:
            self._salir_mundo()
        else:
            self._mostrar("🤔 No entendí ese comando. Prueba con: letras, animales, frutas y verduras, números o final.")

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
                        "🚫 Todavía no has desbloqueado este mundo. ¡Consigue más estrellas para avanzar! ⭐"
                    )
            else:
                self._mostrar("⚠️ Usuario no definido o no encontrado en la base de datos.")
        else:
            self._mostrar(
                "❌ Mundo no reconocido. Di: letras, animales, frutas y verduras, números o final."
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

            self._mostrar(f"🌈 Entrando al Mundo de las {nombre_mundo.replace('_', ' ').capitalize()}...")
            instancia.iniciar()

            print(f"[GestorJuegosAR] ✅ Mundo '{nombre_mundo}' cargado y guardado en GameState.")

        except Exception as e:
            self._mostrar(f"⚠️ Error al cargar el mundo {nombre_mundo}: {e}")


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
            else:
                self._mostrar(f"⚠️ No se reconoce el tipo de juego: {tipo_juego}")
                return

        # Cambiamos la fase del estado global
        self.state.establecer_fase("jugando", minijuego=tipo_juego)
        self.juego_actual = tipo_juego

        self._mostrar(f"🎯 Iniciando minijuego: {tipo_juego.title()}...")

        try:
            self.mundo_actual.iniciar_juego(tipo_juego)
        except Exception as e:
            self._mostrar(f"⚠️ Error al iniciar el minijuego '{tipo_juego}': {e}")

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

        self._mostrar(f"✨ Has ganado {estrellas} estrellas en '{minijuego}' del mundo {mundo.capitalize()}!")
        self._mostrar(f"🌟 Total en {mundo.capitalize()}: {total_categoria} ⭐ | General: {total_general} ⭐")

        self.state._verificar_desbloqueos()
        self._salir_mundo()
