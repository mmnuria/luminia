# import json
# import os

# ###

# from pymongo import MongoClient
# from pymongo.errors import ConnectionFailure

# class MongoDBManager:
#     _instance = None  # Variable de clase para almacenar la única instancia

#     def __new__(cls, *args, **kwargs):
#         """Implementa el patrón Singleton asegurando una sola instancia."""
#         if cls._instance is None:
#             cls._instance = super(MongoDBManager, cls).__new__(cls)
#         return cls._instance

#     def __init__(self, uri="mongodb://root:example@localhost:27017/?authSource=admin", db_name="luminia_db", collection_name="users"):
#         # Evitar reinicialización si la instancia ya existe
#         if not hasattr(self, '_initialized'):
#             self.uri = uri
#             self.db_name = db_name
#             self.collection_name = collection_name
#             self.client = None
#             self.db = None
#             self.collection = None
#             self._initialized = True

#     def conectar(self):
#         """Establece la conexión con MongoDB."""
#         if self.client is not None:
#             print("Ya está conectado a MongoDB")
#             return
#         try:
#             self.client = MongoClient(self.uri)
#             # Verificar la conexión
#             self.client.admin.command('ping')
#             print("Conexión exitosa a MongoDB")
#             self.db = self.client[self.db_name]
#             self.collection = self.db[self.collection_name]
#         except ConnectionFailure as e:
#             print(f"Error al conectar a MongoDB: {e}")
#             raise
#         except Exception as e:
#             print(f"Error inesperado: {e}")
#             raise

#     def desconectar(self):
#         """Cierra la conexión con MongoDB."""
#         if self.client:
#             self.client.close()
#             print("Conexión cerrada")
#             self.client = None
#             self.db = None
#             self.collection = None
#         else:
#             print("Cuidado! El cliente ya está cerrado o no se inicializó")

#     def crear_usuario(self, nombre, edad=30):
#         """Inserta un nuevo usuario en la colección."""
#         try:
#             self.collection.insert_one({"nombre": nombre, "edad": edad})
#             print(f"Usuario {nombre} creado")
#         except Exception as e:
#             print(f"Error al crear usuario: {e}")

#     def encontrar_usuario(self, nombre):
#         """Busca usuarios por nombre en la colección."""
#         try:
#             usuarios = self.collection.find({"nombre": nombre})
#             for usuario in usuarios:
#                 print("Usuario:", usuario)
#             return usuarios
#         except Exception as e:
#             print(f"Error al buscar usuario: {e}")


# ###

# DATA_PATH = "data/luminia_data.json"

# def _asegurar_directorio():
#     if not os.path.exists("data"):
#         os.makedirs("data")

# # def cargar_data():
# #     _asegurar_directorio()
# #     if not os.path.exists(DATA_PATH):
# #         return {"usuarios": {}, "game_state": {}}
# #     with open(DATA_PATH, "r", encoding="utf-8") as f:
# #         try:
# #             data = json.load(f)
# #             if "usuarios" not in data:
# #                 data["usuarios"] = {}
# #             if "game_state" not in data:
# #                 data["game_state"] = {}
# #             return data
# #         except json.JSONDecodeError:
# #             return {"usuarios": {}, "game_state": {}}

# # def guardar_data(data):
# #     _asegurar_directorio()
# #     with open(DATA_PATH, "w", encoding="utf-8") as f:
# #         json.dump(data, f, ensure_ascii=False, indent=4)

# def cargar_data():
#     _asegurar_directorio()
#     if not os.path.exists(DATA_PATH):
#         return {"usuarios": {}}
#     with open(DATA_PATH, "r", encoding="utf-8") as f:
#         try:
#             data = json.load(f)
#             if "usuarios" not in data:
#                 data["usuarios"] = {}
#             return data
#         except json.JSONDecodeError:
#             return {"usuarios": {}}

# def guardar_data(data):
#     _asegurar_directorio()
#     with open(DATA_PATH, "w", encoding="utf-8") as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)

# def sincronizar_usuario_y_game_state(nombre_usuario):
#     datos = cargar_data()
    
#     if "game_state" not in datos or "usuario_data" not in datos["game_state"]:
#         print("No hay game_state válido que sincronizar.")
#         return
    
#     usuario_data = datos["game_state"]["usuario_data"]
    
#     # 🔄 Copiar usuario_data a usuarios[nombre]
#     datos["usuarios"][nombre_usuario] = usuario_data
    
#     # También podrías querer actualizar ciertos valores del game_state
#     # desde el usuario (si cambian fuera del juego)
#     # datos["game_state"]["usuario_data"] = datos["usuarios"][nombre_usuario]
    
#     guardar_data(datos)
#     print(f"✅ Datos sincronizados con el usuario '{nombre_usuario}'")

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import time

class MongoDBManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, uri="mongodb://root:example@localhost:27017/?authSource=admin", db_name="luminia_db", collection_name="users"):
        if not hasattr(self, '_initialized'):
            self.uri = uri
            self.db_name = db_name
            self.collection_name = collection_name
            self.client = None
            self.db = None
            self.collection = None
            self._initialized = True

    def conectar(self):
        """Establece la conexión con MongoDB."""
        if self.client is not None:
            print("Ya está conectado a MongoDB")
            return
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            print("Conexión exitosa a MongoDB")
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
        except ConnectionFailure as e:
            print(f"Error al conectar a MongoDB: {e}")
            raise
        except Exception as e:
            print(f"Error inesperado: {e}")
            raise

    def asegurar_conexion(self):
        """Verifica si la conexión está activa; si no, intenta reconectar."""
        max_intentos = 3
        for i in range(max_intentos):
            if self.client is None or self.collection is None:
                print(f"Conexión no activa, intentando reconectar... (intento {i+1}/{max_intentos})")
                try:
                    self.conectar()
                    return
                except Exception as e:
                    print(f"Error al reconectar: {e}")
                    time.sleep(1)
            try:
                self.client.admin.command('ping')
                return
            except ConnectionFailure:
                print(f"Conexión perdida, intentando reconectar... (intento {i+1}/{max_intentos})")
                self.client = None
                self.db = None
                self.collection = None
                time.sleep(1)
        raise Exception("No se pudo conectar a MongoDB después de varios intentos")

    def desconectar(self):
        """Cierra la conexión con MongoDB."""
        if self.client:
            self.client.close()
            print("Conexión cerrada")
            self.client = None
            self.db = None
            self.collection = None
        else:
            print("Cuidado! El cliente ya está cerrado o no se inicializó")

    def crear_usuario(self, datos_usuario):
        """Inserta un nuevo usuario. _id = nombre.lower()"""
        self.asegurar_conexion()
        try:
            nombre_lower = datos_usuario["nombre"].lower()
            if self.collection.find_one({"_id": nombre_lower}):
                print(f"Usuario {nombre_lower} ya existe")
                return None
            datos_usuario["_id"] = nombre_lower
            result = self.collection.insert_one(datos_usuario)
            print(f"Usuario {datos_usuario['nombre']} creado con _id: {result.inserted_id}")
            return datos_usuario
        except Exception as e:
            print(f"Error al crear usuario: {e}")
            return None

    def encontrar_usuario(self, nombre):
        """Busca un usuario por nombre (case-insensitive, usa _id)"""
        self.asegurar_conexion()
        try:
            usuario = self.collection.find_one({"_id": nombre.lower()})
            if usuario:
                print("Usuario encontrado:", usuario)
                return usuario
            return None
        except Exception as e:
            print(f"Error al buscar usuario: {e}")
            return None

    def actualizar_usuario(self, nombre, datos_actualizados):
        """Actualiza campos de un usuario"""
        self.asegurar_conexion()
        try:
            result = self.collection.update_one(
                {"_id": nombre.lower()},
                {"$set": datos_actualizados}
            )
            if result.matched_count > 0:
                print(f"Usuario {nombre} actualizado")
                return True
            return False
        except Exception as e:
            print(f"Error al actualizar usuario: {e}")
            return False

    def eliminar_usuario(self, nombre):
        """Elimina un usuario"""
        self.asegurar_conexion()
        try:
            result = self.collection.delete_one({"_id": nombre.lower()})
            if result.deleted_count > 0:
                print(f"Usuario {nombre} eliminado")
                return True
            return False
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False

    def listar_usuarios(self):
        """Lista todos los usuarios (sin vector_facial por brevedad)"""
        self.asegurar_conexion()
        try:
            return list(self.collection.find({}, {"_id": 1, "nombre": 1, "estrellas_totales": 1}))
        except Exception as e:
            print(f"Error al listar usuarios: {e}")
            return []
    
    def mundos_desbloqueados_usuario(self, nombre):
        """Devuelve la lista de mundos desbloqueados de un usuario"""
        self.asegurar_conexion()
        usuario = self.collection.find_one({"_id": nombre.lower()})
        if usuario and "mundos_desbloqueados" in usuario:
            return usuario["mundos_desbloqueados"]
        return []
    
    # -------------------- NUEVAS FUNCIONES --------------------

    def obtener_nombre(self, nombre):
        """Devuelve el nombre del usuario"""
        self.asegurar_conexion()
        usuario = self.collection.find_one({"_id": nombre.lower()})
        if usuario and "nombre" in usuario:
            return usuario["nombre"]
        return None

    def obtener_estrellas(self, nombre):
        """Devuelve las estrellas_totales de un usuario"""
        self.asegurar_conexion()
        usuario = self.collection.find_one({"_id": nombre.lower()})
        if usuario and "estrellas_totales" in usuario:
            return usuario["estrellas_totales"]
        return 0

    def obtener_lumios(self, nombre):
        """Devuelve los lumios de un usuario"""
        self.asegurar_conexion()
        usuario = self.collection.find_one({"_id": nombre.lower()})
        if usuario and "lumios" in usuario:
            return usuario["lumios"]
        return 0


