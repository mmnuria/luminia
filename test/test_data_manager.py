import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from modules.data_manager import MongoDBManager

@pytest.fixture
def manager():
    return MongoDBManager()

def test_conexion_y_desconexion(manager):
    assert manager.conectar() is True
    assert manager.desconectar() is True

def test_lectura_usuario(manager):
    usuario = manager.encontrar_usuario("nuria")
    assert usuario is not None
    assert "lumios" in usuario

def test_actualizacion_datos(manager):
    resultado = manager.actualizar_usuario("nuria", {"lumios": 120})
    assert resultado is True

