# import json
# import os
# import cv2
# from modules.data_manager import cargar_data, guardar_data, sincronizar_usuario_y_game_state

# DATA_PATH = "data/luminia_data.json"

# # ----- CONFIGURACIÓN RECONOCIMIENTO FACIAL -----
# FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# class GameState:
#     """
#     Representa el estado global del juego Luminia.
#     Controla la fase actual, mundo activo, minijuego, y desbloqueos.
#     """

#     def __init__(self):
#         # Fase actual del juego (inicio, menu_principal, mundo_letras, jugando, etc.)
#         self.fase = "inicio"

#          # --- NUEVOS FLAGS DE CONTROL ---
#         self.intro_terminada = False       # Se pone en True cuando acaba el audio de introducción
#         self.microfono_listo = True        # Controla cuándo se puede usar el micro
#         self.esperando_voz = False         # Indica si se espera entrada por voz
#         self.usuario_actual = None  # Referencia al usuario logueado o registrado


#         # Nombre del mundo actual (letras, animales, etc.)
#         self.mundo_actual = None

#         # Minijuego actual dentro del mundo
#         self.minijuego_actual = None

#         # Estados desbloqueados (control de avance global)
#         self.mundos_desbloqueados = {
#             "letras": True,  
#             "animales": False,
#             "fruta_y_verdura": False,
#             "numeros": False,
#             "final": False,
#         }

#         # Datos del usuario asociados
#         self.usuario_data = {
#             "nombre": None,
#             "estrellas_totales": 0,
#             "mundos": {}
#         }

#         self.marcadores_castillos = {
#             1: "letras",
#             3: "animales",
#             4: "fruta_y_verdura",
#             6: "numeros",
#             11: "final"
#         }

#         # Instancias de mundos AR
#         self.instancia_mundo_letras = None
#         self.instancia_mundo_animales = None
#         self.instancia_mundo_numeros = None
#         self.instancia_mundo_fruta_y_verdura = None
#         self.instancia_mundo_final = None


#     # ----------------------------------------------------------
#     # ESTADO Y PROGRESO
#     # ----------------------------------------------------------
#     def sincronizar_con_usuario(self, usuario_data):
#         """
#         Sincroniza los datos del usuario. Respeta los mundos desbloqueados cargados desde JSON.
#         """
#         self.usuario_data["nombre"] = usuario_data.get("nombre")
#         self.usuario_data["estrellas_totales"] = usuario_data.get("estrellas_totales", 0)

#         # Si el usuario no tiene 'mundos', inicializamos para nuevo usuario
#         if "mundos" not in usuario_data:
#             self.mundos_desbloqueados = {
#                 "letras": True,
#                 "animales": False,
#                 "fruta_y_verdura": False,
#                 "numeros": False,
#                 "final": False,
#             }
#             self.usuario_data["mundos"] = {}
#         else:
#             # Usuario existente → respetamos mundos desbloqueados tal como vienen del JSON
#             self.mundos_desbloqueados = usuario_data.get("mundos_desbloqueados", self.mundos_desbloqueados)



#     def establecer_fase(self, nueva_fase, mundo=None, minijuego=None):
#         """
#         Cambia la fase actual del juego.
#         """
#         self.fase = nueva_fase
#         if mundo:
#             self.mundo_actual = mundo
#         if minijuego:
#             self.minijuego_actual = minijuego
#         print(f"🎮 Estado actualizado → Fase: {self.fase}, Mundo: {self.mundo_actual}, Minijuego: {self.minijuego_actual}")

#     def reiniciar(self):
#         """
#         Reinicia el estado global del juego a su configuración inicial.
#         """
#         self.__init__()
#         print("🔁 Estado global del juego reiniciado.")

#     # ----------------------------------------------------------
#     # APOYO AL GESTOR DE JUEGOS
#     # ----------------------------------------------------------
#     def mundo_desbloqueado(self, nombre_mundo: str) -> bool:
#         """
#         Indica si un mundo está desbloqueado.
#         """
#         return self.mundos_desbloqueados.get(nombre_mundo, False)

#     # def registrar_resultado(self, mundo, minijuego, estrellas):
#     #     """
#     #     Registra estrellas obtenidas en un minijuego, actualiza totales por mundo y global.
#     #     """
#     #     if "mundos" not in self.usuario_data:
#     #         self.usuario_data["mundos"] = {}

#     #     if mundo not in self.usuario_data["mundos"]:
#     #         self.usuario_data["mundos"][mundo] = {}

#     #     # Guardamos estrellas del minijuego (máx 3)
#     #     estrellas = min(max(int(estrellas), 0), 3)
#     #     self.usuario_data["mundos"][mundo][minijuego] = estrellas

#     #     # Calculamos total de estrellas del mundo
#     #     total_mundo = sum(
#     #         v for k, v in self.usuario_data["mundos"][mundo].items() if k != "total_estrellas"
#     #     )
#     #     self.usuario_data["mundos"][mundo]["total_estrellas"] = total_mundo

#     #     # Calculamos total global
#     #     total_global = sum(
#     #         m.get("total_estrellas", 0) for m in self.usuario_data["mundos"].values()
#     #     )
#     #     self.usuario_data["estrellas_totales"] = total_global

#     #     print(f"⭐ Progreso actualizado → Mundo '{mundo}': {total_mundo}⭐ | Total global: {total_global}⭐")
#     #     self._verificar_desbloqueos()
#     #     self.guardar()
#     #     # 🔄 Sincroniza el progreso con la sección de usuarios
#     #     sincronizar_usuario_y_game_state(self.usuario_data["nombre"])

#     def registrar_resultado(self, mundo, minijuego, estrellas):
#         """
#         Registra estrellas obtenidas en un minijuego, actualiza totales por mundo y global,
#         usando los mundos que ya existen en usuario_data.
#         """
#         if "mundos" not in self.usuario_data:
#             self.usuario_data["mundos"] = {}

#         # Si el mundo existe, usamos la estructura actual; si no, creamos una vacía
#         if mundo not in self.usuario_data["mundos"]:
#             self.usuario_data["mundos"][mundo] = {}

#         # Guardamos estrellas del minijuego (máx 3)
#         estrellas = min(max(int(estrellas), 0), 3)
#         self.usuario_data["mundos"][mundo][minijuego] = estrellas

#         # Calculamos total de estrellas del mundo
#         total_mundo = sum(
#             v for k, v in self.usuario_data["mundos"][mundo].items() if k != "total_estrellas"
#         )
#         self.usuario_data["mundos"][mundo]["total_estrellas"] = total_mundo

#         # Calculamos total global
#         total_global = sum(
#             m.get("total_estrellas", 0) for m in self.usuario_data["mundos"].values()
#         )
#         self.usuario_data["estrellas_totales"] = total_global

#         print(f"⭐ Progreso actualizado → Mundo '{mundo}': {total_mundo}⭐ | Total global: {total_global}⭐")

#         # Actualizamos desbloqueos
#         self._verificar_desbloqueos()

#         # Guardamos directamente en el JSON unificado bajo usuarios
#         from modules.data_manager import cargar_data, guardar_data  # ajusta según tu proyecto
#         data = cargar_data()
#         data["usuarios"][self.usuario_data["nombre"]] = self.usuario_data
#         guardar_data(data)




#     def obtener_progreso(self, mundo):
#         """
#         Devuelve el progreso guardado para un mundo.
#         """
#         # Cambiado de "progreso" a "mundos"
#         return self.usuario_data.get("mundos", {}).get(mundo, {})


#     def _verificar_desbloqueos(self):
#         """
#         Verifica si se han desbloqueado nuevos mundos tras ganar estrellas.
#         """
#         total = self.usuario_data["estrellas_totales"]
#         umbrales = {
#             "animales": 5,
#             "fruta_y_verdura": 10,
#             "numeros": 15,
#             "final": 20,
#         }

#         for mundo, estrellas_req in umbrales.items():
#             if total >= estrellas_req and not self.mundos_desbloqueados[mundo]:
#                 self.mundos_desbloqueados[mundo] = True
#                 print(f"🌟 ¡Nuevo mundo desbloqueado!: {mundo.capitalize()}")

#     # ----------------------------------------------------------
#     # PERSISTENCIA
#     # ----------------------------------------------------------
#     # def guardar(self):
#     #     """
#     #     Guarda el estado actual en data/game_state.json.
#     #     """
#     #     if not os.path.exists("data"):
#     #         os.makedirs("data")

#     #     datos = {
#     #         "fase": self.fase,
#     #         "mundo_actual": self.mundo_actual,
#     #         "minijuego_actual": self.minijuego_actual,
#     #         "mundos_desbloqueados": self.mundos_desbloqueados,
#     #         "usuario_data": self.usuario_data,
#     #     }

#     #     with open(DATA_PATH, "w", encoding="utf-8") as f:
#     #         json.dump(datos, f, ensure_ascii=False, indent=4)

#     #     print("💾 Estado global del juego guardado correctamente.")

#     # @classmethod
#     # def cargar(cls):
#     #     """
#     #     Carga el estado previo del juego si existe.
#     #     Respeta los mundos desbloqueados almacenados en el JSON del usuario.
#     #     """
#     #     if not os.path.exists(DATA_PATH):
#     #         print("⚠️ No se encontró un estado previo. Se iniciará uno nuevo.")
#     #         return cls()

#     #     with open(DATA_PATH, "r", encoding="utf-8") as f:
#     #         try:
#     #             datos = json.load(f)
#     #         except json.JSONDecodeError:
#     #             print("⚠️ Archivo de estado corrupto. Se generará uno nuevo.")
#     #             return cls()

#     #     gs = cls()
#     #     gs.fase = datos.get("fase", "inicio")
#     #     gs.mundo_actual = datos.get("mundo_actual")
#     #     gs.minijuego_actual = datos.get("minijuego_actual")
#     #     gs.usuario_data = datos.get("usuario_data", gs.usuario_data)

#     #     # 🔹 Si existe clave 'mundos_desbloqueados' en el JSON, la usamos
#     #     gs.mundos_desbloqueados = datos.get("mundos_desbloqueados", gs.mundos_desbloqueados)

#     #     # 🔹 Aseguramos que siempre exista la clave 'progreso' (compatibilidad retroactiva)
#     #     if "progreso" not in gs.usuario_data:
#     #         gs.usuario_data["progreso"] = {}

#     #     print(f"🔄 Estado global cargado: Fase={gs.fase}, Mundo={gs.mundo_actual}, Minijuego={gs.minijuego_actual}")
#     #     return gs

#     def guardar(self):
#         data = cargar_data()
#         data["game_state"] = {
#             "fase": self.fase,
#             "mundo_actual": self.mundo_actual,
#             "minijuego_actual": self.minijuego_actual,
#             "mundos_desbloqueados": self.mundos_desbloqueados,
#             "usuario_data": self.usuario_data,
#         }
#         guardar_data(data)
#         print("💾 GameState guardado dentro de luminia_data.json")

#     @classmethod
#     def cargar(cls):
#         data = cargar_data()
#         gs_data = data.get("game_state", {})
#         gs = cls()
#         gs.fase = gs_data.get("fase", "inicio")
#         gs.mundo_actual = gs_data.get("mundo_actual")
#         gs.minijuego_actual = gs_data.get("minijuego_actual")
#         gs.mundos_desbloqueados = gs_data.get("mundos_desbloqueados", gs.mundos_desbloqueados)
#         gs.usuario_data = gs_data.get("usuario_data", gs.usuario_data)
#         return gs
    
#     # ----------------------------------------------------------
#     # INFORMACIÓN
#     # ----------------------------------------------------------
#     def mostrar_estado(self):
#         """
#         Muestra un resumen legible del estado actual del juego.
#         """
#         print("\n🎯 ESTADO ACTUAL DE LUMINIA")
#         print(f"Fase actual: {self.fase}")
#         print(f"Mundo actual: {self.mundo_actual or 'Ninguno'}")
#         print(f"Minijuego actual: {self.minijuego_actual or 'Ninguno'}")
#         print("Mundos desbloqueados:")
#         for mundo, desbloqueado in self.mundos_desbloqueados.items():
#             estado = "✅" if desbloqueado else "🔒"
#             print(f" - {mundo.capitalize()}: {estado}")
#         print("")


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
        #self.sesion_iniciada = False
        self.mundos_desbloqueados = {
            "letras": True, "animales": False, "fruta_y_verdura": False, "numeros": False, "final": False,
        }
        self.usuario_data = {}  # Dict del documento del usuario
        self.marcadores_castillos = {
            1: "letras",
            3: "animales",
            4: "fruta_y_verdura",
            6: "numeros",
            11: "final"
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
            self.fase = datos.get("fase", "menu_principal") 

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
        estrellas = min(max(int(estrellas), 0), 3)
        self.usuario_data["mundos"][mundo][minijuego] = estrellas
        total_mundo = sum(v for k, v in self.usuario_data["mundos"][mundo].items() if k != "total_estrellas")
        self.usuario_data["mundos"][mundo]["total_estrellas"] = total_mundo
        total_global = sum(m.get("total_estrellas", 0) for m in self.usuario_data["mundos"].values())
        self.usuario_data["estrellas_totales"] = total_global
        self._verificar_desbloqueos()
        self.guardar()

    def _verificar_desbloqueos(self):
        umbrales = {"letras": 0, "animales": 3, "fruta_y_verdura": 6, "numeros": 9, "final": 12}  # Ajusta según tu lógica
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
            # 🔹 Guardamos en MongoDB usando update_one con $set (no borra datos antiguos)
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