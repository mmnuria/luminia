# ui_renderer.py
import cv2
import face_recognition
import time
import random

from models.modelos import crear_modelo, obtener_ruta_por_categoria, rutas_mascota
from ar.escena import crear_escena
from ar.deteccion import detectar_pose
from utils.conversiones import from_opencv_to_pygfx
from utils.operaciones import alphaBlending
from modules.game_state import FACE_CASCADE

from modules.usuarios import Usuario
from modules.data_manager import MongoDBManager

mongo = MongoDBManager()

traduccion_mascotas = {
    "Bear": "Oso",
    "Cat": "Gato",
    "Chicken": "Pollo",
    "Crocodile": "Cocodrilo",
    "Deer": "Ciervo",
    "Dragon": "Dragon",
    "Duck": "Pato",
    "Eagle": "Aguila",
    "Fish": "Pez",
    "Flamingo": "Flamenco",
    "Fox": "Zorro",
    "Giraffe": "Jirafa",
    "Gorilla": "Gorila",
    "Hippo": "Hipopotamo",
    "Koala": "Koala",
    "Lion": "Leon",
    "Monkey": "Mono",
    "Octopus": "Pulpo",
    "Owl": "Buho",
    "Panda": "Panda",
    "Penguin": "Pinguino",
    "Raccoon": "Mapache",
    "Rabbit": "Conejo",
    "Rat": "Rata",
    "Seel": "Foca",
    "Shark": "Tiburon",
    "Tiger": "Tigre",
    "Zebra": "Cebra",
    "tina_unicornio": "Unicornio",
    "Bee": "Abeja",
    "Butterfly": "Mariposa",
    "Horn_beetle": "Escarabajo",
}

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
    ret, pose = detectar_pose(frame, 0.18, detector, cameraMatrix, distCoeffs)
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
# Mostrar disfraces en columnas
def mostrar_disfraces_como_columnas(frame, lista_disfraces, inicio_y, titulo, color_texto, bg_color_texto, columnas=3):
    draw_text_with_background(frame, titulo, (50, inicio_y - 30), color=(255,255,255), bg_color=(80,60,120))
    x_base = 50
    y = inicio_y
    x = x_base
    contador = 0

    for disfraz in lista_disfraces:
        nombre_traducido = traduccion_mascotas.get(disfraz, disfraz)
        draw_text_with_background(frame, nombre_traducido, (x, y),
                                color=color_texto, bg_color=bg_color_texto)
        x += 200  # distancia entre columnas
        contador += 1
        if contador % columnas == 0:
            x = x_base
            y += 40  # salto de fila

# ---------------------------------------------------
# Renderizado de realidad mixta
# ---------------------------------------------------

def realidad_mixta(frame, detector, cameraMatrix, distCoeffs, state, escenas):
    """
    Renderiza los modelos 3D sobre los marcadores según el estado actual.
    """
    ret, pose = detectar_pose(frame, 0.25, detector, cameraMatrix, distCoeffs)
    marcadores_actuales = set(pose.keys()) if ret and pose else set()
    mundo_anterior = None

    # ---------------------------------------------------
    # Siempre mostrar Tina en marcador 0
    # ---------------------------------------------------
    if 0 in marcadores_actuales and state.fase != "jugando":
        if 0 not in escenas:
            # Valor por defecto
            equipado = "tina_unicornio"

            if state.usuario_actual:
                datos_usuario = mongo.obtener_datos_usuario(state.usuario_actual)
                disfraces = datos_usuario.get("disfraces", {})
                if disfraces:
                    equipado_db = disfraces.get("equipado")
                    if equipado_db and isinstance(equipado_db, str):
                        # Normalizar usando las claves exactas de traduccion_mascotas
                        if equipado_db in traduccion_mascotas:
                            equipado = equipado_db
                        else:
                            # Intentar buscar sin distinguir mayúsculas/minúsculas
                            for clave in traduccion_mascotas.keys():
                                if clave.lower() == equipado_db.lower():
                                    equipado = clave
                                    break

            # Cargar la ruta correspondiente del disfraz equipado
            ruta_tina = obtener_ruta_por_categoria("mascota", equipado)
            if ruta_tina:
                modelo = crear_modelo(ruta_tina)
                escenas[0] = crear_escena(modelo, cameraMatrix, frame.shape[1], frame.shape[0])
            else:
                print(f"[UIRenderer] ⚠️ No se encontró ruta para disfraz '{equipado}'")

        # Actualizar posición del modelo en la cámara
        M = from_opencv_to_pygfx(pose[0][0], pose[0][1])
        escenas[0].actualizar_camara(M)

        # Renderizar y mezclar con el frame
        imagen_render = escenas[0].render()
        imagen_render_bgr = cv2.cvtColor(imagen_render, cv2.COLOR_RGBA2BGRA)
        frame = alphaBlending(imagen_render_bgr, frame.copy())


    # ---------------------------------------------------
    # Mostrar indicador de micrófono (en cualquier fase)
    # ---------------------------------------------------
    if getattr(state, "esperando_voz", False) and getattr(state, "microfono_listo", False):
        h, w, _ = frame.shape
        texto = "Escuchando..."
        # posición en esquina inferior derecha con margen de 20 px
        pos = (w - 350, h - 40)
        draw_text_with_background(
            frame,
            texto,
            pos,
            color=(255, 255, 255),
            bg_color=(50, 120, 50)
        )

    # ---------------------------------------------------
    # FASE: INICIO
    # ---------------------------------------------------
    if state.fase == "inicio":
        draw_text_with_background(frame, "Bienvenido a Luminia, la tierra del aprendizaje magico !!!", (50, 60),
                                  color=(255, 255, 255), bg_color=(56, 118, 29))
        draw_text_with_background(frame, "Escucha a Tina y sabras que hacer a continuacion...", (50, 100),
                                  color=(255, 255, 0), bg_color=(100, 100, 0))
        return frame

    # ---------------------------------------------------
    # FASE: RECONOCIMIENTO FACIAL
    # ---------------------------------------------------
    if state.fase == "reconocimiento_facial":
        draw_text_with_background(frame, "Inicia sesion o registrate", (50, 60),
                                  color=(255, 255, 255), bg_color=(56, 118, 29))
        
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

                draw_text_with_background(frame, "Cara detectada", (x, y - 15),
                                          color=(0, 255, 0), bg_color=(0, 100, 0))
                draw_text_with_background(frame, "Di 'iniciar sesion' o 'registrarme'", (50, 100),
                                          color=(255, 255, 255), bg_color=(0, 0, 100))
                if state.fase != "reconocimiento_facial":
                    state.fase = "reconocimiento_facial"
                    state.esperando_voz = True
            else:
                draw_text_with_background(frame, "Error procesando cara", (x, y - 15),
                                          color=(255, 255, 255), bg_color=(200, 50, 50))
        else:
            draw_text_with_background(frame, "Mira a la camara para comenzar", (50, 100),
                                      color=(255, 255, 255), bg_color=(100, 100, 100))
            state.cara_detectada = False
        
        return frame

    # ---------------------------------------------------
    # FASE: MENU PRINCIPAL
    # ---------------------------------------------------
    if state.fase == "menu_principal":

         # --- LIMPIAR ESCENAS DE MUNDOS ANTERIORES ---
        if mundo_anterior != None:
            modelos_actuales = [m[2] for m in getattr(mundo_anterior, "modelos_a_mostrar", [])]
            for marker_id in list(escenas.keys()):
                if marker_id not in modelos_actuales:
                    escenas.pop(marker_id)

        draw_text_with_background(frame, "Bienvenido a Luminia!", (50, 60),
                                  color=(255, 255, 255), bg_color=(56, 118, 29))
        draw_text_with_background(frame, "Revisa tu perfil di: 'perfil'", (50, 100),
                                  color=(255, 255, 0), bg_color=(100, 100, 0))
        draw_text_with_background(frame, "Revisa tu progreso di: 'progreso'", (50, 140),
                                  color=(255, 255, 0), bg_color=(100, 100, 0))
        draw_text_with_background(frame, "Accede a los disfraces de Tina, di: 'disfraces'", (50, 180),
                                  color=(255, 255, 0), bg_color=(100, 100, 0))
        draw_text_with_background(frame, "Elige el mundo que quieres visitar", (50, 220),
                                  color=(255, 255, 0), bg_color=(100, 100, 0))
        draw_text_with_background(frame, "Di: letras, animales, frutas y verduras, numeros o final", (50, 260),
                                  color=(255, 255, 255), bg_color=(0, 0, 100))

        # Mostrar lumios y estrellas_totales del usuario salvo en fases "inicio" y "reconocimiento_facial"
        if hasattr(state, "fase") and state.fase not in ["inicio", "reconocimiento_facial"]:
            if hasattr(state, "usuario_actual") and state.usuario_actual:
                nombre_usuario = str(state.usuario_actual)  # Asumimos que es el _id o nombre del usuario

                # Obtener datos directamente desde MongoDB
                lumios = mongo.obtener_lumios(nombre_usuario)
                estrellas = int(mongo.obtener_estrellas(nombre_usuario))
                nombre = mongo.obtener_nombre(nombre_usuario)

                texto = f"Lumios: {lumios}   Destellos: {estrellas}"
                (h, w) = frame.shape[:2]
                pos_x = w - 400  # 250 px desde la derecha
                pos_y = 30       # 30 px desde arriba
                draw_text_with_background(frame, texto, (pos_x, pos_y),
                                        color=(255, 255, 255), bg_color=(50, 50, 50, 200))
            else:
                print("[ui_renderer] Advertencia: no hay usuario definido")

        
        # Mostrar los castillos en los marcadores configurados
        marcadores_castillos = getattr(state, "marcadores_castillos", {
            1: "letras", 4: "animales", 6: "fruta_y_verdura", 9: "numeros", 12: "final"
        })

         # Recorremos cada castillo y lo mostramos
        for marker_id, mundo in marcadores_castillos.items():
            desbloqueado = state.mundos_desbloqueados.get(mundo, False)
            ruta = obtener_ruta_por_categoria("castillo", mundo, desbloqueado)

            if not ruta:
                continue  # seguridad

            # Crear modelo si no existe ya
            if marker_id not in escenas:
                modelo = crear_modelo(ruta)
                escenas[marker_id] = crear_escena(modelo, cameraMatrix, frame.shape[1], frame.shape[0])

            # Mostrar el castillo si su marcador está visible
            if marker_id in marcadores_actuales:
                M = from_opencv_to_pygfx(pose[marker_id][0], pose[marker_id][1])
                escenas[marker_id].actualizar_camara(M)
                imagen_render = escenas[marker_id].render()
                imagen_render_bgr = cv2.cvtColor(imagen_render, cv2.COLOR_RGBA2BGRA)
                frame = alphaBlending(imagen_render_bgr, frame)

        return frame

    # ---------------------------------------------------
    # FASE: PERFIL.
    # ---------------------------------------------------
    if state.fase == "perfil":
        datos = getattr(state, "datos_perfil", {})
        draw_text_with_background(frame, "PERFIL DE USUARIO", (50, 60),
                                color=(255, 255, 255), bg_color=(50, 80, 150))
        
        y = 100
        # Solo mostrar nombre, idioma y fecha_registro
        campos_a_mostrar = ["nombre", "idioma", "fecha_registro"]
        traducciones = {"nombre": "Nombre", "idioma": "Idioma", "fecha_registro": "Fecha de registro"}
        
        for clave in campos_a_mostrar:
            valor = datos.get(clave, "N/A")
            draw_text_with_background(frame, f"{traducciones[clave]}: {valor}", (50, y),
                                    color=(255, 255, 0), bg_color=(0, 60, 60))
            y += 40 
        
        draw_text_with_background(frame, "Di 'atras' para regresar", (50, y + 20),
                                color=(255, 255, 255), bg_color=(100, 60, 20))
        return frame

    # ---------------------------------------------------
    # FASE: PROGRESO
    # ---------------------------------------------------
    if state.fase == "progreso":
        progreso = getattr(state, "datos_progreso", {})

        draw_text_with_background(
            frame, "PROGRESO GENERAL", (50, 60),
            color=(255, 255, 255), bg_color=(60, 40, 100)
        )

        y = 110
        estrellas_totales_total = progreso.get("estrellas_totales", 0)

        # Iteramos por mundos, evitando el campo global de estrellas
        for mundo, datos in progreso.items():
            if mundo == "estrellas_totales" or not isinstance(datos, dict):
                continue

            # Título del mundo
            draw_text_with_background(
                frame, f"Mundo {mundo.capitalize()}", (50, y),
                color=(255, 255, 255), bg_color=(40, 80, 120)
            )
            y += 35

            # Minijuegos dentro del mundo
            for juego, estrellas in datos.items():
                if juego == "total_estrellas":
                    continue
                draw_text_with_background(
                    frame, f"- {juego.capitalize()}: {estrellas} destellos",
                    (80, y), color=(255, 255, 0), bg_color=(80, 60, 20)
                )
                y += 25

            # Total por mundo
            total = datos.get("total_estrellas", 0)
            draw_text_with_background(
                frame, f"Total: {total}", (80, y),
                color=(0, 255, 255), bg_color=(60, 60, 60)
            )
            y += 40

        draw_text_with_background(
            frame, f"Destellos totales: {estrellas_totales_total}", (50, y + 10),
            color=(255, 255, 255), bg_color=(100, 80, 20)
        )
        y += 50

        draw_text_with_background(
            frame, "Di 'atras' para regresar", (50, y + 20),
            color=(255, 255, 255), bg_color=(100, 60, 20)
        )
        return frame


    # ---------------------------------------------------
    # FASE: DISFRACES
    # ---------------------------------------------------
    if state.fase == "disfraces":
        disfraces = getattr(state, "datos_disfraces", {})
        comprados = disfraces.get("disponibles", [])
        equipado = disfraces.get("equipado", None)

        todas_las_mascotas = list(rutas_mascota.keys())
        disponibles_para_comprar = [d for d in todas_las_mascotas if d not in comprados]

        # Títulos principales
        draw_text_with_background(frame, "BIENVENIDO A TU ARMARIO", (50, 60),
                                color=(255, 255, 255), bg_color=(120, 60, 140))
        draw_text_with_background(frame, f"Equipado actualmente: {traduccion_mascotas.get(equipado, equipado) if equipado else 'Ninguno'}",
                                (50, 100), color=(255, 255, 0), bg_color=(100, 60, 60))

        # Mostrar comprados
        mostrar_disfraces_como_columnas(frame, comprados, 180,
                                        "Disfraces comprados:",
                                        color_texto=(0, 255, 0), bg_color_texto=(50,100,50))

        # Mostrar disponibles para comprar
        mostrar_disfraces_como_columnas(frame, disponibles_para_comprar, 350,
                                        "Disfraces disponibles para comprar:",
                                        color_texto=(255, 255, 0), bg_color_texto=(80,80,80))

        draw_text_with_background(frame, "Di 'atras' para regresar", (50, -550),
                                color=(255, 255, 255), bg_color=(100, 60, 20))

        return frame




    # ---------------------------------------------------
    # FASE: MUNDO_X (letras, animales, frutas, números, final)
    # ---------------------------------------------------
    if state.fase.startswith("mundo_"):
        mundo = state.fase.split("_", 1)[1]
        draw_text_with_background(frame, f"Estamos en el Mundo de las {mundo.replace('_', ' ').capitalize()}",
                                  (50, 60), color=(255, 255, 255), bg_color=(56, 118, 29))
        
        draw_text_with_background(frame, "Di el minijuego que quieres jugar o 'salir' para volver.",
                                  (50, 100), color=(255, 255, 0), bg_color=(100, 100, 0))
        
        # Mostrar los minijuegos disponibles según el mundo
        minijuegos = {
            "letras": ["Adivina", "Memoria", "Seuencia"],
            "animales": ["Adivina", "Sonido", "Clasificar"],
            "fruta_y_verdura": ["Adivina", "Color", "Clasifica"],
            "numeros": ["Adivina", "Suma", "Mayor"],
            "final": ["Contar", "Secuencia", "Deletreo"]
        }

        # Obtener la lista de minijuegos correspondientes al mundo actual
        minijuegos_disponibles = minijuegos.get(mundo.lower(), [])

        # Dibujar los minijuegos disponibles
        if minijuegos_disponibles:
            y_offset = 140
            for juego in minijuegos_disponibles:
                draw_text_with_background(
                    frame,
                    f"- {juego}",
                    (70, y_offset),
                    color=(255, 255, 255),
                    bg_color=(0, 100, 100)
                )
                y_offset += 30
        else:
            draw_text_with_background(
                frame,
                "No hay minijuegos disponibles para este mundo.",
                (70, 140),
                color=(255, 0, 0),
                bg_color=(50, 0, 0)
            )

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
        draw_text_with_background(frame, "Jugando... Di 'atras' para volver al menu principal", (50, 60),
                                color=(255, 255, 255), bg_color=(56, 118, 29))

        # Seleccionar la instancia del mundo activo
        mundo_activo = getattr(state, f"instancia_mundo_{state.mundo_actual}", None)
        mundo_anterior = mundo_activo

        if mundo_activo:
            # --- LIMPIAR ESCENAS DE MUNDOS ANTERIORES ---
            modelos_actuales = [m[2] for m in getattr(mundo_activo, "modelos_a_mostrar", [])]
            for marker_id in list(escenas.keys()):
                if marker_id not in modelos_actuales:
                    escenas.pop(marker_id)
            
            pose = pose or {}
            
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
                
            # --- Mostrar mensajes de minijuego en pantalla ---
            if hasattr(mundo_activo, "juego_en_curso"):
                # MUNDO LETRAS
                if state.mundo_actual == "letras" and mundo_activo.juego_en_curso == "adivina":
                    draw_text_with_background(frame, "Letras magicas aparecieron:", (50, 120),
                                            color=(255, 255, 255), bg_color=(80, 40, 120))
                    draw_text_with_background(frame, "Di la respuesta diciendo: Letra A, Letra B, etc.",
                                            (50, 160), color=(255, 255, 0), bg_color=(100, 80, 20))

                elif state.mundo_actual == "letras" and mundo_activo.juego_en_curso == "memoria":
                    draw_text_with_background(frame, "Observa con atencion las letras magicas...",
                                            (50, 120), color=(255, 255, 255), bg_color=(40, 100, 100))
                    draw_text_with_background(frame, "Di las letras en orden: Letras A B C ...",
                                            (50, 160), color=(255, 255, 0), bg_color=(80, 80, 20))

                elif state.mundo_actual == "letras" and mundo_activo.juego_en_curso == "secuencia":
                    draw_text_with_background(frame, "Vamos a formar una palabra magica.",
                                            (50, 120), color=(255, 255, 255), bg_color=(100, 60, 20))
                    draw_text_with_background(frame, "Forma una palabra con las letras que ves en el tablero.",
                                            (50, 160), color=(255, 255, 0), bg_color=(120, 80, 30))
                # MUNDO ANIMALES
                if state.mundo_actual == "animales":
                    if mundo_activo.juego_en_curso == "adivina":
                        draw_text_with_background(frame, "Observa bien el animal que aparece...", (50, 120),
                                                color=(255, 255, 255), bg_color=(60, 100, 40))
                        draw_text_with_background(frame, "¿Que animal ves sobre la mesa magica? Di, perro, gato... ",
                                                (50, 160), color=(255, 255, 0), bg_color=(100, 80, 20))

                    elif mundo_activo.juego_en_curso == "sonido":
                        draw_text_with_background(frame, "🔊 Escucha con atencion...", (50, 120),
                                                color=(255, 255, 255), bg_color=(40, 80, 120))
                        draw_text_with_background(frame, "¿Que animal hace ese sonido?, di perro, gato, ...",
                                                (50, 160), color=(255, 255, 0), bg_color=(120, 80, 20))

                    elif mundo_activo.juego_en_curso == "clasificar":
                        # Mostrar pregunta según la ronda actual
                        if mundo_activo.ronda_actual == 0:
                            mensaje = "Selecciona el animal que vive en tierra."
                        elif mundo_activo.ronda_actual == 1:
                            mensaje = "Selecciona el animal que vive en el agua."
                        else:
                            mensaje = "Selecciona el animal que puede volar."

                        draw_text_with_background(frame, mensaje, (50, 120),
                                                color=(255, 255, 255), bg_color=(80, 60, 120))
                        draw_text_with_background(frame, "Di el nombre del animal correcto, perro, gato ...",
                                                (50, 160), color=(255, 255, 0), bg_color=(100, 80, 20))
                # MUNDO FRUTAS Y VERDURAS
                if state.mundo_actual == "fruta_y_verdura":
                    
                    if mundo_activo.juego_en_curso == "adivina":
                        draw_text_with_background(frame, "Ha aparecido un alimento...", (50, 120),
                                                color=(255, 255, 255), bg_color=(80, 40, 120))
                        draw_text_with_background(frame, "¿Que alimento es este? Di: pera, platano ...",
                                                (50, 160), color=(255, 255, 0), bg_color=(100, 80, 20))

                    elif mundo_activo.juego_en_curso == "color":
                        color_pedido = getattr(mundo_activo, "color_pedido", None)

                        draw_text_with_background(frame, "Observa con atencion los alimentos...", (50, 120),
                                                color=(255, 255, 255), bg_color=(40, 100, 100))
                        
                        if color_pedido:
                            draw_text_with_background(
                                frame,
                                f"¿Cual de ellos es de color {color_pedido.upper()}?",
                                (50, 160),
                                color=(255, 255, 0),
                                bg_color=(80, 80, 20)
                            )
                        else:
                            draw_text_with_background(
                                frame,
                                "Espera un momento... preparando el reto de color.",
                                (50, 160),
                                color=(255, 255, 0),
                                bg_color=(80, 80, 20)
                            )

                    elif mundo_activo.juego_en_curso == "clasifica":
                        draw_text_with_background(frame, "Observa bien el alimento que ha aparecido...", (50, 120),
                                                color=(255, 255, 255), bg_color=(60, 80, 120))
                        draw_text_with_background(frame, "¿Es una FRUTA o una VERDURA? Di: fruta o Alimento verdura.",
                                                (50, 160), color=(255, 255, 0), bg_color=(100, 80, 20))
                # MUNDO NÚMEROS
                if state.mundo_actual == "numeros":
                    
                    if mundo_activo.juego_en_curso == "adivina":
                        draw_text_with_background(frame, "Observa los numeros que han aparecido...", (50, 120),
                                                color=(255, 255, 255), bg_color=(80, 40, 120))
                        draw_text_with_background(frame, "¿Que numero ves? Di: Numero 3, Numero 10, Numero 25...", 
                                                (50, 160), color=(255, 255, 0), bg_color=(100, 80, 20))

                    elif mundo_activo.juego_en_curso == "suma":
                        draw_text_with_background(frame, "Observa los numeros que aparecen...", (50, 120),
                                                color=(255, 255, 255), bg_color=(60, 100, 60))
                        draw_text_with_background(frame, "¿Cual es el resultado de su suma?: Numero 4, Numero 7, Numero 12...",
                                                (50, 160), color=(255, 255, 0), bg_color=(100, 80, 20))

                    elif mundo_activo.juego_en_curso == "mayor":
                        draw_text_with_background(frame, "Mira los numeros sobre la mesa magica...", (50, 120),
                                                color=(255, 255, 255), bg_color=(40, 80, 120))
                        draw_text_with_background(frame, "¿Cual es el numero MAYOR? Di: Numero 5, Numero 9, Numero 2...",
                                                (50, 160), color=(255, 255, 0), bg_color=(100, 80, 20))
                        
                # MUNDO FINAL
                if state.mundo_actual == "final":
                    
                    if mundo_activo.juego_en_curso == "contar":
                    # Intentar mostrar el nombre del objeto elegido
                        try:
                            objeto_elegido = mundo_activo._mostrar_nombre_en_es(
                                mundo_activo.modelos_a_mostrar[0][1]
                            ).upper()
                        except Exception:
                            objeto_elegido = "objetos"

                        draw_text_with_background(frame, "Observa bien los objetos que aparecen...", (50, 120),
                                                color=(255, 255, 255), bg_color=(80, 60, 140))
                        draw_text_with_background(
                            frame,
                            f"¿Cuantos {objeto_elegido}s hay? Di: Hay tres, Hay cuatro, Hay dos...",
                            (50, 160),
                            color=(255, 255, 0),
                            bg_color=(100, 80, 20)
                        )

                    elif mundo_activo.juego_en_curso == "secuencia":
                        draw_text_with_background(frame, "Mira la secuencia...", (50, 120),
                                                color=(255, 255, 255), bg_color=(60, 120, 100))
                        draw_text_with_background(frame, "Repite en orden lo que ves: Manzana perro dos plátano...", 
                                                (50, 160), color=(255, 255, 0), bg_color=(100, 80, 20))

                    # --- Minijuego "deletreo" ---
                    elif mundo_activo.juego_en_curso == "deletreo":
                        draw_text_with_background(frame, "Observa el objeto sobre la mesa...", (50, 120),
                                                color=(255, 255, 255), bg_color=(100, 60, 100))
                        draw_text_with_background(frame, "Deletrea su nombre: Di las letras una por una, por ejemplo: M-A-N-Z-A-N-A.",
                                                (50, 160), color=(255, 255, 0), bg_color=(100, 80, 20))
                # --- Mostrar mensaje temporal (si existe) ---
                if state.mensaje_pantalla and time.time() < state.tiempo_mensaje:
                    draw_text_with_background(
                        frame,
                        state.mensaje_pantalla,
                        (50, 200),
                        color=(255, 255, 255),
                        bg_color=(0, 120, 60)
                    )
                    time.sleep(2)
                else:
                    state.mensaje_pantalla = None


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
