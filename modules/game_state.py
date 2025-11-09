import cv2
from modules.data_manager import MongoDBManager

FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

mongo = MongoDBManager()

class GameState:
    def __init__(self):
        self.fase = "inicio"
        self.intro_terminada = False
        self.microfono_listo = True
        self.esperando_voz = False
        self.usuario_actual = None  # Nombre del usuario logueado
        self.mundo_actual = None
        self.minijuego_actual = None
        self.mensaje_pantalla = None
        self.tiempo_mensaje = 0
        self.mundos_desbloqueados = {
            "letras": True, "animales": False, "fruta_y_verdura": False, "numeros": False, "final": False,
        }
        self.usuario_data = {}  # Dict del documento del usuario
        self.marcadores_castillos = {
            1: "letras",
            4: "animales",
            6: "fruta_y_verdura",
            9: "numeros",
            12: "final"
        }

    def sincronizar_con_usuario(self, nombre_usuario):
        datos = mongo.encontrar_usuario(nombre_usuario)
        if datos:
            print(f"[GameState] Sincronizando datos de {nombre_usuario}")
            self.usuario_actual = nombre_usuario  # Mantenerlo como string
            self.usuario_data = datos
            self.mundos_desbloqueados = datos.get("mundos_desbloqueados", self.mundos_desbloqueados)
            self.mundo_actual = datos.get("mundo_actual")
            self.minijuego_actual = datos.get("minijuego_actual")

    def establecer_fase(self, nueva_fase, mundo=None, minijuego=None):
        self.fase = nueva_fase
        if mundo:
            self.mundo_actual = mundo
        if minijuego:
            self.minijuego_actual = minijuego
        self.guardar()  # Persiste cambios

    def registrar_resultado(self, mundo, minijuego, estrellas):
        if not self.usuario_data:
            print("No hay usuario logueado")
            return

        # Asegurar rango de estrellas entre 0 y 3
        estrellas = min(max(int(estrellas), 0), 3)

        # --- otorgar lumios siempre por las estrellas de esta ronda ---
        lumios_ganados = estrellas * 10
        if "lumios" not in self.usuario_data:
            self.usuario_data["lumios"] = 0
        self.usuario_data["lumios"] += lumios_ganados
        print(f"💡 Has ganado {lumios_ganados} lumios ({self.usuario_data['lumios']} en total).")

        # --- MANTENER el sistema de progreso de estrellas ---
        estrellas_previas = self.usuario_data["mundos"][mundo].get(minijuego, 0)
        # Solo actualizar si mejora la marca anterior
        if estrellas > estrellas_previas:
            self.usuario_data["mundos"][mundo][minijuego] = estrellas

            # Recalcular totales de estrellas
            total_mundo = sum(v for k, v in self.usuario_data["mundos"][mundo].items() if k != "total_estrellas")
            self.usuario_data["mundos"][mundo]["total_estrellas"] = total_mundo
            total_global = sum(m.get("total_estrellas", 0) for m in self.usuario_data["mundos"].values())
            self.usuario_data["estrellas_totales"] = total_global

        # Verificar desbloqueos y guardar progreso
        self._verificar_desbloqueos()
        self.guardar()


    def _verificar_desbloqueos(self):
        umbrales = {"letras": 0, "animales": 3, "fruta_y_verdura": 6, "numeros": 9, "final": 12} 
        for mundo, estrellas_req in umbrales.items():
            if self.usuario_data["estrellas_totales"] >= estrellas_req:
                self.mundos_desbloqueados[mundo] = True
        self.usuario_data["mundos_desbloqueados"] = self.mundos_desbloqueados

    def guardar(self):
        """
        Guarda TODO el estado actual del usuario en MongoDB.
        Sincroniza progreso, desbloqueos, lumios, disfraces, idioma, etc.
        """
        if not self.usuario_actual:
            print("⚠️ No hay usuario logueado, no se puede guardar el estado.")
            return False

        # --- Actualizamos en memoria los campos que cambian dinámicamente ---
        self.usuario_data.update({
            "fase": self.fase,
            "mundo_actual": self.mundo_actual,
            "minijuego_actual": self.minijuego_actual,
            "mundos_desbloqueados": self.mundos_desbloqueados,
        })

        # Si el usuario tiene mundos definidos, recalculamos las estrellas totales
        if "mundos" in self.usuario_data:
            total_global = sum(
                m.get("total_estrellas", 0)
                for m in self.usuario_data["mundos"].values()
                if isinstance(m, dict)
            )
            self.usuario_data["estrellas_totales"] = total_global

        # --- Aseguramos que haya campos por defecto si no existen ---
        self.usuario_data.setdefault("lumios", 0)
        self.usuario_data.setdefault("idioma", "es")
        self.usuario_data.setdefault("disfraces", {"disponibles": ["tina_unicornio"], "equipado": "tina_unicornio"})
        self.usuario_data.setdefault("fecha_registro", None)
        self.usuario_data.setdefault("vector_facial", [])
        self.usuario_data.setdefault("nombre", self.usuario_actual)

        try:
            # Guardamos en MongoDB usando update_one con $set (no borra datos antiguos)
            mongo.actualizar_usuario(self.usuario_actual, self.usuario_data)
            print(f"💾 Estado COMPLETO guardado correctamente para {self.usuario_actual}")
            return True
        except Exception as e:
            print(f"❌ Error al guardar estado completo del usuario {self.usuario_actual}: {e}")
            return False

    @classmethod
    def cargar(cls, nombre_usuario):
        gs = cls()
        gs.sincronizar_con_usuario(nombre_usuario)
        return gs

    def obtener_progreso(self, mundo):
        """
        Devuelve el progreso guardado para un mundo.
        """
        # Cambiado de "progreso" a "mundos"
        return self.usuario_data.get("mundos", {}).get(mundo, {})