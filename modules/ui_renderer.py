import cv2
import face_recognition
import time
from modules.juegos import JuegoDescubreAR, JuegoEncuentraFrutasAR, JuegoCategoriasAR, JuegoMemoriaAR
from models.modelos import MODELOS_FRUTAS_VERDURAS, crear_modelo_por_id, obtener_info_modelo
from ar.escena import crear_escena
from ar.deteccion import detectar_pose, ocultar_marcadores_visualmente
from utils.conversiones import from_opencv_to_pygfx
from modules.cuia import alphaBlending
from modules.game_state import FACE_CASCADE

def extraer_vector_facial(frame, face_box):
    try:
        x, y, w, h = face_box
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = [(y, x+w, y+h, x)]
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        if len(face_encodings) > 0:
            return face_encodings[0].tolist()
        return None
    except Exception as e:
        print(f"Error extrayendo vector facial: {e}")
        return None

def detectar_marcadores_disponibles(frame, detector, cameraMatrix, distCoeffs):
    ret, pose = detectar_pose(frame, 0.19, detector, cameraMatrix, distCoeffs)
    marcadores_encontrados = set()
    if ret and pose is not None:
        for marker_id in pose.keys():
            if marker_id in MODELOS_FRUTAS_VERDURAS:
                marcadores_encontrados.add(marker_id)
    return marcadores_encontrados

def realidad_mixta(frame, detector, cameraMatrix, distCoeffs, state, escenas):
    marcadores_actuales = detectar_marcadores_disponibles(frame, detector, cameraMatrix, distCoeffs)
    if state.fase == "escaneo_inicial":
        state.marcadores_detectados.update(marcadores_actuales)
    if state.usuario_identificado and state.fase in ["pregunta", "esperando_respuesta", "resultado"]:
        ret, pose = detectar_pose(frame, 0.19, detector, cameraMatrix, distCoeffs)
        if ret and pose is not None:
            marker_ids = list(pose.keys())
            if marker_ids:
                marcador_pendiente_visible = None
                for mid in marker_ids:
                    if mid in state.marcadores_pendientes:
                        marcador_pendiente_visible = mid
                        break
                if marcador_pendiente_visible:
                    marker_id = marcador_pendiente_visible
                else:
                    marker_id = marker_ids[0]
                if state.marker_id_actual != marker_id:
                    state.marker_id_actual = marker_id
                    state.info_modelo_actual = obtener_info_modelo(marker_id)
                    if marker_id not in escenas:
                        modelo = crear_modelo_por_id(marker_id)
                        escenas[marker_id] = crear_escena(modelo, cameraMatrix,
                                                        int(frame.shape[1]), int(frame.shape[0]))
                    print(f" Mostrando: {state.info_modelo_actual['nombre']} (ID: {marker_id})")
                if state.marker_id_actual in escenas:
                    M = from_opencv_to_pygfx(pose[state.marker_id_actual][0], pose[state.marker_id_actual][1])
                    escenas[state.marker_id_actual].actualizar_camara(M)
                    imagen_render = escenas[state.marker_id_actual].render()
                    imagen_render_bgr = cv2.cvtColor(imagen_render, cv2.COLOR_RGBA2BGRA)
                    frame_con_modelo = alphaBlending(imagen_render_bgr, frame.copy())
                    return frame_con_modelo
    return frame

def draw_text_with_background(img, text, pos, font_scale=0.7, color=(255, 255, 255), bg_color=(0, 0, 0)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 2
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    cv2.rectangle(img,
                  (pos[0] - 5, pos[1] - text_height - 5),
                  (pos[0] + text_width + 5, pos[1] + baseline + 5),
                  bg_color, -1)
    cv2.putText(img, text, pos, font, font_scale, color, thickness)

def render_ui(frame, state, detector, cameraMatrix, distCoeffs, escenas, tts_manager):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    current_time = time.time()
    alto = frame.shape[0]
    if state.fase == "reconocimiento_facial":
        faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)
        if len(faces) > 0:
            faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
            (x, y, w, h) = faces[0]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
            vector_facial = extraer_vector_facial(frame, (x, y, w, h))
            if vector_facial is not None:
                state.vector_facial_actual = vector_facial
                state.cara_detectada = True
                draw_text_with_background(frame, "¡Cara detectada!", (x, y-15),
                                        color=(0, 255, 0), bg_color=(0, 100, 0))
                draw_text_with_background(frame, "Di: 'iniciar sesión' o 'registrarme'", (50, 50),
                                        color=(255, 255, 255), bg_color=(0, 0, 100))
                if state.fase != "esperando_comando":
                    state.fase = "esperando_comando"
                    state.esperando_voz = True
                    if tts_manager:
                        tts_manager.announce("Di: iniciar sesión o registrarme", key="esperando_comando")
            else:
                draw_text_with_background(frame, "Error procesando cara", (x, y-15),
                                        color=(255, 255, 255), bg_color=(200, 50, 50))
        else:
            draw_text_with_background(frame, "Mira a la cámara para comenzar", (50, 50),
                                    color=(255, 255, 255), bg_color=(100, 100, 100))
            state.cara_detectada = False
        if state.microfono_listo:
            draw_text_with_background(frame, " Micrófono listo ", (50, 100),
                                    color=(0, 255, 0), bg_color=(0, 100, 0))
        else:
            draw_text_with_background(frame, " Configurando micrófono... ", (50, 100),
                                    color=(255, 255, 0), bg_color=(100, 100, 0))
    elif state.fase == "esperando_comando":
        draw_text_with_background(frame, "BIENVENIDO A LA PLATAFORMA EDUCATIVA DE Kids&Veggies", (50, 60),
                color=(255, 255, 255), bg_color=(56,118, 29))
        draw_text_with_background(frame, "Di: 'iniciar sesión' o 'registrarme'", (50, 100),
                color=(255, 255, 255), bg_color=(0, 0, 100))
        draw_text_with_background(frame, "Esperando comando de voz...", (50, 140),
                color=(255, 255, 0), bg_color=(100, 100, 0))
        if not state.esperando_voz:
            state.esperando_voz = True
    elif state.fase == "intentando_iniciar_sesion":
        draw_text_with_background(frame, "Verificando identidad...", (50, alto - 100),
                                color=(255, 255, 255), bg_color=(0, 100, 100))
        if hasattr(state, 'vector_facial_actual'):
            from modules.usuarios import buscar_usuario_por_cara
            nombre_encontrado, datos_usuario = buscar_usuario_por_cara(state.vector_facial_actual)
            if nombre_encontrado:
                state.usuario_nombre = nombre_encontrado
                state.usuario_data = datos_usuario
                state.fase = "menu_principal"
                state.sesion_iniciada = True
                print(f"🔓 Sesión iniciada para {nombre_encontrado}")
                if tts_manager:
                    tts_manager.announce(f"Sesión iniciada. Bienvenido {nombre_encontrado}", key="inicio_sesion")
            else:
                print("❌ Cara no registrada. Debes registrarte primero.")
                state.error_mensaje = "Cara no registrada. Di 'registrarme' para crear una cuenta."
                state.fase = "inicio_sesion_fallido"
                state.esperando_voz = False
    elif state.fase == "inicio_sesion_fallido":
        draw_text_with_background(frame, "Cara no registrada. No puedes iniciar sesión.", (50, alto - 130),
                                color=(255, 255, 255), bg_color=(200, 50, 50))
        draw_text_with_background(frame, "Di: 'registrarme' para crear una cuenta", (50, alto - 100),
                                color=(255, 255, 255), bg_color=(0, 0, 100))
        if not hasattr(state, 'tiempo_pausa_cara_no_registrada'):
            state.tiempo_pausa_cara_no_registrada = time.time()
        if time.time() - state.tiempo_pausa_cara_no_registrada > 2:
            state.fase = "esperando_comando"
            del state.tiempo_pausa_cara_no_registrada
        state.esperando_voz = True
    elif state.fase == "registro_denegado_por_seguridad":
        draw_text_with_background(frame, "Esa cara ya está registrada.", (50, alto - 130),
                                color=(255, 255, 255), bg_color=(200, 50, 50))
        draw_text_with_background(frame, "Di: 'iniciar sesión' para entrar", (50, alto - 100),
                                color=(255, 255, 255), bg_color=(0, 0, 100))
        if not hasattr(state, 'tiempo_pausa'):
            state.tiempo_pausa = time.time()
        if time.time() - state.tiempo_pausa > 2:
            state.fase = "esperando_comando"
            del state.tiempo_pausa
        state.esperando_voz = True
    elif state.fase == "esperando_nombre_registro":
        if hasattr(state, 'vector_facial_actual'):
            from modules.usuarios import buscar_usuario_por_cara
            nombre_encontrado, datos_usuario = buscar_usuario_por_cara(state.vector_facial_actual)
            if nombre_encontrado:
                state.error_mensaje = f"Usuario registrado como {nombre_encontrado}. Di 'iniciar sesión'."
                print(f" Intento de registro con cara ya registrada: {nombre_encontrado}")
                if not hasattr(state, 'tiempo_pausa'):
                    state.tiempo_pausa = time.time()
                if time.time() - state.tiempo_pausa > 2:
                    state.fase = "registro_denegado_por_seguridad"
                    del state.tiempo_pausa
                state.esperando_voz = False
            else:
                draw_text_with_background(frame, "Dime tu nombre...", (50, alto - 100),
                                        color=(255, 255, 255), bg_color=(0, 100, 0))
                if hasattr(state, 'error_mensaje'):
                    draw_text_with_background(frame, state.error_mensaje, (50, alto - 130),
                                            color=(255, 255, 255), bg_color=(200, 50, 50))
                state.esperando_voz = True
        else:
            state.error_mensaje = "No se detectó tu cara. Intenta de nuevo."
            print(" Registro detenido: no hay vector facial.")
    elif state.fase == "esperando_idioma_registro":
        draw_text_with_background(frame, f"Hola {state.usuario_nombre}!", (50, alto - 160),
                        color=(255, 255, 255), bg_color=(0, 100, 0))
        draw_text_with_background(frame, "¿Qué idioma prefieres?", (50, alto - 130),
                        color=(255, 255, 255), bg_color=(100, 100, 0))
        draw_text_with_background(frame, "Di: 'español' o 'inglés'", (50, alto - 100),
                        color=(255, 255, 255), bg_color=(100, 100, 0))
        state.esperando_voz = True
        if hasattr(state, 'error_mensaje'):
            draw_text_with_background(frame, state.error_mensaje, (50, alto - 190),
                                    color=(255, 255, 255), bg_color=(200, 50, 50))
    elif state.fase == "menu_principal":
        if hasattr(state, 'registro_exitoso') and state.registro_exitoso:
            draw_text_with_background(frame, f"Usuario registrado exitosamente", (50, alto - 220),
                            color=(255, 255, 255), bg_color=(50, 200, 50))
            if hasattr(state, 'idioma_seleccionado'):
                draw_text_with_background(frame, f"Idioma: {state.idioma_seleccionado}", (50, alto - 250),
                                color=(255, 255, 255), bg_color=(50, 200, 50))
            if not hasattr(state, 'contador_registro'):
                state.contador_registro = 0
            state.contador_registro += 1
            if state.contador_registro > 90:
                delattr(state, 'registro_exitoso')
                delattr(state, 'contador_registro')
                if hasattr(state, 'idioma_seleccionado'):
                    delattr(state, 'idioma_seleccionado')
        draw_text_with_background(frame, "MENÚ PRINCIPAL", (50, 40),
                        color=(255, 255, 255), bg_color=(0, 100, 0))
        nombre = state.usuario_nombre or "Usuario"
        draw_text_with_background(frame, f"Bienvenido, {nombre}", (50, 80),
                        font_scale=0.7, color=(255, 255, 255), bg_color=(0, 0, 100))
        draw_text_with_background(frame, "Di 'cuenta' para administrar tus datos", (50, 120),
                        color=(255, 255, 255), bg_color=(100, 0, 100))
        draw_text_with_background(frame, "Di 'progreso' para ver tus estadísticas", (50, 160),
                        color=(255, 255, 255), bg_color=(100, 0, 100))
        draw_text_with_background(frame, "Di 'comenzar' para jugar", (50, 200),
                        color=(255, 255, 255), bg_color=(100, 0, 100))
        draw_text_with_background(frame, "Di 'salir' para cerrar", (50, 240),
                        color=(255, 255, 255), bg_color=(100, 0, 100))
        state.esperando_voz = True
    elif state.fase == "ver_progreso":
        from modules.usuarios import obtener_progreso_usuario
        progreso = obtener_progreso_usuario(state.usuario_nombre)
        if not progreso or "mensaje" in progreso:
            draw_text_with_background(frame, "No hay datos de progreso aún.", (50, 100),
                                    color=(255, 255, 255), bg_color=(100, 0, 0))
        else:
            y = 40
            draw_text_with_background(frame, f"PROGRESO DE {progreso['nombre'].upper()}", (50, y), bg_color=(0, 100, 100)); y += 40
            draw_text_with_background(frame, f"Partidas totales: {progreso['total_partidas']}", (50, y)); y += 30
            draw_text_with_background(frame, f"Número de juegos diferentes: {progreso['juegos_completados']}", (50, y)); y += 30
            for modo, stats in progreso["resumen_por_modo"].items():
                draw_text_with_background(frame, f"--- MODO {modo.upper()} ---", (50, y), bg_color=(20, 20, 100)); y += 30
                draw_text_with_background(frame, f"  Juegos: {stats['juegos_jugados']}", (50, y)); y += 25
                draw_text_with_background(frame, f"  Partidas: {stats['total_partidas_modo']}", (50, y)); y += 25
                draw_text_with_background(frame, f"  Promedio: {stats['promedio_general']:.1f}%", (50, y)); y += 25
                for juego, info in stats["juegos"].items():
                    draw_text_with_background(frame, f"{juego}: {info['puntuacion_media']:.1f}% ({info['partidas_jugadas']} partidas)", (50, y)); y += 30
        draw_text_with_background(frame, "Di 'volver' para regresar al menú", (50, alto - 60), bg_color=(0, 0, 100))
        state.esperando_voz = True
    elif state.fase == "configuracion_cuenta":
        draw_text_with_background(frame, "CONFIGURACIÓN DE LA CUENTA", (50, 40),
                        color=(255, 255, 255), bg_color=(0, 100, 0))
        nombre = state.usuario_nombre or "Usuario"
        idioma = state.usuario_data.get("idioma")
        if idioma == "es":
            idioma = "Español"
        else:
            idioma = "Inglés"
        draw_text_with_background(frame, f"Nombre: {nombre}", (50, 80),
                        font_scale=0.7, color=(255, 255, 255), bg_color=(0, 0, 100))
        draw_text_with_background(frame, f"Idioma: {idioma}", (50, 120),
                        font_scale=0.7, color=(255, 255, 255), bg_color=(0, 0, 120))
        draw_text_with_background(frame, "Di 'cambiar nombre' para modificar tu nombre", (50, 160),
                        color=(255, 255, 255), bg_color=(100, 0, 100))
        draw_text_with_background(frame, "Di 'cambiar idioma' para seleccionar un nuevo idioma", (50, 200),
                        color=(255, 255, 255), bg_color=(100, 0, 100))
        draw_text_with_background(frame, "Di 'volver' para regresar al menú principal", (50, 240),
                        color=(255, 255, 255), bg_color=(100, 0, 100))
        if hasattr(state, 'error_mensaje'):
            draw_text_with_background(frame, state.error_mensaje, (50, alto - 190),
                                    color=(255, 255, 255), bg_color=(200, 50, 50))
        state.esperando_voz = True
    elif state.fase == "esperando_nuevo_nombre":
        draw_text_with_background(frame, "Escuchando nuevo nombre...", (50, 40),
                        color=(255, 255, 255), bg_color=(0, 100, 0))
        if hasattr(state, 'nombre_cambiado') and state.nombre_cambiado:
            draw_text_with_background(frame, "Nombre actualizado correctamente", (50, alto - 220),
                color=(255, 255, 255), bg_color=(50, 200, 50))
            state.contador_nombre += 1
            if state.contador_nombre > 90:
                delattr(state, 'nombre_cambiado')
                delattr(state, 'contador_nombre')
        if hasattr(state, 'mensaje_temporal'):
            draw_text_with_background(frame, state.mensaje_temporal, (50, alto - 280),
                color=(255, 255, 255), bg_color=(100, 100, 0))
            delattr(state, 'mensaje_temporal')
        if hasattr(state, 'error_mensaje'):
            draw_text_with_background(frame, state.error_mensaje, (50, alto - 190),
                                    color=(255, 255, 255), bg_color=(200, 50, 50))
    elif state.fase == "esperando_nuevo_idioma":
        draw_text_with_background(frame, "Escuchando nuevo idioma...", (50, 40),
                        color=(255, 255, 255), bg_color=(0, 100, 0))
        if hasattr(state, 'idioma_cambiado') and state.idioma_cambiado:
            draw_text_with_background(frame, "Idioma actualizado correctamente", (50, alto - 250),
                color=(255, 255, 255), bg_color=(50, 200, 50))
            state.contador_idioma += 1
            if state.contador_idioma > 90:
                delattr(state, 'idioma_cambiado')
                delattr(state, 'contador_idioma')
        if hasattr(state, 'mensaje_temporal'):
            draw_text_with_background(frame, state.mensaje_temporal, (50, alto - 280),
                color=(255, 255, 255), bg_color=(100, 100, 0))
            delattr(state, 'mensaje_temporal')
        if hasattr(state, 'error_mensaje'):
            draw_text_with_background(frame, state.error_mensaje, (50, alto - 190),
                                    color=(255, 255, 255), bg_color=(200, 50, 50))
    elif state.fase == "seleccion_modo":
        nombre = state.usuario_nombre or "Desconocido"
        draw_text_with_background(frame, f"Hola, {nombre}", (50, 80),
                font_scale=0.7, color=(255, 255, 255), bg_color=(0, 0, 0))
        draw_text_with_background(frame, "SELECCIONA MODO DE JUEGO:", (50, 120),
                                color=(255, 255, 255), bg_color=(0, 100, 0))
        draw_text_with_background(frame, "Di 'entrenamiento' para practicar", (50, 160),
                                color=(255, 255, 255), bg_color=(0, 0, 100))
        draw_text_with_background(frame, "Di 'evaluación' para ser evaluado", (50, 200),
                                color=(255, 255, 255), bg_color=(100, 0, 0))
        draw_text_with_background(frame, "Di 'volver' para regresar al menú principal", (50, 240),
                        color=(255, 255, 255), bg_color=(100, 0, 100))
        state.esperando_voz = True
    elif state.fase == "seleccion_juego":
        modo = getattr(state, 'modo_juego', 'desconocido')
        draw_text_with_background(frame, f"MODO: {modo.upper()}", (50, 50),
                                color=(255, 255, 255), bg_color=(100, 0, 100))
        state.gestor_juegos.establecer_modo(modo)
        juegos_disponibles = state.gestor_juegos.obtener_juegos_disponibles()
        draw_text_with_background(frame, "SELECCIONA UN JUEGO:", (50, 100),
                                color=(255, 255, 255), bg_color=(0, 100, 0))
        y_pos = 140
        for key, juego in juegos_disponibles.items():
            draw_text_with_background(frame, f"Di '{juego['comando']}' - {juego['nombre']}",
                                    (50, y_pos), font_scale=0.7,
                                    color=(255, 255, 255), bg_color=(0, 0, 100))
            y_pos += 30
            draw_text_with_background(frame, f"  {juego['descripcion']}",
                                    (70, y_pos), font_scale=0.5,
                                    color=(200, 200, 200), bg_color=(50, 50, 50))
            y_pos += 40
        draw_text_with_background(frame, "Di 'volver' para cambiar modo", (50, y_pos),
                                font_scale=0.6, color=(255, 255, 0), bg_color=(100, 100, 0))
        state.esperando_voz = True
    elif state.fase == "jugando":
        frame_limpio = frame.copy()
        frame_visual = frame.copy()
        marcadores_actuales = detectar_marcadores_disponibles(frame_limpio, detector, cameraMatrix, distCoeffs)
        state.marcadores_detectados.update(marcadores_actuales)
        ocultar_marcadores_visualmente(frame_visual, detector)
        juego_actual = getattr(state.gestor_juegos, 'juego_activo', None)
        if juego_actual and (isinstance(juego_actual, JuegoDescubreAR) or
                            isinstance(juego_actual, JuegoMemoriaAR) or
                            isinstance(juego_actual, JuegoEncuentraFrutasAR) or
                            isinstance(juego_actual, JuegoCategoriasAR)):
            marcadores_a_renderizar = []
            if hasattr(juego_actual, 'obtener_marcadores_renderizado'):
                marcadores_a_renderizar = juego_actual.obtener_marcadores_renderizado()
            ret_pose, pose = detectar_pose(frame_limpio, 0.19, detector, cameraMatrix, distCoeffs)
            if ret_pose and pose:
                for marker_id in marcadores_a_renderizar:
                    if marker_id in marcadores_actuales and marker_id in pose:
                        if marker_id not in escenas:
                            modelo = crear_modelo_por_id(marker_id)
                            escenas[marker_id] = crear_escena(modelo, cameraMatrix,
                                                            int(frame.shape[1]), int(frame.shape[0]))
                        M = from_opencv_to_pygfx(pose[marker_id][0], pose[marker_id][1])
                        escenas[marker_id].actualizar_camara(M)
                        imagen_render = escenas[marker_id].render()
                        imagen_render_bgr = cv2.cvtColor(imagen_render, cv2.COLOR_RGBA2BGRA)
                        frame_visual = alphaBlending(imagen_render_bgr, frame_visual)
        if state.gestor_juegos and state.gestor_juegos.juego_activo:
            state.gestor_juegos.actualizar_marcadores_detectados(marcadores_actuales)
        esperando_voz = False
        juego_actual = getattr(state.gestor_juegos, 'juego_activo', None)
        if juego_actual and hasattr(juego_actual, 'debe_escuchar_voz'):
            esperando_voz = juego_actual.debe_escuchar_voz()
        if isinstance(juego_actual, JuegoDescubreAR):
            if not juego_actual.fase_escaneo_completada:
                tiempo_transcurrido = time.time() - juego_actual.tiempo_escaneo if juego_actual.tiempo_escaneo else 0
                tiempo_restante = max(0, 10 - int(tiempo_transcurrido))
                draw_text_with_background(frame_visual, f"ESCANEO: {tiempo_restante}s",
                                        (50, frame_visual.shape[0]-180),
                                        color=(255, 255, 0), bg_color=(100, 100, 0))
                draw_text_with_background(frame_visual, f"Marcadores: {len(juego_actual.marcadores_detectados_inicial)}",
                                        (50, frame_visual.shape[0]-150),
                                        color=(0, 255, 255), bg_color=(0, 100, 100))
            elif not juego_actual.juego_terminado:
                progreso = len(juego_actual.marcadores_detectados_inicial) - len(juego_actual.marcadores_pendientes) + 1
                total = len(juego_actual.marcadores_detectados_inicial)
                if juego_actual.pregunta_actual:
                    draw_text_with_background(frame_visual, juego_actual.pregunta_actual,
                                            (50, frame_visual.shape[0]-180),
                                            color=(0, 255, 255), bg_color=(100, 0, 100))
                if juego_actual.esperando_nombre:
                    tiempo_esperando = time.time() - juego_actual.tiempo_pregunta if juego_actual.tiempo_pregunta else 0
                    tiempo_restante = max(0, juego_actual.timeout_respuesta - int(tiempo_esperando))
                    draw_text_with_background(frame_visual, f"[MIC] Responde ({tiempo_restante}s)",
                                            (50, frame_visual.shape[0]-150),
                                            color=(255, 255, 255), bg_color=(50, 50, 50))
                draw_text_with_background(frame_visual, f"Progreso: {progreso}/{total}",
                                        (50, frame_visual.shape[0]-120),
                                        color=(255, 165, 0), bg_color=(100, 50, 0))
            elif juego_actual.juego_terminado:
                if hasattr(juego_actual, 'resultado_final') and juego_actual.resultado_final:
                    resultado = juego_actual.resultado_final
                    puntuacion = resultado.get("Puntuación", 0)
                    total = resultado.get("total", 0)
                    precision = resultado.get("precision", 0)
                    draw_text_with_background(frame_visual, f"RESULTADO: {puntuacion}/{total} ({precision:.1f}%)",
                                            (50, frame_visual.shape[0]-150),
                                            color=(0, 255, 255), bg_color=(0, 100, 100))
        elif isinstance(juego_actual, JuegoCategoriasAR):
            if not juego_actual.fase_escaneo_completada:
                tiempo_transcurrido = time.time() - juego_actual.tiempo_escaneo if juego_actual.tiempo_escaneo else 0
                tiempo_restante = max(0, 12 - int(tiempo_transcurrido))
                draw_text_with_background(frame_visual, f"ESCANEO: {tiempo_restante}s",
                                        (50, frame_visual.shape[0]-180),
                                        color=(255, 255, 0), bg_color=(100, 100, 0))
                draw_text_with_background(frame_visual, f"Items: {len(juego_actual.marcadores_detectados_inicial)}/6",
                                        (50, frame_visual.shape[0]-150),
                                        color=(0, 255, 255), bg_color=(0, 100, 100))
            elif not juego_actual.esperando_respuesta and not juego_actual.juego_terminado:
                elementos_presentes = [m for m in marcadores_actuales if m in juego_actual.elementos_juego]
                draw_text_with_background(frame_visual, f"COLOCA ELEMENTOS: {len(elementos_presentes)}/{len(juego_actual.elementos_juego)}",
                                        (50, frame_visual.shape[0]-150),
                                        color=(255, 165, 0), bg_color=(100, 50, 0))
            elif juego_actual.esperando_respuesta and not juego_actual.juego_terminado:
                tiempo_esperando = time.time() - juego_actual.tiempo_pregunta if juego_actual.tiempo_pregunta else 0
                tiempo_restante = max(0, juego_actual.timeout_respuesta - int(tiempo_esperando))
                if juego_actual.categoria_actual == "frutas":
                    tipo_icono = "[FRUTA]"
                    categoria_nombre = "FRUTAS"
                    respuestas_actuales = len(juego_actual.respuestas_frutas)
                    total_categoria = len(juego_actual.frutas_correctas)
                else:
                    tipo_icono = "[VERDURA]"
                    categoria_nombre = "VERDURAS"
                    respuestas_actuales = len(juego_actual.respuestas_verduras)
                    total_categoria = len(juego_actual.verduras_correctas)
                draw_text_with_background(frame_visual, f"{tipo_icono} {categoria_nombre} - {tiempo_restante}s",
                                        (50, frame_visual.shape[0]-180),
                                        color=(255, 255, 0), bg_color=(100, 100, 0))
                draw_text_with_background(frame_visual, f"Encontradas: {respuestas_actuales}/{total_categoria}",
                                        (50, frame_visual.shape[0]-150),
                                        color=(0, 255, 255), bg_color=(0, 100, 100))
            elif juego_actual.juego_terminado:
                if hasattr(juego_actual, 'resultado_final') and juego_actual.resultado_final:
                    resultado = juego_actual.resultado_final
                    total_correctas = resultado.get("total_correctas", 0)
                    total_elementos = resultado.get("total_elementos", 0)
                    porcentaje = resultado.get("porcentaje", 0)
                    draw_text_with_background(frame_visual, f"RESULTADO: {total_correctas}/{total_elementos} ({porcentaje:.1f}%)",
                                            (50, frame_visual.shape[0]-150),
                                            color=(0, 255, 255), bg_color=(0, 100, 100))
        state.esperando_voz = esperando_voz
        if state.gestor_juegos:
            state.gestor_juegos.dibujar_interfaz(frame_visual)
        if state.esperando_voz:
            draw_text_with_background(frame_visual, "[VOZ] VOZ ACTIVA",
                                    (frame_visual.shape[1] - 200, 30), font_scale=0.5,
                                    color=(0, 255, 0), bg_color=(0, 100, 0))
        if isinstance(juego_actual, JuegoDescubreAR) and juego_actual.juego_terminado:
            if not getattr(juego_actual, "puntuacion_guardada", False):
                from modules.usuarios import guardar_puntuacion_juego
                modo = state.gestor_juegos.modo_actual
                nombre_juego = juego_actual.obtener_nombre()
                if hasattr(juego_actual, 'resultado_final') and juego_actual.resultado_final:
                    puntuacion = int(juego_actual.resultado_final.get('precision', 0))
                else:
                    puntuacion_raw = getattr(juego_actual, 'puntuacion', 0)
                    intentos = getattr(juego_actual, 'intentos', 1)
                    puntuacion = int((puntuacion_raw / intentos) * 100) if intentos > 0 else 0
                exito = guardar_puntuacion_juego(nombre, modo, nombre_juego, puntuacion)
                if exito:
                    juego_actual.puntuacion_guardada = True
                    print(f"[OK] Puntuación guardada: {puntuacion}% para {nombre_juego}")
        if isinstance(juego_actual, JuegoCategoriasAR) and juego_actual.juego_terminado:
            if not getattr(juego_actual, "puntuacion_guardada", False):
                from modules.usuarios import guardar_puntuacion_juego
                modo = state.gestor_juegos.modo_actual
                nombre_juego = juego_actual.obtener_nombre()
                if hasattr(juego_actual, 'resultado_final') and juego_actual.resultado_final:
                    puntuacion = int(juego_actual.resultado_final.get('porcentaje', 0))
                else:
                    puntuacion_raw = getattr(juego_actual, 'puntuacion', 0)
                    intentos = getattr(juego_actual, 'intentos', 1)
                    puntuacion = int((puntuacion_raw / intentos) * 100) if intentos > 0 else 0
                exito = guardar_puntuacion_juego(nombre, modo, nombre_juego, puntuacion)
                if exito:
                    juego_actual.puntuacion_guardada = True
                    print(f"[OK] Puntuación guardada: {puntuacion}% para {nombre_juego}")
        instrucciones = []
        if isinstance(juego_actual, JuegoDescubreAR):
            if not juego_actual.fase_escaneo_completada:
                instrucciones.append("Muestra marcadores uno por uno")
            elif not juego_actual.juego_terminado:
                if juego_actual.marcador_actual:
                    instrucciones.append(f"Busca marcador ID: {juego_actual.marcador_actual}")
                if juego_actual.esperando_nombre:
                    instrucciones.append("Di el nombre en voz alta")
            elif juego_actual.juego_terminado:
                instrucciones.append("'otra vez' para repetir | 'salir' para menú")
        elif isinstance(juego_actual, JuegoCategoriasAR):
            if not juego_actual.fase_escaneo_completada:
                instrucciones.append("Muestra 6 marcadores diferentes")
            elif not juego_actual.esperando_respuesta and not juego_actual.juego_terminado:
                instrucciones.append("Coloca todos los elementos")
            elif juego_actual.esperando_respuesta:
                categoria = juego_actual.categoria_actual
                instrucciones.append(f"Di todas las {categoria}")
                instrucciones.append("'siguiente' para cambiar | 'listo' para terminar")
            elif juego_actual.juego_terminado:
                instrucciones.append("'otra vez' para repetir | 'salir' para menú")
        for i, instruccion in enumerate(instrucciones):
            y_offset = 80 + (i * 25)
            draw_text_with_background(frame_visual, instruccion,
                                    (50, frame_visual.shape[0] - y_offset), font_scale=0.5,
                                    color=(200, 200, 200), bg_color=(50, 50, 50))
        return frame_visual
    return frame