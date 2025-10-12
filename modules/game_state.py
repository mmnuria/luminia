import cv2

# ----- ESTADOS DE LA APLICACION -----
class GameState:
    def __init__(self):
        self.fase = "reconocimiento_facial"
        self.usuario_identificado = False
        self.pregunta_realizada = False
        self.respuesta_recibida = ""
        self.respuesta_correcta = False
        self.tiempo_pregunta = 0
        self.mostrar_resultado = False
        self.tiempo_resultado = 0
        self.microfono_listo = False
        self.esperando_voz = False
        self.marker_id_actual = None
        self.modelo_actual = None
        self.info_modelo_actual = None
        self.usuario_nombre = None
        self.usuario_data = None
        self.esperando_comando_sesion = False
        self.gestor_juegos = None  # Will be set in main.py
        self.modo_juego = None
        self.idioma_seleccionado = None
        self.idioma_cambiado = None
        self.contador_idioma = 0
        self.nombre_cambiado = None
        self.contador_nombre = 0
        self.vector_facial_actual = None
        self.marcadores_detectados = set()
        self.marcadores_respondidos = set()
        self.marcadores_pendientes = set()
        self.puntuacion = 0
        self.total_preguntas = 0
        self.juego_completado = False
        self.tiempo_escaneo = 0
        self.en_fase_escaneo = False
        self.error_mensaje = ""
        self.cara_detectada = False
        self.mensaje_temporal = ""

# ----- CONFIGURACIÓN RECONOCIMIENTO FACIAL -----
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ----- VARIABLES GLOBALES -----
JUEGO_ACTUAL = "juego_1"