# import json
# import os
# import numpy as np
# from datetime import datetime
# from sklearn.metrics.pairwise import cosine_similarity
# from modules.data_manager import cargar_data, guardar_data

# # ------------------------------------------------------------------
# # CONFIGURACIÓN GLOBAL
# # ------------------------------------------------------------------
# DATA_PATH = "data/luminia_data.json"
# UMBRAL_SIMILITUD = 0.92
# LUMIOS_POR_ESTRELLA = 10
# COSTE_DISFRAZ = 12  # Lumios por disfraz

# MUNDOS_BASE = {
#     "mundo_letras": {"adivina": 0, "memoria": 0, "secuencia": 0},
#     "mundo_animales": {"adivina": 0, "sonido": 0, "clasificar": 0},
#     "mundo_frutas_verduras": {"adivina": 0, "color": 0, "clasifica": 0},
#     "mundo_numeros": {"adivina": 0, "suma": 0, "mayor": 0},
#     "mundo_final": {"contar": 0, "secuencia": 0, "deletreo": 0},
# }

# MUNDOS_DESBLOQUEO = {
#     "mundo_letras": 0,
#     "mundo_animales": 3,
#     "mundo_frutas_verduras": 6,
#     "mundo_numeros": 9,
#     "mundo_final": 12,
# }

# # ------------------------------------------------------------------
# # UTILIDADES DE FICHEROS
# # ------------------------------------------------------------------
# def _asegurar_directorio():
#     if not os.path.exists("data"):
#         os.makedirs("data")

# def cargar_usuarios():
#     data = cargar_data()
#     return data.get("usuarios", {})

# def guardar_usuarios(usuarios):
#     data = cargar_data()
#     data["usuarios"] = usuarios
#     guardar_data(data)

# # ------------------------------------------------------------------
# # FUNCIONES DE GESTIÓN DE USUARIOS
# # ------------------------------------------------------------------
# def registrar_usuario(nombre, idioma="es", vector_facial=None):
#     usuarios = cargar_usuarios()
#     key = nombre.lower()
#     if key not in usuarios:
#         mundos = {m: {**minijuegos, "total_estrellas": 0} for m, minijuegos in MUNDOS_BASE.items()}
#         usuarios[key] = {
#             "nombre": nombre,
#             "idioma": idioma,
#             "vector_facial": vector_facial,
#             "fecha_registro": datetime.now().isoformat(),
#             "mundos": mundos,
#             "estrellas_totales": 0,
#             "lumios": 0,
#             "disfraces": {"disponibles": ["tina_unicornio"], "equipado": "tina_unicornio"},
#             "mundo_actual": "mundo_letras",
#             "minijuego_actual": "memoria",
#             "mundos_desbloqueados": {m: m in ["mundo_letras", "mundo_animales"] for m in MUNDOS_BASE}
#         }
#         guardar_usuarios(usuarios)
#     return usuarios[key]

# def verificar_usuario_existe(nombre):
#     return nombre.lower() in cargar_usuarios()

# def obtener_usuario(nombre):
#     return cargar_usuarios().get(nombre.lower())

# def actualizar_nombre_usuario(nombre_actual, nuevo_nombre):
#     usuarios = cargar_usuarios()
#     key_actual = nombre_actual.lower()
#     key_nuevo = nuevo_nombre.lower()
#     if key_actual not in usuarios or key_nuevo in usuarios:
#         return False
#     usuarios[key_nuevo] = usuarios.pop(key_actual)
#     usuarios[key_nuevo]["nombre"] = nuevo_nombre
#     guardar_usuarios(usuarios)
#     return True

# def actualizar_idioma_usuario(nombre, nuevo_idioma):
#     usuarios = cargar_usuarios()
#     key = nombre.lower()
#     if key not in usuarios:
#         return False
#     usuarios[key]["idioma"] = nuevo_idioma
#     usuarios[key]["fecha_actualizacion_idioma"] = datetime.now().isoformat()
#     guardar_usuarios(usuarios)
#     return True

# # ------------------------------------------------------------------
# # FUNCIONES DE RECONOCIMIENTO FACIAL
# # ------------------------------------------------------------------
# def comparar_vectores_faciales(v1, v2):
#     try:
#         if v1 is None or v2 is None:
#             return 0.0
#         v1 = np.array(v1).reshape(1, -1)
#         v2 = np.array(v2).reshape(1, -1)
#         return float(cosine_similarity(v1, v2)[0][0])
#     except Exception:
#         return 0.0

# def buscar_usuario_por_cara(vector_facial):
#     usuarios = cargar_usuarios()
#     mejor_similitud = 0
#     mejor_usuario = None
#     for nombre, datos in usuarios.items():
#         if "vector_facial" in datos and datos["vector_facial"] is not None:
#             similitud = comparar_vectores_faciales(vector_facial, datos["vector_facial"])
#             if similitud > mejor_similitud and similitud >= UMBRAL_SIMILITUD:
#                 mejor_usuario = datos
#                 mejor_similitud = similitud
#     if mejor_usuario:
#         return mejor_usuario["nombre"], mejor_usuario
#     return None, None

# def actualizar_vector_facial(nombre, vector_facial):
#     usuarios = cargar_usuarios()
#     key = nombre.lower()
#     if key not in usuarios:
#         return False
#     usuarios[key]["vector_facial"] = vector_facial
#     usuarios[key]["fecha_actualizacion_facial"] = datetime.now().isoformat()
#     guardar_usuarios(usuarios)
#     return True

# def eliminar_vector_facial(nombre):
#     usuarios = cargar_usuarios()
#     key = nombre.lower()
#     if key in usuarios and "vector_facial" in usuarios[key]:
#         del usuarios[key]["vector_facial"]
#         usuarios[key]["fecha_eliminacion_facial"] = datetime.now().isoformat()
#         guardar_usuarios(usuarios)
#         return True
#     return False

# # ------------------------------------------------------------------
# # CLASE USUARIO
# # ------------------------------------------------------------------
# class Usuario:
#     def __init__(self, nombre="Invitado", idioma="es", vector_facial=None):
#         self.nombre = nombre
#         self.idioma = idioma
#         self.vector_facial = vector_facial
#         self.fecha_registro = datetime.now().isoformat()
#         self.mundos = {m: {**minijuegos, "total_estrellas": 0} for m, minijuegos in MUNDOS_BASE.items()}
#         self.estrellas_totales = 0
#         self.lumios = 0
#         self.disfraces = {"disponibles": ["tina_unicornio"], "equipado": "tina_unicornio"}
#         self.mundo_actual = "mundo_letras"
#         self.minijuego_actual = "memoria"
#         self.mundos_desbloqueados = {m: m in ["mundo_letras", "mundo_animales"] for m in MUNDOS_BASE}

#     # ---------------------------
#     # Gestión de estrellas y lumios
#     # ---------------------------
#     def agregar_estrellas(self, mundo, minijuego, estrellas_nuevas):
#         estrellas_nuevas = max(0, min(int(round(estrellas_nuevas)), 3))
#         if mundo not in self.mundos or minijuego not in self.mundos[mundo]:
#             return
#         prev = self.mundos[mundo][minijuego]
#         media = (prev + estrellas_nuevas) / 2
#         self.mundos[mundo][minijuego] = min(media, 3)
#         self.lumios += estrellas_nuevas * LUMIOS_POR_ESTRELLA
#         self._actualizar_totales()
#         self._actualizar_desbloqueos()
#         self.guardar_progreso()

#     def _actualizar_totales(self):
#         total = 0
#         for mundo, datos in self.mundos.items():
#             suma = sum(v for k, v in datos.items() if k != "total_estrellas")
#             self.mundos[mundo]["total_estrellas"] = suma
#             total += suma
#         self.estrellas_totales = total

#     def _actualizar_desbloqueos(self):
#         for mundo, umbral in MUNDOS_DESBLOQUEO.items():
#             self.mundos_desbloqueados[mundo] = self.estrellas_totales >= umbral

#     # ---------------------------
#     # Gestión de disfraces
#     # ---------------------------
#     def comprar_disfraz(self, nombre_disfraz):
#         if nombre_disfraz in self.disfraces["disponibles"]:
#             return False
#         if self.lumios >= COSTE_DISFRAZ:
#             self.lumios -= COSTE_DISFRAZ
#             self.disfraces["disponibles"].append(nombre_disfraz)
#             self.guardar_progreso()
#             return True
#         return False

#     def equipar_disfraz(self, nombre_disfraz):
#         if nombre_disfraz in self.disfraces["disponibles"]:
#             self.disfraces["equipado"] = nombre_disfraz
#             self.guardar_progreso()
#             return True
#         return False

#     # ---------------------------
#     # Guardar y cargar progreso
#     # ---------------------------
#     def guardar_progreso(self):
#         usuarios = cargar_usuarios()
#         usuarios[self.nombre.lower()] = self._serializar()
#         guardar_usuarios(usuarios)

#     @classmethod
#     def cargar_progreso(cls, nombre):
#         usuarios = cargar_usuarios()
#         key = nombre.lower()
#         if key not in usuarios:
#             return cls(nombre)
#         datos = usuarios[key]
#         u = cls(nombre=datos.get("nombre", nombre), idioma=datos.get("idioma", "es"),
#                 vector_facial=datos.get("vector_facial"))
#         u.fecha_registro = datos.get("fecha_registro", datetime.now().isoformat())
#         u.mundos = datos.get("mundos", u.mundos)
#         u.estrellas_totales = datos.get("estrellas_totales", 0)
#         u.lumios = datos.get("lumios", 0)
#         u.disfraces = datos.get("disfraces", u.disfraces)
#         u.mundo_actual = datos.get("mundo_actual", "mundo_letras")
#         u.minijuego_actual = datos.get("minijuego_actual", "memoria")
#         u.mundos_desbloqueados = datos.get("mundos_desbloqueados", u.mundos_desbloqueados)
#         return u

#     def _serializar(self):
#         return {
#             "nombre": self.nombre,
#             "idioma": self.idioma,
#             "vector_facial": self.vector_facial,
#             "fecha_registro": self.fecha_registro,
#             "mundos": self.mundos,
#             "estrellas_totales": self.estrellas_totales,
#             "lumios": self.lumios,
#             "disfraces": self.disfraces,
#             "mundo_actual": self.mundo_actual,
#             "minijuego_actual": self.minijuego_actual,
#             "mundos_desbloqueados": self.mundos_desbloqueados
#         }

#     # ---------------------------
#     # Cambiar usuario e idioma
#     # ---------------------------
#     def actualizar_nombre_usuario(self, nuevo_nombre):
#         usuarios = cargar_usuarios()
#         key_actual = self.nombre.lower()
#         key_nuevo = nuevo_nombre.lower()
#         if key_nuevo in usuarios:
#             return False
#         usuarios[key_nuevo] = usuarios.pop(key_actual)
#         self.nombre = nuevo_nombre
#         guardar_usuarios(usuarios)
#         return True

#     def actualizar_idioma_usuario(self, nuevo_idioma):
#         self.idioma = nuevo_idioma
#         self.guardar_progreso()
#         return True

import numpy as np
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from modules.data_manager import MongoDBManager  # Importa el manager

# ------------------------------------------------------------------
# CONFIGURACIÓN GLOBAL
# ------------------------------------------------------------------
UMBRAL_SIMILITUD = 0.92
LUMIOS_POR_ESTRELLA = 10
COSTE_DISFRAZ = 12  # Lumios por disfraz

MUNDOS_BASE = {
    "letras": {"adivina": 0, "memoria": 0, "secuencia": 0, "total_estrellas": 0},
    "animales": {"adivina": 0, "sonido": 0, "clasificar": 0, "total_estrellas": 0},
    "frutas_verduras": {"adivina": 0, "color": 0, "clasifica": 0, "total_estrellas": 0},
    "numeros": {"adivina": 0, "suma": 0, "mayor": 0, "total_estrellas": 0},
    "final": {"contar": 0, "secuencia": 0, "deletreo": 0, "total_estrellas": 0},
}

MUNDOS_DESBLOQUEO = {
    "letras": 0,
    "animales": 3,
    "frutas_verduras": 6,
    "numeros": 9,
    "final": 12,
}

mongo = MongoDBManager()  # Singleton, se conectará cuando llames a conectar()

# ------------------------------------------------------------------
# FUNCIONES DE GESTIÓN DE USUARIOS
# ------------------------------------------------------------------
def registrar_usuario(nombre, idioma="es", vector_facial=None):
    datos = {
        "nombre": nombre,
        "idioma": idioma,
        "vector_facial": vector_facial,
        "fecha_registro": datetime.now().isoformat(),
        "mundos": MUNDOS_BASE,
        "estrellas_totales": 0,
        "lumios": 0,
        "disfraces": {"disponibles": ["tina_unicornio"], "equipado": "tina_unicornio"},
        "mundo_actual": "letras",
        "minijuego_actual": "memoria",
        "mundos_desbloqueados": {
            "mundo_letras": True,
            "mundo_animales": False,
            "mundo_frutas_verduras": False,
            "mundo_numeros": False,
            "mundo_final": False
        }
    }
    return mongo.crear_usuario(datos)

def verificar_usuario_existe(nombre):
    return mongo.encontrar_usuario(nombre) is not None

def obtener_usuario(nombre):
    return mongo.encontrar_usuario(nombre)

def actualizar_nombre_usuario(nombre_actual, nuevo_nombre):
    datos = {"nombre": nuevo_nombre}
    if mongo.actualizar_usuario(nombre_actual, datos):
        # Actualizar _id también (renombrar documento)
        usuario = mongo.encontrar_usuario(nombre_actual)
        if usuario:
            usuario["_id"] = nuevo_nombre.lower()
            mongo.eliminar_usuario(nombre_actual)
            mongo.collection.insert_one(usuario)
            return True
    return False

def actualizar_idioma_usuario(nombre, nuevo_idioma):
    return mongo.actualizar_usuario(nombre, {"idioma": nuevo_idioma})

# ------------------------------------------------------------------
# FUNCIONES DE RECONOCIMIENTO FACIAL
# ------------------------------------------------------------------
def comparar_vectores_faciales(v1, v2):
    try:
        if v1 is None or v2 is None:
            return 0.0
        v1 = np.array(v1).reshape(1, -1)
        v2 = np.array(v2).reshape(1, -1)
        return float(cosine_similarity(v1, v2)[0][0])
    except Exception:
        return 0.0

def buscar_usuario_por_cara(vector_facial):
    """Busca un usuario por vector facial en MongoDB."""
    try:
        mongo.asegurar_conexion()  # Asegurar conexión antes de la consulta
        mejor_similitud = 0
        mejor_usuario = None
        for usuario in mongo.collection.find({"vector_facial": {"$ne": None}}):
            similitud = comparar_vectores_faciales(vector_facial, usuario.get("vector_facial"))
            if similitud > mejor_similitud and similitud >= UMBRAL_SIMILITUD:
                mejor_usuario = usuario
                mejor_similitud = similitud
        if mejor_usuario:
            return mejor_usuario["nombre"], mejor_usuario
        return None, None
    except Exception as e:
        print(f"Error al buscar usuario por cara: {e}")
        return None, None

def verificar_usuario_existe(nombre):
    """Verifica si un usuario existe en MongoDB."""
    try:
        return mongo.encontrar_usuario(nombre) is not None
    except Exception as e:
        print(f"Error al verificar usuario existente: {e}")
        return False
def actualizar_vector_facial(nombre, vector_facial):
    return mongo.actualizar_usuario(nombre, {"vector_facial": vector_facial})

def eliminar_vector_facial(nombre):
    return mongo.actualizar_usuario(nombre, {"vector_facial": {"$unset": ""}})

# ------------------------------------------------------------------
# CLASE USUARIO
# ------------------------------------------------------------------
class Usuario:
    def __init__(self, datos):
        self.datos = datos  # Almacena todo el dict del documento

    @property
    def nombre(self):
        return self.datos["nombre"]

    @property
    def estrellas_totales(self):
        return self.datos["estrellas_totales"]
    
    @property
    def lumios(self):
        return self.datos["lumios"]

    # ... (agrega propiedades para otros campos similares)

    def agregar_estrellas(self, mundo, minijuego, estrellas_nuevas):
        estrellas_nuevas = max(0, min(int(round(estrellas_nuevas)), 3))
        if mundo not in self.datos["mundos"] or minijuego not in self.datos["mundos"][mundo]:
            return
        prev = self.datos["mundos"][mundo][minijuego]
        media = (prev + estrellas_nuevas) / 2
        self.datos["mundos"][mundo][minijuego] = min(media, 3)
        self.datos["lumios"] += estrellas_nuevas * LUMIOS_POR_ESTRELLA
        self._actualizar_totales()
        self._actualizar_desbloqueos()
        self.guardar_progreso()

    def _actualizar_totales(self):
        total = 0
        for mundo, datos_mundo in self.datos["mundos"].items():
            suma = sum(v for k, v in datos_mundo.items() if k != "total_estrellas")
            self.datos["mundos"][mundo]["total_estrellas"] = suma
            total += suma
        self.datos["estrellas_totales"] = total

    def _actualizar_desbloqueos(self):
        for mundo, umbral in MUNDOS_DESBLOQUEO.items():
            self.datos["mundos_desbloqueados"][mundo] = self.datos["estrellas_totales"] >= umbral

    def comprar_disfraz(self, nombre_disfraz):
        if nombre_disfraz in self.datos["disfraces"]["disponibles"]:
            return False
        if self.datos["lumios"] >= COSTE_DISFRAZ:
            self.datos["lumios"] -= COSTE_DISFRAZ
            self.datos["disfraces"]["disponibles"].append(nombre_disfraz)
            self.guardar_progreso()
            return True
        return False

    def equipar_disfraz(self, nombre_disfraz):
        if nombre_disfraz in self.datos["disfraces"]["disponibles"]:
            self.datos["disfraces"]["equipado"] = nombre_disfraz
            self.guardar_progreso()
            return True
        return False

    def guardar_progreso(self):
        mongo.actualizar_usuario(self.nombre, self.datos)

    @classmethod
    def cargar_progreso(cls, nombre):
        datos = obtener_usuario(nombre)
        if not datos:
            # Crear si no existe? O retornar None
            return None
        return cls(datos)

    # ... (otros métodos como actualizar_nombre_usuario, etc., usan mongo.actualizar_usuario)