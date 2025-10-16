# voice_recognition.py
import speech_recognition as sr
import time
import traceback

from modules.usuarios import (
    buscar_usuario_por_cara,
    verificar_usuario_existe,
    registrar_usuario,
    actualizar_nombre_usuario,
    actualizar_idioma_usuario,
)

# -------------------------
# Config / helpers
# -------------------------
def inicializar_microfono(state, recognizer, microphone):
    """
    Configura parámetros del recognizer y marca el micrófono como listo en el state.
    """
    try:
        print(" Inicializando micrófono...")
        recognizer.energy_threshold = 4000
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8
        recognizer.phrase_threshold = 0.3
        state.microfono_listo = True
        print("***** Micrófono listo *****")
    except Exception as e:
        print(f"xxxxxx Error configurando micrófono: {e} xxxxxxx")
        state.microfono_listo = False


def reconocimiento_voz(state, recognizer, microphone, voice_thread_active):
    """
    Bucle principal de reconocimiento adaptado al flujo:
    inicio -> reconocimiento_facial -> menu_principal -> mundo_X -> jugando
    - state: objeto compartido con atributos de fase, esperando_voz, etc.
    - recognizer, microphone: objetos de speech_recognition
    - voice_thread_active: lista/objeto mutable que indica si el hilo debe seguir (ej: [True])
    """
    print("[voz] hilo de reconocimiento iniciado")

    # 🟢 Asegurar que el micrófono se marca como listo al inicio
    if not hasattr(state, "microfono_listo"):
        state.microfono_listo = True
    if not hasattr(state, "esperando_voz"):
        state.esperando_voz = True

    while voice_thread_active[0]:
        # solo intentar reconocimiento si el sistema quiere escuchar y el micrófono está listo
        if not (getattr(state, "esperando_voz", False) and getattr(state, "microfono_listo", False)):
            time.sleep(0.12)
            continue

        try:
            fase = getattr(state, "fase", "inicio")
            print(f"[voz] escuchando en fase: {fase}")

            # Parámetros adaptativos por fase
            timeout = 6 if "nombre" in fase else 4
            phrase_limit = 7 if "nombre" in fase else 5

            with microphone as source:
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)

            texto = recognizer.recognize_google(audio, language="es-ES").lower().strip()
            print(f"[voz] detectado: '{texto}'")

            if hasattr(state, "error_mensaje"):
                delattr(state, "error_mensaje")

            # ---------- Fase: inicio ----------
            if fase == "inicio":
                if getattr(state, "intro_terminado", False) or any(k in texto for k in ["continuar", "empezar", "comenzar"]):
                    state.fase = "reconocimiento_facial"
                    state.esperando_voz = True  # 🟢 dejamos activado para escuchar de inmediato
                    state.microfono_listo = True
                    print("➡️ Transición: inicio -> reconocimiento_facial")
                else:
                    state.error_mensaje = "Di 'continuar' para seguir."
                    state.esperando_voz = True
                    state.microfono_listo = True

            # ---------- Fase: reconocimiento_facial ----------
            elif fase == "reconocimiento_facial":
                if "iniciar sesión" in texto or "iniciar sesion" in texto or ("iniciar" in texto and "sesión" in texto):
                    print("[voz] petición iniciar sesión por voz")
                    if hasattr(state, "vector_facial_actual"):
                        nombre_encontrado, datos_usuario = buscar_usuario_por_cara(state.vector_facial_actual)
                        if nombre_encontrado:
                            state.usuario_nombre = nombre_encontrado
                            state.usuario_data = datos_usuario
                            state.sesion_iniciada = True
                            state.fase = "menu_principal"
                            state.esperando_voz = True   # 🟢 micrófono listo al llegar al menú
                            state.microfono_listo = True
                            print(f"[auth] sesión iniciada: {nombre_encontrado} -> menu_principal")
                        else:
                            state.error_mensaje = "Cara no registrada. Di 'registrarme' para crear cuenta."
                            state.esperando_voz = True
                            state.microfono_listo = True
                    else:
                        state.error_mensaje = "No se detectó la cara. Mira a la cámara."
                        state.esperando_voz = True
                        state.microfono_listo = True

                elif "registrar" in texto or "registrarme" in texto or "crear cuenta" in texto:
                    state.fase = "esperando_nombre_registro"
                    state.esperando_voz = True
                    state.microfono_listo = True
                    print("➡️ Transición: reconocimiento_facial -> esperando_nombre_registro")

                else:
                    state.error_mensaje = "Di 'iniciar sesión' o 'registrarme'."
                    state.esperando_voz = True
                    state.microfono_listo = True

            # ---------- Fase: esperando_nombre_registro ----------
            elif fase == "esperando_nombre_registro":
                nombre = texto.strip().title()
                print(f"[registro] nombre detectado: '{nombre}'")
                if len(nombre) >= 2:
                    if verificar_usuario_por_nombre_existente(nombre=nombre):
                        state.error_mensaje = f"El nombre '{nombre}' ya existe. Di otro nombre."
                        state.esperando_voz = True
                        state.microfono_listo = True
                    else:
                        state.usuario_nombre = nombre
                        state.fase = "esperando_idioma_registro"
                        state.esperando_voz = True
                        state.microfono_listo = True
                        print(f"[registro] nombre ok -> pedir idioma para {nombre}")
                else:
                    state.error_mensaje = "Nombre demasiado corto. Intenta de nuevo."
                    state.esperando_voz = True
                    state.microfono_listo = True

            # ---------- Fase: esperando_idioma_registro ----------
            elif fase == "esperando_idioma_registro":
                idiomas_disponibles = {
                    "español": "es", "castellano": "es", "espanol": "es",
                    "inglés": "en", "ingles": "en", "english": "en"
                }
                idioma_texto = texto.strip().lower()
                idioma_codigo = idiomas_disponibles.get(idioma_texto)
                if idioma_codigo:
                    if hasattr(state, "vector_facial_actual"):
                        datos = registrar_usuario(state.usuario_nombre, idioma_codigo, state.vector_facial_actual)
                        if datos:
                            state.usuario_data = datos
                            state.registro_exitoso = True
                            state.fase = "menu_principal"
                            state.esperando_voz = True   # 🟢 dejamos el micrófono activo al terminar el registro
                            state.microfono_listo = True
                            print(f"[registro] usuario '{state.usuario_nombre}' registrado -> menu_principal")
                        else:
                            state.error_mensaje = "Error registrando usuario. Intenta de nuevo."
                            state.esperando_voz = True
                            state.microfono_listo = True
                    else:
                        state.error_mensaje = "No se detectó la cara para registrar."
                        state.esperando_voz = True
                        state.microfono_listo = True
                else:
                    state.error_mensaje = "Idioma no válido. Di 'español' o 'inglés'."
                    state.esperando_voz = True
                    state.microfono_listo = True

            # ---------- Fase: menu_principal ----------
            elif fase == "menu_principal":
                palabra = texto.strip().lower()
                mapping_mundos = {
                    "letras": "letras",
                    "animales": "animales",
                    "fruta": "fruta_y_verdura",
                    "frutas": "fruta_y_verdura",
                    "fruta y verdura": "fruta_y_verdura",
                    "fruta y verduras": "fruta_y_verdura",
                    "verdura": "fruta_y_verdura",
                    "verduras": "fruta_y_verdura",
                    "números": "numeros",
                    "numeros": "numeros",
                    "final": "final",
                    "mundo final": "final",
                }
                elegido = None
                for k, v in mapping_mundos.items():
                    if k in palabra:
                        elegido = v
                        break

                if elegido:
                    if hasattr(state, "gestor_juegos") and state.gestor_juegos:
                        print(f"[menu] petición elección mundo: {elegido}")
                        state.gestor_juegos.procesar_comando_voz(elegido)
                        # 🟢 Activamos por seguridad el micrófono tras cargar el mundo
                        state.esperando_voz = True
                        state.microfono_listo = True
                    else:
                        state.error_mensaje = "Sistema no listo. Gestor no inicializado."
                        state.esperando_voz = True
                        state.microfono_listo = True
                elif any(x in palabra for x in ["salir", "cerrar", "volver"]):
                    state.fase = "inicio"
                    state.esperando_voz = True
                    state.microfono_listo = True
                    print("[menu] comando salir -> inicio")
                else:
                    state.error_mensaje = "Di el mundo que quieres: letras, animales, fruta y verdura, números o final."
                    state.esperando_voz = True
                    state.microfono_listo = True

            # ---------- Fase: mundo_<nombre> ----------
            elif fase.startswith("mundo_"):
                palabra = texto.strip().lower()
                comandos_minijuego = [
                    "adivina", "memoria", "secuencia", "reto", "desafio", "desafío",
                    "sonido", "clasificacion", "contar", "suma", "mayor", "descubre", "encuentra"
                ]
                if any(cmd in palabra for cmd in comandos_minijuego):
                    if hasattr(state, "gestor_juegos") and state.gestor_juegos:
                        print(f"[mundo] iniciar minijuego solicitado: '{palabra}'")
                        state.gestor_juegos.procesar_comando_voz(palabra)
                        state.esperando_voz = True    # 🟢 micrófono listo tras cargar minijuego
                        state.microfono_listo = True
                    else:
                        state.error_mensaje = "Gestor no inicializado."
                        state.esperando_voz = True
                        state.microfono_listo = True
                elif any(x in palabra for x in ["salir", "volver", "atrás", "atras"]):
                    if hasattr(state, "gestor_juegos") and state.gestor_juegos:
                        if hasattr(state.gestor_juegos, "_salir_mundo"):
                            state.gestor_juegos._salir_mundo()
                    state.fase = "menu_principal"
                    state.esperando_voz = True
                    state.microfono_listo = True
                    print("[mundo] salir -> menu_principal")
                else:
                    state.error_mensaje = "Di el minijuego que quieres jugar o 'salir' para volver."
                    state.esperando_voz = True
                    state.microfono_listo = True

            # ---------- Fase: jugando ----------
            elif fase == "jugando":
                palabra = texto.strip().lower()
                if any(x in palabra for x in ["salir", "volver", "atrás", "atras"]):
                    if hasattr(state, "gestor_juegos") and state.gestor_juegos:
                        try:
                            if hasattr(state.gestor_juegos, "_salir_mundo"):
                                state.gestor_juegos._salir_mundo()
                        except Exception:
                            print("Warning: error al llamar _salir_mundo()")
                    state.fase = "menu_principal"
                    state.esperando_voz = True
                    state.microfono_listo = True
                    print("[jugando] salir -> menu_principal")
                else:
                    if hasattr(state, "gestor_juegos") and state.gestor_juegos and getattr(state.gestor_juegos, "mundo_actual", None):
                        try:
                            mundo_actual = state.gestor_juegos.mundo_actual
                            if hasattr(mundo_actual, "procesar_comando"):
                                resultado = mundo_actual.procesar_comando(palabra)
                                if resultado:
                                    print("[jugando] comando enviado al mundo/juego y procesado")
                                    state.esperando_voz = True
                                    state.microfono_listo = True
                                else:
                                    state.error_mensaje = "Comando no reconocido por el juego."
                                    state.esperando_voz = True
                                    state.microfono_listo = True
                            else:
                                state.error_mensaje = "El mundo no soporta comandos por voz."
                                state.esperando_voz = True
                                state.microfono_listo = True
                        except Exception as e:
                            print(f"[jugando] error al procesar comando en mundo: {e}")
                            traceback.print_exc()
                            state.error_mensaje = "Error interno del juego."
                            state.esperando_voz = True
                            state.microfono_listo = True
                    else:
                        state.error_mensaje = "No hay juego activo."
                        state.esperando_voz = True
                        state.microfono_listo = True

            # ---------- Otras fases ----------
            else:
                state.error_mensaje = "Comando no reconocido en esta fase."
                state.esperando_voz = True
                state.microfono_listo = True

        except sr.WaitTimeoutError:
            print("[voz] WaitTimeoutError (no se detectó audio)")
            state.esperando_voz = True
            state.microfono_listo = True
            continue

        except sr.UnknownValueError:
            print("[voz] UnknownValueError (no se entendió audio)")
            state.error_mensaje = "No se entendió, habla más claro."
            state.esperando_voz = True
            state.microfono_listo = True
            continue

        except sr.RequestError as e:
            print(f"[voz] RequestError servicio reconocimiento: {e}")
            state.error_mensaje = "Error con el servicio de reconocimiento. Reintentando..."
            state.esperando_voz = True
            state.microfono_listo = True
            time.sleep(1)
            continue

        except Exception as e:
            print(f"[voz] Error inesperado: {e}")
            traceback.print_exc()
            state.error_mensaje = "Error inesperado en reconocimiento de voz."
            state.esperando_voz = True
            state.microfono_listo = True
            time.sleep(0.5)
            continue

    print("[voz] hilo de reconocimiento terminado")

# -------------------------
# Utiles internos
# -------------------------
def verificar_usuario_por_nombre_existente(nombre: str) -> bool:
    """
    Usa la función del módulo usuarios para comprobar si existe un nombre.
    Si tu módulo tiene otra firma puedes adaptarla.
    """
    try:
        return verificar_usuario_existe(nombre)
    except Exception:
        # por seguridad, asumimos que no existe si hay error en llamada
        return False
