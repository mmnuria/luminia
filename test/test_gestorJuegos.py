import sys, os
import pytest

# Añadimos el path para importar correctamente
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.gestor_juegos import GestorJuegosAR

# --- Clases simuladas (Mocks) para no depender de otros módulos ---
class DummyUI:
    def render(self, *args, **kwargs):
        pass

class DummyVoice:
    def hablar(self, texto):
        print(f"[Voz] {texto}")

class DummyGameState:
    def __init__(self):
        self.fase = "menu_principal"
        self.mensaje_actual = ""
        self.usuario_actual = "test_user"
        self.usuario_data = {"estrellas_totales": 5}
        self._progreso = {}
    
    def establecer_fase(self, fase, **kwargs):
        self.fase = fase

    def registrar_resultado(self, mundo, minijuego, estrellas):
        self._progreso[minijuego] = estrellas

    def obtener_progreso(self, mundo):
        return {"total_estrellas": 3, "adivina": 2}

    def _verificar_desbloqueos(self):
        pass


@pytest.fixture
def gestor():
    ui = DummyUI()
    voice = DummyVoice()
    state = DummyGameState()
    return GestorJuegosAR(ui, voice, state)


# --- TESTS ---

def test_inicia_minijuego(gestor):
    """Comprueba que _iniciar_minijuego cambia la fase y registra el juego."""
    # Simulamos un mundo con un método iniciar_juego()
    class DummyMundo:
        def iniciar_juego(self, tipo):
            print(f"[DummyMundo] Juego {tipo} iniciado.")

    gestor.mundo_actual = DummyMundo()
    gestor._iniciar_minijuego("adivina")

    assert gestor.state.fase == "jugando"
    assert gestor.juego_actual == "adivina"

def test_mostrar_mensaje(gestor):
    """Verifica que el mensaje se guarda correctamente en el estado."""
    gestor._mostrar("Mensaje de prueba")
    assert gestor.state.mensaje_actual == "Mensaje de prueba"

def test_salir_mundo(gestor):
    """Verifica que al salir del mundo se vuelve al menú principal."""
    gestor.mundo_actual = "dummy"
    gestor._salir_mundo()
    assert gestor.mundo_actual is None
    assert gestor.state.fase == "menu_principal"

def test_registrar_resultado(gestor):
    """Comprueba que se registran los resultados correctamente."""
    gestor.registrar_resultado("letras", "adivina", 3)
    assert gestor.state._progreso["adivina"] == 3
