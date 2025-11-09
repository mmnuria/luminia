import pytest
from modules.gestor_juegos import GestorJuegosAR
from modules.game_state import GameState
from modules.data_manager import MongoDBManager


class DummyUI:
    def render(self, msg):
        print(f"[UI] {msg}")

class DummyVoice:
    def escuchar(self):
        comando = "letras"
        print(f"[DummyVoice] Simulando comando: {comando}")
        return comando

@pytest.mark.integration_db
def test_flujo_integracion_con_db():
    """
    Prueba el flujo completo usando una base de datos MongoDB real.
    Requiere que el contenedor o servicio esté activo:
    
        docker run -d -p 27017:27017 \
            -e MONGO_INITDB_ROOT_USERNAME=root \
            -e MONGO_INITDB_ROOT_PASSWORD=example \
            mongo
    """

    # Conectar con MongoDB
    db = MongoDBManager()
    assert db.conectar() is True

    # Crear o cargar usuario
    nombre_usuario = "nuria"
    usuario = db.encontrar_usuario(nombre_usuario)
    if usuario is None:
        usuario = {
            "nombre": nombre_usuario,
            "lumios": 0,
            "estrellas_totales": 0,
            "mundos": {
                "letras": {"adivina": 0, "memoria": 0, "total_estrellas": 0},
                "animales": {"adivina": 0, "memoria": 0, "total_estrellas": 0}
            }
        }
        db.crear_usuario(usuario)

    # Inicializar gestor y estado
    gs = GameState()
    gestor = GestorJuegosAR(DummyUI(), DummyVoice(), gs)
    gs.usuario_actual = nombre_usuario
    gs.usuario_data = usuario
    gs.fase = "menu_principal"

    # Simular flujo de interacción
    comando = "letras"
    gestor.procesar_comando_voz(comando)
    assert gs.fase.startswith("mundo_")

    gestor._iniciar_minijuego("adivina")
    assert gs.fase == "jugando"

    # Registrar resultado y actualizar en BD
    gestor.registrar_resultado("letras", "adivina", 3)
    actualizado = db.actualizar_usuario(gs.usuario_actual, gs.usuario_data)
    assert actualizado is True

    # Verificar que se guardó correctamente
    usuario_final = db.encontrar_usuario(nombre_usuario)
    assert usuario_final is not None
    assert usuario_final["estrellas_totales"] >= 3

    # Desconectar
    assert db.desconectar() is True