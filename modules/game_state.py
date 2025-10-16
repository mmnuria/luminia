import json
import os
import cv2

DATA_PATH = "data/game_state.json"

# ----- CONFIGURACIÓN RECONOCIMIENTO FACIAL -----
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

class GameState:
    """
    Representa el estado global del juego Luminia.
    Controla la fase actual, mundo activo, minijuego, y desbloqueos.
    """

    def __init__(self):
        # Fase actual del juego (inicio, menu_principal, mundo_letras, jugando, etc.)
        self.fase = "inicio"

        # Nombre del mundo actual (letras, animales, etc.)
        self.mundo_actual = None

        # Minijuego actual dentro del mundo
        self.minijuego_actual = None

        # Estados desbloqueados (control de avance global)
        self.mundos_desbloqueados = {
            "letras": True,  # Siempre disponible
            "animales": False,
            "fruta_y_verdura": False,
            "numeros": False,
            "final": False,
        }

        # Datos del usuario asociados
        self.usuario_data = {
            "nombre": None,
            "estrellas_totales": 0,
            "progreso": {}
        }

        self.marcadores_castillos = {
            1: "letras",
            3: "animales",
            4: "fruta_y_verdura",
            6: "numeros",
            11: "final"
        }

        # Instancias de mundos AR
        self.instancia_mundo_letras = None
        self.instancia_mundo_animales = None
        self.instancia_mundo_numeros = None
        self.instancia_mundo_fruta_y_verdura = None
        self.instancia_mundo_final = None


    # ----------------------------------------------------------
    # ESTADO Y PROGRESO
    # ----------------------------------------------------------
    def sincronizar_con_usuario(self, usuario):
        """
        Actualiza los mundos desbloqueados según el total de estrellas del usuario.
        """
        desbloqueos = {
            0: "letras",
            5: "animales",
            10: "fruta_y_verdura",
            15: "numeros",
            20: "final",
        }

        for estrellas_req, mundo in desbloqueos.items():
            self.mundos_desbloqueados[mundo] = usuario.estrellas_totales >= estrellas_req

        print(f"🔄 Mundos desbloqueados actualizados según progreso de {usuario.nombre}:")
        for m, estado in self.mundos_desbloqueados.items():
            print(f"   · {m.capitalize()}: {'✅' if estado else '🔒'}")

        self.usuario_data["nombre"] = usuario.nombre
        self.usuario_data["estrellas_totales"] = usuario.estrellas_totales

    def establecer_fase(self, nueva_fase, mundo=None, minijuego=None):
        """
        Cambia la fase actual del juego.
        """
        self.fase = nueva_fase
        if mundo:
            self.mundo_actual = mundo
        if minijuego:
            self.minijuego_actual = minijuego
        print(f"🎮 Estado actualizado → Fase: {self.fase}, Mundo: {self.mundo_actual}, Minijuego: {self.minijuego_actual}")

    def reiniciar(self):
        """
        Reinicia el estado global del juego a su configuración inicial.
        """
        self.__init__()
        print("🔁 Estado global del juego reiniciado.")

    # ----------------------------------------------------------
    # APOYO AL GESTOR DE JUEGOS
    # ----------------------------------------------------------
    def mundo_desbloqueado(self, nombre_mundo: str) -> bool:
        """
        Indica si un mundo está desbloqueado.
        """
        return self.mundos_desbloqueados.get(nombre_mundo, False)

    def registrar_resultado(self, mundo, minijuego, estrellas):
        """
        Registra el resultado de un minijuego.
        """
        if mundo not in self.usuario_data["progreso"]:
            self.usuario_data["progreso"][mundo] = {}

        self.usuario_data["progreso"][mundo][minijuego] = {"estrellas": estrellas}

        # Actualiza el total de estrellas del jugador
        self.usuario_data["estrellas_totales"] = sum(
            j["estrellas"]
            for m in self.usuario_data["progreso"].values()
            for j in m.values()
        )

        print(f"⭐ Progreso actualizado → {self.usuario_data['estrellas_totales']} estrellas totales.")
        self._verificar_desbloqueos()
        self.guardar()

    def obtener_progreso(self, mundo):
        """
        Devuelve el progreso guardado para un mundo.
        """
        return self.usuario_data["progreso"].get(mundo, {})

    def _verificar_desbloqueos(self):
        """
        Verifica si se han desbloqueado nuevos mundos tras ganar estrellas.
        """
        total = self.usuario_data["estrellas_totales"]
        umbrales = {
            "animales": 5,
            "fruta_y_verdura": 10,
            "numeros": 15,
            "final": 20,
        }

        for mundo, estrellas_req in umbrales.items():
            if total >= estrellas_req and not self.mundos_desbloqueados[mundo]:
                self.mundos_desbloqueados[mundo] = True
                print(f"🌟 ¡Nuevo mundo desbloqueado!: {mundo.capitalize()}")

    # ----------------------------------------------------------
    # PERSISTENCIA
    # ----------------------------------------------------------
    def guardar(self):
        """
        Guarda el estado actual en data/game_state.json.
        """
        if not os.path.exists("data"):
            os.makedirs("data")

        datos = {
            "fase": self.fase,
            "mundo_actual": self.mundo_actual,
            "minijuego_actual": self.minijuego_actual,
            "mundos_desbloqueados": self.mundos_desbloqueados,
            "usuario_data": self.usuario_data,
        }

        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)

        print("💾 Estado global del juego guardado correctamente.")

    @classmethod
    def cargar(cls):
        """
        Carga el estado previo del juego si existe.
        """
        if not os.path.exists(DATA_PATH):
            print("⚠️ No se encontró un estado previo. Se iniciará uno nuevo.")
            return cls()

        with open(DATA_PATH, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except json.JSONDecodeError:
                print("⚠️ Archivo de estado corrupto. Se generará uno nuevo.")
                return cls()

        gs = cls()
        gs.fase = datos.get("fase", "inicio")
        gs.mundo_actual = datos.get("mundo_actual")
        gs.minijuego_actual = datos.get("minijuego_actual")
        gs.mundos_desbloqueados = datos.get("mundos_desbloqueados", gs.mundos_desbloqueados)
        gs.usuario_data = datos.get("usuario_data", gs.usuario_data)

        print(f"🔄 Estado global cargado: Fase={gs.fase}, Mundo={gs.mundo_actual}, Minijuego={gs.minijuego_actual}")
        return gs

    # ----------------------------------------------------------
    # INFORMACIÓN
    # ----------------------------------------------------------
    def mostrar_estado(self):
        """
        Muestra un resumen legible del estado actual del juego.
        """
        print("\n🎯 ESTADO ACTUAL DE LUMINIA")
        print(f"Fase actual: {self.fase}")
        print(f"Mundo actual: {self.mundo_actual or 'Ninguno'}")
        print(f"Minijuego actual: {self.minijuego_actual or 'Ninguno'}")
        print("Mundos desbloqueados:")
        for mundo, desbloqueado in self.mundos_desbloqueados.items():
            estado = "✅" if desbloqueado else "🔒"
            print(f" - {mundo.capitalize()}: {estado}")
        print("")
