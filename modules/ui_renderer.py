# ui_renderer.py
import cv2
import face_recognition
import time
import random

from models.modelos import crear_modelo, obtener_ruta_por_categoria
from ar.escena import crear_escena
from ar.deteccion import detectar_pose
from utils.conversiones import from_opencv_to_pygfx
from modules.cuia import alphaBlending
from modules.game_state import FACE_CASCADE


# ---------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------

def extraer_vector_facial(frame, face_box):
    try:
        x, y, w, h = face_box
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = [(y, x + w, y + h, x)]
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        if len(face_encodings) > 0:
            return face_encodings[0].tolist()
        return None
    except Exception as e:
        print(f"[ui_renderer] Error extrayendo vector facial: {e}")
        return None


def detectar_marcadores_disponibles(frame, detector, cameraMatrix, distCoeffs):
    ret, pose = detectar_pose(frame, 0.19, detector, cameraMatrix, distCoeffs)
    marcadores_encontrados = set()
    if ret and pose is not None:
        for marker_id in pose.keys():
            marcadores_encontrados.add(marker_id)
    return marcadores_encontrados


def draw_text_with_background(img, text, pos, font_scale=0.7,
                              color=(255, 255, 255), bg_color=(0, 0, 0)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 2
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    cv2.rectangle(
        img,
        (pos[0] - 5, pos[1] - text_height - 5),
        (pos[0] + text_width + 5, pos[1] + baseline + 5),
        bg_color, -1
    )
    cv2.putText(img, text, pos, font, font_scale, color, thickness)


def mostrar_modelo(self, categoria, nombre, marker_id, escenas, cameraMatrix, frame):
        ruta = obtener_ruta_por_categoria(categoria, nombre)
        if ruta:
            modelo = crear_modelo(ruta)
            escenas[marker_id] = crear_escena(
                modelo,
                cameraMatrix,
                frame.shape[1],
                frame.shape[0]
            )
        else:
            print(f"[UIRenderer] No se encontró modelo para {nombre} de {categoria}")

# ---------------------------------------------------
# Renderizado de realidad mixta
# ---------------------------------------------------

def realidad_mixta(frame, detector, cameraMatrix, distCoeffs, state, escenas):
    """
    Renderiza los modelos 3D sobre los marcadores según el estado actual.
    """
    ret, pose = detectar_pose(frame, 0.19, detector, cameraMatrix, distCoeffs)
    marcadores_actuales = set(pose.keys()) if ret and pose else set()

    # ---------------------------------------------------
    # Siempre mostrar Tina en marcador 0
    # ---------------------------------------------------
    if 0 in marcadores_actuales:
        if 0 not in escenas:
            ruta_tina = obtener_ruta_por_categoria("mascota", "tina_unicornio")
            modelo = crear_modelo(ruta_tina)
            escenas[0] = crear_escena(modelo, cameraMatrix, frame.shape[1], frame.shape[0])
        M = from_opencv_to_pygfx(pose[0][0], pose[0][1])
        escenas[0].actualizar_camara(M)
        imagen_render = escenas[0].render()
        imagen_render_bgr = cv2.cvtColor(imagen_render, cv2.COLOR_RGBA2BGRA)
        frame = alphaBlending(imagen_render_bgr, frame.copy())

    # ---------------------------------------------------
    # FASE: INICIO
    # ---------------------------------------------------
    if state.fase == "inicio":
        draw_text_with_background(frame, "✨ Bienvenido a Luminia, la tierra del aprendizaje mágico ✨", (50, 60),
                                  color=(255, 255, 255), bg_color=(56, 118, 29))
        draw_text_with_background(frame, "Tina: Hola, soy tu amiga mágica. Di 'continuar' para comenzar 🦄", (50, 100),
                                  color=(255, 255, 0), bg_color=(100, 100, 0))
        return frame

    # ---------------------------------------------------
    # FASE: RECONOCIMIENTO FACIAL
    # ---------------------------------------------------
    if state.fase == "reconocimiento_facial":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)
        if len(faces) > 0:
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            (x, y, w, h) = faces[0]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            vector_facial = extraer_vector_facial(frame, (x, y, w, h))
            if vector_facial is not None:
                state.vector_facial_actual = vector_facial
                state.cara_detectada = True
                draw_text_with_background(frame, "¡Cara detectada!", (x, y - 15),
                                          color=(0, 255, 0), bg_color=(0, 100, 0))
                draw_text_with_background(frame, "Di 'iniciar sesión' o 'registrarme'", (50, 50),
                                          color=(255, 255, 255), bg_color=(0, 0, 100))
                if state.fase != "reconocimiento_facial":
                    state.fase = "reconocimiento_facial"
                    state.esperando_voz = True
            else:
                draw_text_with_background(frame, "Error procesando cara", (x, y - 15),
                                          color=(255, 255, 255), bg_color=(200, 50, 50))
        else:
            draw_text_with_background(frame, "Mira a la cámara para comenzar", (50, 50),
                                      color=(255, 255, 255), bg_color=(100, 100, 100))
            state.cara_detectada = False
        return frame

    # ---------------------------------------------------
    # FASE: MENU PRINCIPAL
    # ---------------------------------------------------
    if state.fase == "menu_principal":
        draw_text_with_background(frame, "🏰 Bienvenido a Luminia 🏰", (50, 60),
                                  color=(255, 255, 255), bg_color=(56, 118, 29))
        draw_text_with_background(frame, "Elige el mundo que quieres visitar", (50, 100),
                                  color=(255, 255, 0), bg_color=(100, 100, 0))
        draw_text_with_background(frame, "Di: letras, animales, frutas y verduras, números o final", (50, 140),
                                  color=(255, 255, 255), bg_color=(0, 0, 100))

        # Mostrar los castillos en los marcadores configurados
        marcadores_castillos = state.marcadores_castillos if hasattr(state, "marcadores_castillos") else {
            1: "letras", 3: "animales", 4: "fruta_y_verdura", 6: "numeros", 11: "final"
        }

        for marker_id, mundo in marcadores_castillos.items():
            if marker_id in marcadores_actuales:
                desbloqueado = state.mundos_desbloqueados.get(mundo, False)
                ruta = obtener_ruta_por_categoria("castillo", mundo, desbloqueado)
                if ruta and marker_id not in escenas:
                    modelo = crear_modelo(ruta)
                    escenas[marker_id] = crear_escena(modelo, cameraMatrix, frame.shape[1], frame.shape[0])
                if marker_id in escenas:
                    M = from_opencv_to_pygfx(pose[marker_id][0], pose[marker_id][1])
                    escenas[marker_id].actualizar_camara(M)
                    imagen_render = escenas[marker_id].render()
                    imagen_render_bgr = cv2.cvtColor(imagen_render, cv2.COLOR_RGBA2BGRA)
                    frame = alphaBlending(imagen_render_bgr, frame)
        return frame

    # ---------------------------------------------------
    # FASE: MUNDO_X (letras, animales, frutas, números, final)
    # ---------------------------------------------------
    if state.fase.startswith("mundo_"):
        mundo = state.fase.split("_", 1)[1]
        draw_text_with_background(frame, f"🌈 Estás en el Mundo de las {mundo.replace('_', ' ').capitalize()}",
                                  (50, 60), color=(255, 255, 255), bg_color=(56, 118, 29))
        draw_text_with_background(frame, "Tina: Di el minijuego que quieres jugar o 'salir' para volver.",
                                  (50, 100), color=(255, 255, 0), bg_color=(100, 100, 0))

        # Mostrar solo el castillo del mundo actual (con color)
        marcador_mundo = next((k for k, v in state.marcadores_castillos.items() if v == mundo), None)
        if marcador_mundo and marcador_mundo in marcadores_actuales:
            ruta = obtener_ruta_por_categoria("castillo", mundo, True)
            if ruta and marcador_mundo not in escenas:
                modelo = crear_modelo(ruta)
                escenas[marcador_mundo] = crear_escena(modelo, cameraMatrix, frame.shape[1], frame.shape[0])
            if marcador_mundo in escenas:
                M = from_opencv_to_pygfx(pose[marcador_mundo][0], pose[marcador_mundo][1])
                escenas[marcador_mundo].actualizar_camara(M)
                imagen_render = escenas[marcador_mundo].render()
                imagen_render_bgr = cv2.cvtColor(imagen_render, cv2.COLOR_RGBA2BGRA)
                frame = alphaBlending(imagen_render_bgr, frame)
        return frame

    # ---------------------------------------------------
    # FASE: JUGANDO (delegado al mundo)
    # ---------------------------------------------------
    if state.fase == "jugando":
        draw_text_with_background(frame, "🎮 Jugando... Di 'salir' para volver al menú", (50, 60),
                                color=(255, 255, 255), bg_color=(56, 118, 29))

        # Seleccionar la instancia del mundo activo
        mundo_activo = getattr(state, f"instancia_mundo_{state.mundo_actual}", None)

        if mundo_activo:
            for categoria, nombre_modelo, marker_id in getattr(mundo_activo, "modelos_a_mostrar", []):
                if marker_id not in escenas:
                    ruta = obtener_ruta_por_categoria(categoria, nombre_modelo)
                    if ruta:
                        modelo = crear_modelo(ruta)
                        escenas[marker_id] = crear_escena(modelo, cameraMatrix, frame.shape[1], frame.shape[0])
                if marker_id in escenas and marker_id in pose:
                    M = from_opencv_to_pygfx(pose[marker_id][0], pose[marker_id][1])
                    escenas[marker_id].actualizar_camara(M)
                    imagen_render = escenas[marker_id].render()
                    imagen_render_bgr = cv2.cvtColor(imagen_render, cv2.COLOR_RGBA2BGRA)
                    frame = alphaBlending(imagen_render_bgr, frame)

        # Actualizar cámaras de cualquier otro marcador activo que no esté en modelos_a_mostrar
        for marker_id in marcadores_actuales - {0}:
            if marker_id in escenas and (not mundo_activo or marker_id not in [m[2] for m in getattr(mundo_activo, "modelos_a_mostrar", [])]):
                M = from_opencv_to_pygfx(pose[marker_id][0], pose[marker_id][1])
                escenas[marker_id].actualizar_camara(M)
                imagen_render = escenas[marker_id].render()
                imagen_render_bgr = cv2.cvtColor(imagen_render, cv2.COLOR_RGBA2BGRA)
                frame = alphaBlending(imagen_render_bgr, frame)

        return frame

    return frame


# ---------------------------------------------------
# Renderizado general de UI
# ---------------------------------------------------

def render_ui(frame, state, detector, cameraMatrix, distCoeffs, escenas, tts_manager):
    """
    Punto central de renderizado que llama a realidad_mixta() y dibuja textos adicionales.
    """
    frame = realidad_mixta(frame, detector, cameraMatrix, distCoeffs, state, escenas)

    # Mostrar posibles mensajes de error o ayudas contextuales
    if hasattr(state, "error_mensaje") and state.error_mensaje:
        draw_text_with_background(frame, f"⚠️ {state.error_mensaje}", (50, frame.shape[0] - 50),
                                  color=(255, 255, 255), bg_color=(150, 0, 0))

    return frame
