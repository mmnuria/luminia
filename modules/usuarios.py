import numpy as np
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from modules.data_manager import MongoDBManager  

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

mongo = MongoDBManager() 

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
            "letras": True,
            "animales": False,
            "frutas_verduras": False,
            "numeros": False,
            "final": False
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
