import speech_recognition as sr
import time
import traceback
import unicodedata

from modules.usuarios import (
    buscar_usuario_por_cara,
    verificar_usuario_existe,
    registrar_usuario,
    actualizar_nombre_usuario,
    actualizar_idioma_usuario,
    Usuario
)
from modules.data_manager import MongoDBManager

mongo = MongoDBManager()

def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto

def inicializar_microfono(state, recognizer, microphone):
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
    print("[voz] hilo de reconocimiento iniciado")
    
    # Asegurar conexión a MongoDB al inicio del hilo
    try:
        mongo.asegurar_conexion()
        print("[voz] Conexión a MongoDB verificada")
    except Exception as e:
        print(f"[voz] Error al conectar con MongoDB: {e}")
        state.error_mensaje = "Error de conexion con la base de datos. Intenta de nuevo."
        state.esperando_voz = True
        state.microfono_listo = True
        return

    if not hasattr(state, "microfono_listo"):
        state.microfono_listo = True
    if not hasattr(state, "esperando_voz"):
        state.esperando_voz = True

    while voice_thread_active[0]:
        if not (getattr(state, "esperando_voz", False) and getattr(state, "microfono_listo", False)):
            time.sleep(0.12)
            continue

        try:
            fase = getattr(state, "fase", "inicio")
            print(f"[voz] escuchando en fase: {fase}")

            timeout = 6 if "nombre" in fase else 4
            phrase_limit = 7 if "nombre" in fase else 5

            with microphone as source:
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)

            texto = recognizer.recognize_google(audio, language="es-ES").lower().strip()
            print(f"[voz] detectado: '{texto}'")

            if hasattr(state, "error_mensaje"):
                delattr(state, "error_mensaje")

            # ---------- Fase: reconocimiento_facial ----------
            if fase == "reconocimiento_facial":
                if "iniciar sesión" in texto or "iniciar sesion" in texto or ("iniciar" in texto and "sesión" in texto):
                    print("[voz] petición iniciar sesión por voz")
                    if hasattr(state, "vector_facial_actual"):
                        nombre_encontrado, datos_usuario = buscar_usuario_por_cara(state.vector_facial_actual)
                        if nombre_encontrado:
                            state.usuario_nombre = nombre_encontrado
                            state.usuario_data = datos_usuario
                            state.sesion_iniciada = True
                            state.fase = "menu_principal"
                            state.esperando_voz = True
                            state.microfono_listo = True
                            state.usuario_actual = Usuario.cargar_progreso(nombre_encontrado)
                            print(f"[auth] sesión iniciada: {nombre_encontrado} -> menu_principal")
                            
                            if state.usuario_actual:
                                state.sincronizar_con_usuario(nombre_encontrado)
                                print(f"[voz] usuario '{nombre_encontrado}' sincronizado con MongoDB")
                            else:
                                state.error_mensaje = "Error al cargar datos del usuario. Intenta de nuevo."
                                state.esperando_voz = True
                                state.microfono_listo = True
                        else:
                            state.error_mensaje = "Cara no registrada. Di 'registrarme' para crear cuenta."
                            state.esperando_voz = True
                            state.microfono_listo = True
                    else:
                        state.error_mensaje = "No se detecto la cara. Mira a la camara."
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
                    try:
                        if verificar_usuario_existe(nombre):
                            state.error_mensaje = f"El nombre '{nombre}' ya existe. Di otro nombre."
                            state.esperando_voz = True
                            state.microfono_listo = True
                        else:
                            state.usuario_nombre = nombre
                            state.fase = "esperando_idioma_registro"
                            state.esperando_voz = True
                            state.microfono_listo = True
                            print(f"[registro] nombre ok -> pedir idioma para {nombre}")
                    except Exception as e:
                        state.error_mensaje = f"Error verificando nombre: {e}. Intenta de nuevo."
                        state.esperando_voz = True
                        state.microfono_listo = True
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
                        try:
                            datos = registrar_usuario(state.usuario_nombre, idioma_codigo, state.vector_facial_actual)
                            if datos:
                                state.usuario_data = datos
                                state.sesion_iniciada = True
                                state.fase = "menu_principal"
                                state.esperando_voz = True
                                state.microfono_listo = True
                                state.usuario_actual = Usuario.cargar_progreso(state.usuario_nombre)
                                state.sincronizar_con_usuario(state.usuario_nombre)
                                print(f"[registro] usuario '{state.usuario_nombre}' registrado -> menu_principal")
                            else:
                                state.error_mensaje = "Error registrando usuario. Intenta de nuevo."
                                state.fase = "reconocimiento_facial"
                                state.esperando_voz = True
                                state.microfono_listo = True
                        except Exception as e:
                            state.error_mensaje = f"Error registrando usuario: {e}. Intenta de nuevo."
                            state.fase = "reconocimiento_facial"
                            state.esperando_voz = True
                            state.microfono_listo = True
                    else:
                        state.error_mensaje = "No se detecto la cara para registrar."
                        state.fase = "reconocimiento_facial"
                        state.esperando_voz = True
                        state.microfono_listo = True
                else:
                    state.error_mensaje = "Idioma no valido. Di 'español' o 'ingles'."
                    state.esperando_voz = True
                    state.microfono_listo = True

            # ---------- Fase: menu_principal ----------
            elif fase == "menu_principal":
                palabra = texto.strip().lower()
                # Comandos de menú normal
                if any(x in palabra for x in ["perfil", "progreso", "disfraz", "disfraces"]):
                    print(f"[menu] comando de menú detectado: {palabra}")
                    if hasattr(state, "gestor_juegos") and state.gestor_juegos:
                        state.gestor_juegos.procesar_comando_voz(palabra)
                    else:
                        state.error_mensaje = "Sistema no listo. Gestor no inicializado."
                    state.esperando_voz = True
                    state.microfono_listo = True
                    continue
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
                        state.esperando_voz = True
                        state.microfono_listo = True
                    else:
                        state.error_mensaje = "Sistema no listo. Gestor no inicializado."
                        state.esperando_voz = True
                        state.microfono_listo = True
                elif any(x in palabra for x in ["salir", "cerrar", "volver"]):
                    state.fase = "salir"
                    state.esperando_voz = True
                    state.microfono_listo = True
                    print("[menu] comando salir -> CERRANDO APLICACION")
                else:
                    state.error_mensaje = "Di lo que quieras hacer"
                    state.esperando_voz = True
                    state.microfono_listo = True

            # ---------- Fase: perfil ----------
            elif fase == "perfil":
                palabra = texto.strip().lower()

                # --- Comando para cambiar nombre ---
                if palabra.startswith("nombre "):
                    nombre_nuevo = palabra.replace("nombre ", "").strip()
                    nombre_normalizado = normalizar(nombre_nuevo)  # minusculas, sin tildes, sin ñ

                    if len(nombre_normalizado) < 2:
                        state.error_mensaje = "Nombre demasiado corto. Intenta de nuevo."
                    elif verificar_usuario_existe(nombre_normalizado):
                        state.error_mensaje = f"El nombre '{nombre_normalizado}' ya existe. Di otro nombre."
                    else:
                        try:
                            datos_actualizados = actualizar_nombre_usuario(state.usuario_actual, nombre_normalizado)
                            if datos_actualizados:
                                state.usuario_actual = nombre_normalizado
                                state.usuario_data = Usuario.cargar_progreso(nombre_normalizado)
                                state.error_mensaje = f"Nombre actualizado a '{nombre_normalizado}'"
                                state.fase = "menu_principal"
                                state.esperando_voz = True
                                state.microfono_listo = True
                                print(f"[perfil] nombre actualizado -> menu_principal")
                            else:
                                state.error_mensaje = "Error al actualizar nombre. Intenta de nuevo."
                                state.esperando_voz = True
                                state.microfono_listo = True
                        except Exception as e:
                            state.error_mensaje = f"Excepción al actualizar nombre: {e}"
                            state.esperando_voz = True
                            state.microfono_listo = True

                # --- Comando para cambiar idioma ---
                elif palabra.startswith("idioma "):
                    idioma_nuevo = palabra.replace("idioma ", "").strip()
                    idioma_normalizado = normalizar(idioma_nuevo)
                    idiomas_disponibles = {"espanol": "es", "castellano": "es", "ingles": "en", "english": "en"}
                    codigo = idiomas_disponibles.get(idioma_normalizado)

                    if not codigo:
                        state.error_mensaje = "Idioma no válido. Di 'español' o 'ingles'."
                        state.esperando_voz = True
                        state.microfono_listo = True
                    else:
                        try:
                            exito = actualizar_idioma_usuario(state.usuario_actual, codigo)
                            if exito:
                                state.usuario_data["idioma"] = codigo
                                state.error_mensaje = f"Idioma actualizado a '{idioma_normalizado}'"
                                state.fase = "menu_principal"
                                state.esperando_voz = True
                                state.microfono_listo = True
                                print(f"[perfil] idioma actualizado -> menu_principal")
                            else:
                                state.error_mensaje = "Error al actualizar idioma."
                                state.esperando_voz = True
                                state.microfono_listo = True
                        except Exception as e:
                            state.error_mensaje = f"Excepción al actualizar idioma: {e}"
                            state.esperando_voz = True
                            state.microfono_listo = True

                # --- Comando para volver al menú principal ---
                elif any(x in palabra for x in ["salir", "atrás", "volver", "atras"]):
                    state.fase = "menu_principal"
                    state.esperando_voz = True
                    state.microfono_listo = True
                    print("[perfil] comando salir -> menu principal")

                else:
                    state.error_mensaje = "Di 'nombre <nuevo nombre>' o 'idioma <nuevo idioma>', o 'atras' para volver."
                    state.esperando_voz = True
                    state.microfono_listo = True



            # ---------- Fase: progreso ----------
            elif fase == "progreso":
                palabra = texto.strip().lower()
                if any(x in palabra for x in ["salir", "atrás", "volver", "atras"]):
                    state.fase = "menu_principal"
                    state.esperando_voz = True
                    state.microfono_listo = True
                    print("[progreso] comando salir -> menu principal")
                else:
                    state.esperando_voz = True
                    state.microfono_listo = True
                    
            # ---------- Fase: disfraces ----------
            elif fase == "disfraces":
                palabra = texto.strip().lower()

                # Comprar o equipar
                if palabra.startswith("comprar ") or palabra.startswith("equipar "):
                    if hasattr(state, "gestor_juegos") and state.gestor_juegos:
                        state.gestor_juegos.procesar_comando_disfraces(palabra)
                    else:
                        state.error_mensaje = "Sistema no listo. Gestor no inicializado."
                    state.esperando_voz = True
                    state.microfono_listo = True

                # Salir al menú principal
                elif any(x in palabra for x in ["salir", "atrás", "volver", "atras"]):
                    state.fase = "menu_principal"
                    state.esperando_voz = True
                    state.microfono_listo = True
                    print("[disfraces] comando salir -> menu principal")


            # ---------- Fase: mundo_<nombre> ----------
            elif fase.startswith("mundo_"):
                palabra = texto.strip().lower()
                comandos_minijuego = [
                    "adivina", "memoria", "secuencia", "contar", "deletreo",
                    "sonido", "clasificar", "adivina", "suma", "mayor", "descubre", "encuentra", "color", "clasifica"
                ]
                if any(cmd in palabra for cmd in comandos_minijuego):
                    if hasattr(state, "gestor_juegos") and state.gestor_juegos:
                        print(f"[mundo] iniciar minijuego solicitado: '{palabra}'")
                        state.gestor_juegos.procesar_comando_voz(palabra)
                        state.esperando_voz = True    # micrófono listo tras cargar minijuego
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
                    state.error_mensaje = "Di el minijuego que quieres jugar o 'atras' para volver."
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
            state.error_mensaje = "No se entendio, habla mas claro."
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
# # Utiles internos
# # -------------------------
def verificar_usuario_por_nombre_existente(nombre: str) -> bool:
    """
    Usa la función del módulo usuarios para comprobar si existe un nombre.
    """
    try:
        return verificar_usuario_existe(nombre)
    except Exception:
        return False
    
