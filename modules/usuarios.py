import json
import os
import numpy as np
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity

# ------------------------------------------------------------------
# CONFIGURACIÓN GLOBAL
# ------------------------------------------------------------------
DATA_PATH = "data/usuarios.json"
UMBRAL_SIMILITUD = 0.92

# Estructura base de mundos y minijuegos
MUNDOS_BASE = {
    "mundo_letras": {"adivina": 0, "memoria": 0, "secuencia": 0},
    "mundo_animales": {"adivina": 0, "sonido": 0, "clasificacion": 0},
    "mundo_frutas_verduras": {"adivina": 0, "color": 0, "clasifica": 0},
    "mundo_numeros": {"contar": 0, "suma": 0, "mayor": 0},
    "mundo_final": {"reto": 0, "secuencia": 0, "desafio_final": 0},
}

# ------------------------------------------------------------------
# FUNCIONES DE UTILIDAD GENERAL
# ------------------------------------------------------------------

def _asegurar_directorio():
    if not os.path.exists("data"):
        os.makedirs("data")

def cargar_usuarios():
    _asegurar_directorio()
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def guardar_usuarios(data):
    _asegurar_directorio()
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ------------------------------------------------------------------
# FUNCIONES DE GESTIÓN DE USUARIOS
# ------------------------------------------------------------------

def registrar_usuario(nombre, idioma="es", vector_facial=None):
    usuarios = cargar_usuarios()
    key = nombre.lower()

    if key not in usuarios:
        # Crear estructura base de mundos con totales
        mundos = {
            mundo: {**minijuegos, "total_estrellas": 0}
            for mundo, minijuegos in MUNDOS_BASE.items()
        }

        usuarios[key] = {
            "nombre": nombre,
            "idioma": idioma,
            "vector_facial": vector_facial,
            "fecha_registro": datetime.now().isoformat(),
            "mundos": mundos,
            "estrellas_totales": 0,
        }

        guardar_usuarios(usuarios)
        print(f"✅ Usuario '{nombre}' registrado correctamente.")
    return usuarios[key]

def obtener_usuario(nombre):
    return cargar_usuarios().get(nombre.lower())

def verificar_usuario_existe(nombre):
    return nombre.lower() in cargar_usuarios()

def actualizar_usuario(nombre_actual, nuevo_nombre=None, nuevo_idioma=None):
    usuarios = cargar_usuarios()
    key_actual = nombre_actual.lower()

    if key_actual not in usuarios:
        print(f"❌ El usuario '{nombre_actual}' no existe.")
        return False

    usuario = usuarios[key_actual]

    # Actualizar nombre
    if nuevo_nombre:
        key_nuevo = nuevo_nombre.lower()
        if key_nuevo in usuarios:
            print(f"⚠️ Ya existe un usuario con el nombre '{nuevo_nombre}'.")
            return False
        usuarios[key_nuevo] = usuario
        del usuarios[key_actual]
        usuario = usuarios[key_nuevo]
        usuario["nombre"] = nuevo_nombre
        key_actual = key_nuevo  
    else:
        nuevo_nombre = nombre_actual

    # Actualizar idioma
    if nuevo_idioma:
        usuario["idioma"] = nuevo_idioma
        usuario["fecha_actualizacion_idioma"] = datetime.now().isoformat()

    guardar_usuarios(usuarios)
    print(f"✅ Usuario '{nuevo_nombre}' actualizado correctamente.")
    return True


def actualizar_nombre_usuario(nombre_anterior, nombre_nuevo):
    """Cambia el nombre del usuario manteniendo su progreso."""
    return actualizar_usuario(nombre_actual=nombre_anterior, nuevo_nombre=nombre_nuevo)


def actualizar_idioma_usuario(nombre_usuario, nuevo_idioma):
    """Cambia el idioma del usuario sin afectar su progreso."""
    return actualizar_usuario(nombre_actual=nombre_usuario, nuevo_idioma=nuevo_idioma)

# ------------------------------------------------------------------
# RECONOCIMIENTO FACIAL
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
    usuarios = cargar_usuarios()
    mejor_similitud = 0
    mejor_usuario = None

    for nombre, datos in usuarios.items():
        if "vector_facial" in datos and datos["vector_facial"] is not None:
            similitud = comparar_vectores_faciales(vector_facial, datos["vector_facial"])
            print(f"Similitud con {nombre}: {similitud:.3f}")
            if similitud > mejor_similitud and similitud >= UMBRAL_SIMILITUD:
                mejor_usuario = datos
                mejor_similitud = similitud

    if mejor_usuario:
        print(f"✅ Usuario reconocido: {mejor_usuario['nombre']} ({mejor_similitud:.3f})")
        return mejor_usuario["nombre"], mejor_usuario
    else:
        print("❌ No se encontró coincidencia facial.")
        return None, None

def actualizar_vector_facial(nombre, vector_facial):
    usuarios = cargar_usuarios()
    key = nombre.lower()
    if key not in usuarios:
        print(f"❌ Usuario '{nombre}' no encontrado.")
        return False

    usuarios[key]["vector_facial"] = vector_facial
    usuarios[key]["fecha_actualizacion_facial"] = datetime.now().isoformat()
    guardar_usuarios(usuarios)
    print(f"✅ Vector facial actualizado para {nombre}")
    return True

def eliminar_vector_facial(nombre):
    usuarios = cargar_usuarios()
    key = nombre.lower()
    if key in usuarios and "vector_facial" in usuarios[key]:
        del usuarios[key]["vector_facial"]
        usuarios[key]["fecha_eliminacion_facial"] = datetime.now().isoformat()
        guardar_usuarios(usuarios)
        print(f"✅ Vector facial eliminado para {nombre}")
        return True
    print(f"⚠️ Usuario '{nombre}' no tiene vector facial.")
    return False

# ------------------------------------------------------------------
# CLASE USUARIO
# ------------------------------------------------------------------

class Usuario:
    """
    Representa un jugador con progreso por mundos y minijuegos.
    Gestiona guardado, carga y reconocimiento facial.
    """

    def __init__(self, nombre="Invitado", idioma="es", vector_facial=None):
        self.nombre = nombre
        self.idioma = idioma
        self.vector_facial = vector_facial
        self.fecha_registro = datetime.now().isoformat()

        # Copia base de mundos
        self.mundos = {
            mundo: {**minijuegos, "total_estrellas": 0}
            for mundo, minijuegos in MUNDOS_BASE.items()
        }

        self.estrellas_totales = 0
        print(f"👤 Usuario '{self.nombre}' inicializado.")

    # ----------------------------------------------------------
    # GESTIÓN DE PROGRESO
    # ----------------------------------------------------------
    def agregar_estrellas(self, mundo, minijuego, cantidad):
        usuarios = cargar_usuarios()
        key = self.nombre.lower()

        if mundo not in self.mundos:
            print(f"⚠️ Mundo '{mundo}' no existe.")
            return

        if minijuego not in self.mundos[mundo]:
            print(f"⚠️ Minijuego '{minijuego}' no pertenece a '{mundo}'.")
            return

        cantidad = max(0, min(int(round(cantidad)), 3))
        estrellas_previas = self.mundos[mundo][minijuego]

        if cantidad > estrellas_previas:
            self.mundos[mundo][minijuego] = cantidad
            print(f"🌟 Nuevo récord en {mundo}-{minijuego}: {cantidad} estrellas")
        else:
            print(f"➡️ Ya tenías {estrellas_previas} estrellas en {mundo}-{minijuego}")

        # Actualizar totales
        self._actualizar_totales()

        # Guardar al JSON
        usuarios[key] = self._serializar()
        guardar_usuarios(usuarios)

    def _actualizar_totales(self):
        total = 0
        for mundo, datos in self.mundos.items():
            suma = sum(v for k, v in datos.items() if k != "total_estrellas")
            self.mundos[mundo]["total_estrellas"] = suma
            total += suma
        self.estrellas_totales = total

    # ----------------------------------------------------------
    # GUARDADO / CARGA
    # ----------------------------------------------------------
    def guardar_progreso(self):
        usuarios = cargar_usuarios()
        usuarios[self.nombre.lower()] = self._serializar()
        guardar_usuarios(usuarios)
        print(f"💾 Progreso guardado de '{self.nombre}' ({self.estrellas_totales}⭐)")

    @classmethod
    def cargar_progreso(cls, nombre="Invitado", vector_facial=None):
        usuarios = cargar_usuarios()
        key = nombre.lower()
        if key not in usuarios:
            print(f"🆕 Usuario nuevo: {nombre}")
            return cls(nombre, vector_facial=vector_facial)

        datos = usuarios[key]
        u = cls(nombre=datos.get("nombre", nombre), idioma=datos.get("idioma", "es"),
                vector_facial=datos.get("vector_facial"))
        u.fecha_registro = datos.get("fecha_registro", datetime.now().isoformat())
        u.mundos = datos.get("mundos", u.mundos)
        u.estrellas_totales = datos.get("estrellas_totales", 0)
        print(f"🔄 Progreso cargado para '{u.nombre}' ({u.estrellas_totales}⭐)")
        return u

    def _serializar(self):
        return {
            "nombre": self.nombre,
            "idioma": self.idioma,
            "vector_facial": self.vector_facial,
            "fecha_registro": self.fecha_registro,
            "mundos": self.mundos,
            "estrellas_totales": self.estrellas_totales,
        }

    # ----------------------------------------------------------
    # VISUALIZACIÓN
    # ----------------------------------------------------------
    def mostrar_progreso(self):
        print(f"\n📘 Progreso de {self.nombre}:")
        for mundo, datos in self.mundos.items():
            total = datos.get("total_estrellas", 0)
            print(f" - {mundo.replace('_', ' ').capitalize()} ({total}⭐):")
            for mini, est in datos.items():
                if mini != "total_estrellas":
                    print(f"    · {mini.capitalize()}: {'⭐' * est or '—'}")
        print(f"\n🌟 Total acumulado: {self.estrellas_totales} estrellas\n")

    # ----------------------------------------------------------
    # DESBLOQUEO DE MUNDOS
    # ----------------------------------------------------------
    def mundo_desbloqueado(self, nombre_mundo):
        """
        Controla el desbloqueo progresivo de mundos basado en estrellas totales.
        Ejemplo de requisitos:
        - mundo_letras: 0
        - mundo_animales: 5
        - mundo_frutas_verduras: 10
        - mundo_numeros: 15
        - mundo_final: 20
        """
        requisitos = {
            "mundo_letras": 0,
            "mundo_animales": 5,
            "mundo_frutas_verduras": 10,
            "mundo_numeros": 15,
            "mundo_final": 20,
        }
        total = self.estrellas_totales
        umbral = requisitos.get(nombre_mundo, float('inf'))
        desbloqueado = total >= umbral
        print(f"🌍 Mundo '{nombre_mundo}' {'desbloqueado' if desbloqueado else 'bloqueado'} ({total}/{umbral}⭐)")
        return desbloqueado

# ------------------------------------------------------------------
# FUNCIONES DE CONSULTA GENERAL
# ------------------------------------------------------------------

def obtener_estadisticas_usuarios():
    usuarios = cargar_usuarios()
    total = len(usuarios)
    con_cara = sum(1 for u in usuarios.values() if u.get("vector_facial"))
    idiomas = {}
    for u in usuarios.values():
        idioma = u.get("idioma", "no_especificado")
        idiomas[idioma] = idiomas.get(idioma, 0) + 1

    return {
        "total_usuarios": total,
        "usuarios_con_cara": con_cara,
        "usuarios_sin_cara": total - con_cara,
        "distribucion_idiomas": idiomas,
        "umbral_similitud": UMBRAL_SIMILITUD,
    }

def listar_usuarios_con_cara():
    usuarios = cargar_usuarios()
    return [
        {"nombre": u["nombre"], "idioma": u.get("idioma", "no_especificado")}
        for u in usuarios.values() if u.get("vector_facial")
    ]
