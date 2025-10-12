import speech_recognition as sr
import threading
import time
from modules.usuarios import buscar_usuario_por_cara, verificar_usuario_existe, registrar_usuario, actualizar_nombre_usuario, actualizar_idioma_usuario

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

def verificar_respuesta(texto, respuesta_correcta):
    texto = texto.lower().strip()
    respuesta_correcta = respuesta_correcta.lower().strip()
    print(f" Verificando: '{texto}' == '{respuesta_correcta}'")
    if respuesta_correcta in texto:
        print(" Coincidencia directa encontrada")
        return True
    if texto in respuesta_correcta:
        print(" Coincidencia inversa encontrada")
        return True
    variaciones = {
        'pera': ['pera', 'peras'],
        'cebolleta': ['cebolleta', 'cebolletas', 'cebollín', 'cebollino'],
        'cebolla': ['cebolla', 'cebollas'],
        'lechuga': ['lechuga', 'lechugas'],
        'limon': ['limón', 'limon', 'limones'],
        'limón': ['limón', 'limon', 'limones'],
        'pimiento rojo': ['pimiento rojo', 'pimiento', 'pimientos rojos', 'pimientos'],
        'pimiento verde': ['pimiento verde', 'pimiento', 'pimientos verdes', 'pimientos'],
        'pimiento': ['pimiento', 'pimientos', 'pimiento rojo', 'pimiento verde'],
        'uvas': ['uvas', 'uva', 'racimo', 'racimo de uvas'],
        'uva': ['uvas', 'uva', 'racimo', 'racimo de uvas'],
        'zanahoria': ['zanahoria', 'zanahorias'],
    }
    if respuesta_correcta in variaciones:
        for variacion in variaciones[respuesta_correcta]:
            if variacion in texto:
                print(f" Variación encontrada: '{variacion}' en '{texto}'")
                return True
    for clave, lista_variaciones in variaciones.items():
        if clave == respuesta_correcta:
            continue
        for variacion in lista_variaciones:
            if variacion in texto and clave == respuesta_correcta:
                print(f" Variación de clave encontrada: '{variacion}' -> '{clave}'")
                return True
    palabras_texto = texto.split()
    palabras_respuesta = respuesta_correcta.split()
    if len(palabras_respuesta) == 1:
        palabra_correcta = palabras_respuesta[0]
        for palabra in palabras_texto:
            if palabra == palabra_correcta:
                print(f" Palabra individual encontrada: '{palabra}'")
                return True
            if palabra_correcta in variaciones:
                if palabra in variaciones[palabra_correcta]:
                    print(f" Variación de palabra encontrada: '{palabra}' -> '{palabra_correcta}'")
                    return True
    print(f" No se encontró coincidencia para '{texto}' vs '{respuesta_correcta}'")
    return False

def reconocimiento_voz(state, recognizer, microphone, voice_thread_active):
    while voice_thread_active[0]:
        if state.esperando_voz and state.microfono_listo and recognizer and microphone:
            try:
                print(f" Escuchando en fase: {state.fase}")
                timeout = 5 if "nombre" in state.fase else 3
                phrase_limit = 6 if "nombre" in state.fase else 4
                with microphone as source:
                    audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
                texto = recognizer.recognize_google(audio, language="es-ES").lower().strip()
                print(f" Detectado: '{texto}'")
                if hasattr(state, 'error_mensaje'):
                    delattr(state, 'error_mensaje')
                if state.fase == "esperando_comando":
                    if "iniciar sesión" in texto:
                        print(" Comando: Iniciar sesión")
                        state.fase = "intentando_iniciar_sesion"
                    elif "registrar" in texto or "registrarme" in texto:
                        print(" Comando: Registro")
                        state.fase = "esperando_nombre_registro"
                    elif "iniciar" in texto:
                        print("❓ ¿Quieres iniciar sesión o registrarte?")
                        state.error_mensaje = "Di 'iniciar sesión' o 'registrarme' para continuar."
                    state.esperando_voz = False
                elif state.fase == "intentando_iniciar_sesion":
                    if hasattr(state, 'vector_facial_actual'):
                        nombre_encontrado, datos_usuario = buscar_usuario_por_cara(state.vector_facial_actual)
                        if nombre_encontrado:
                            state.usuario_nombre = nombre_encontrado
                            state.usuario_data = datos_usuario
                            state.sesion_iniciada = True
                            state.fase = "menu_principal"
                            print(f" Sesión iniciada para {nombre_encontrado}")
                        else:
                            print(" Cara no registrada.")
                            state.fase = "inicio_sesion_fallido"
                    else:
                        print(" No se ha detectado una cara para verificar.")
                        state.error_mensaje = "No se ha detectado una cara para iniciar sesion."
                    state.esperando_voz = False
                elif state.fase == "esperando_nombre_registro":
                    nombre = texto.strip().title()
                    print(f" Usuario dijo llamarse: {nombre}")
                    if len(nombre) >= 2:
                        if verificar_usuario_existe(nombre):
                            state.error_mensaje = f"Usuario {nombre} ya existe. Di otro nombre"
                            print(f" Usuario {nombre} ya existe")
                        else:
                            state.usuario_nombre = nombre
                            state.esperando_voz = False
                            state.fase = "esperando_idioma_registro"
                    else:
                        state.error_mensaje = "Nombre muy corto, intenta de nuevo"
                elif state.fase == "esperando_idioma_registro":
                    print(f" Usuario eligió idioma: {texto}")
                    idiomas_disponibles = {
                        "español": "es",
                        "castellano": "es",
                        "espanol": "es",
                        "inglés": "en",
                        "ingles": "en",
                        "english": "en"
                    }
                    idioma_codigo = idiomas_disponibles.get(texto.strip())
                    if idioma_codigo:
                        if hasattr(state, 'vector_facial_actual'):
                            datos = registrar_usuario(
                                state.usuario_nombre,
                                idioma_codigo,
                                state.vector_facial_actual
                            )
                            if datos:
                                print(f" Usuario {state.usuario_nombre} registrado correctamente")
                                state.usuario_data = datos
                                state.esperando_voz = False
                                state.fase = "menu_principal"
                                state.registro_exitoso = True
                                state.idioma_seleccionado = texto.strip()
                                state.esperando_voz = False
                            else:
                                state.error_mensaje = "Error registrando usuario"
                        else:
                            state.error_mensaje = "Error: no hay datos faciales"
                    else:
                        print(f" Idioma no reconocido: {texto}")
                        state.error_mensaje = "Idioma no válido (di: español o inglés)"
                elif state.fase == "menu_principal":
                    if "comenzar" in texto or "empezar" in texto or "jugar" in texto:
                        print("Iniciando selección de modo de juego")
                        state.esperando_voz = False
                        state.fase = "seleccion_modo"
                    elif "cuenta" in texto or "personal" in texto:
                        print("Entrando en la configuración de la cuenta...")
                        state.esperando_voz = False
                        state.fase = "configuracion_cuenta"
                    elif "progreso" in texto or "estadísticas" in texto:
                        print("Entrando al progreso...")
                        state.esperando_voz = False
                        state.fase = "ver_progreso"
                    elif "salir" in texto or "cerrar" in texto:
                        print(" Cerrando aplicación")
                        state.esperando_voz = False
                        state.fase = "salir"
                elif state.fase == "ver_progreso":
                    if "volver" in texto or "atrás" in texto or "salir" in texto:
                        print("Volviendo al menú principal")
                        state.esperando_voz = False
                        state.fase = "menu_principal"
                elif state.fase == "configuracion_cuenta":
                    if texto.strip().lower() == "cambiar nombre":
                        state.fase = "esperando_nuevo_nombre"
                        state.esperando_voz = True
                        state.mensaje_temporal = "Di tu nuevo nombre"
                    elif texto.strip().lower() == "cambiar idioma":
                        state.fase = "esperando_nuevo_idioma"
                        state.esperando_voz = True
                        state.mensaje_temporal = "Di el nuevo idioma (español o inglés)"
                    elif texto.strip().lower() == "volver":
                        state.fase = "menu_principal"
                        state.esperando_voz = True
                elif state.fase == "esperando_nuevo_nombre":
                    nuevo_nombre = texto.strip().title()
                    print(f" Usuario quiere cambiar su nombre a: {nuevo_nombre}")
                    if len(nuevo_nombre) >= 2:
                        comandos_reservados = ["salir", "cuenta", "comenzar", "cambiar nombre", "cambiar idioma", "volver"]
                        if verificar_usuario_existe(nuevo_nombre) and nuevo_nombre != state.usuario_nombre:
                            state.error_mensaje = f"El nombre {nuevo_nombre} ya está en uso"
                        elif nuevo_nombre.lower() in comandos_reservados:
                            state.error_mensaje = f"'{nuevo_nombre}' no es un nombre válido"
                        else:
                            nombre_anterior = state.usuario_nombre
                            state.usuario_nombre = nuevo_nombre
                            state.fase = "configuracion_cuenta"
                            state.nombre_cambiado = True
                            state.contador_nombre = 0
                            state.esperando_voz = False
                            actualizar_nombre_usuario(nombre_anterior, nuevo_nombre)
                            print(f" Nombre cambiado a {nuevo_nombre}")
                        state.nombre_cambiado = False
                    else:
                        state.error_mensaje = "Nombre muy corto, intenta de nuevo"
                elif state.fase == "esperando_nuevo_idioma":
                    idiomas_disponibles = {
                        "español": "es",
                        "castellano": "es",
                        "espanol": "es",
                        "inglés": "en",
                        "english": "en"
                    }
                    idioma_texto = texto.strip().lower()
                    idioma_codigo = idiomas_disponibles.get(idioma_texto)
                    if idioma_codigo:
                        state.usuario_data['idioma'] = idioma_codigo
                        state.idioma_seleccionado = idioma_texto
                        state.fase = "configuracion_cuenta"
                        state.idioma_cambiado = True
                        state.contador_idioma = 0
                        state.esperando_voz = False
                        if state.idioma_seleccionado in ["español", "castellano", "espanol"]:
                            state.idioma_seleccionado = "es"
                        else:
                            state.idioma_seleccionado = "en"
                        actualizar_idioma_usuario(state.usuario_nombre, state.idioma_seleccionado)
                        print(f" Idioma cambiado a {idioma_texto}")
                        state.idioma_cambiado = False
                    else:
                        state.error_mensaje = "Idioma no válido (di: español o inglés)"
                elif state.fase == "seleccion_modo":
                    if "entrenamiento" in texto or "entrenar" in texto or "practicar" in texto:
                        print(" Modo entrenamiento seleccionado")
                        state.esperando_voz = False
                        state.fase = "seleccion_juego"
                        state.modo_juego = "entrenamiento"
                    elif "evaluación" in texto or "evaluacion" in texto or "evaluar" in texto:
                        print(" Modo evaluación seleccionado")
                        state.esperando_voz = False
                        state.fase = "seleccion_juego"
                        state.modo_juego = "evaluacion"
                    elif "volver" in texto or "atrás" in texto or "salir" in texto:
                        print("Volviendo al menú principal")
                        state.esperando_voz = False
                        state.fase = "menu_principal"
                elif state.fase == "seleccion_juego":
                    juego_iniciado = False
                    if state.modo_juego == "entrenamiento":
                        if "descubre" in texto or "nombra" in texto or "nombres" in texto:
                            print(" Juego 'Descubre y Nombra' seleccionado")
                            try:
                                if not hasattr(state, 'gestor_juegos') or state.gestor_juegos is None:
                                    print(" Error: gestor_juegos no está inicializado")
                                elif "volver" in texto or "atrás" in texto or "salir" in texto:
                                    print("Volviendo al menú de juego")
                                    state.esperando_voz = False
                                    state.fase = "seleccion_juego"
                                else:
                                    state.gestor_juegos.establecer_modo(state.modo_juego)
                                    print(f" Modo establecido en gestor: {state.modo_juego}")
                                    state.gestor_juegos.iniciar_juego("descubre")
                                    if (state.gestor_juegos.juego_activo is not None and
                                        state.gestor_juegos.estado_juego == "en_juego"):
                                        juego_iniciado = True
                                        print(" Juego iniciado correctamente")
                                    else:
                                        print(" Error: juego no se inició correctamente")
                            except Exception as e:
                                print(f" Error detallado al iniciar juego: {e}")
                                import traceback
                                print(f"   - Traceback: {traceback.format_exc()}")
                        elif "frutas" in texto or "encuentra" in texto:
                            print("Juego 'Encuentra las Frutas' seleccionado")
                            try:
                                if not hasattr(state, 'gestor_juegos') or state.gestor_juegos is None:
                                    print("Error: gestor_juegos no está inicializado")
                                elif "volver" in texto or "atrás" in texto or "salir" in texto:
                                    print("Volviendo al menú de juego")
                                    state.esperando_voz = False
                                    state.fase = "seleccion_juego"
                                else:
                                    state.gestor_juegos.establecer_modo(state.modo_juego)
                                    state.gestor_juegos.iniciar_juego("frutas")
                                    if (state.gestor_juegos.juego_activo is not None and
                                        state.gestor_juegos.estado_juego == "en_juego"):
                                        juego_iniciado = True
                                        print(" Juego iniciado correctamente")
                                    else:
                                        print(" Error: juego no se inició correctamente")
                            except Exception as e:
                                print(f" Error detallado al iniciar juego: {e}")
                                import traceback
                                print(f"   - Traceback: {traceback.format_exc()}")
                        elif "volver" in texto or "atrás" in texto or "salir" in texto:
                            print("Volviendo a menú de modos de juegos")
                            state.esperando_voz = False
                            state.fase = "seleccion_modo"
                    elif state.modo_juego == "evaluacion":
                        if "categorías" in texto or "agrupa" in texto or "separa" in texto:
                            print(" Juego 'Agrupa por Categorías' seleccionado")
                            try:
                                if not hasattr(state, 'gestor_juegos') or state.gestor_juegos is None:
                                    print(" Error: gestor_juegos no está inicializado")
                                elif "volver" in texto or "atrás" in texto or "salir" in texto:
                                    print("Volviendo al menú de juego")
                                    state.esperando_voz = False
                                    state.fase = "seleccion_juego"
                                else:
                                    state.gestor_juegos.establecer_modo(state.modo_juego)
                                    state.gestor_juegos.iniciar_juego("categorias")
                                    if (state.gestor_juegos.juego_activo is not None and
                                        state.gestor_juegos.estado_juego == "en_juego"):
                                        juego_iniciado = True
                                        print(" Juego iniciado correctamente")
                                    else:
                                        print(" Error: juego no se inició correctamente")
                            except Exception as e:
                                print(f" Error detallado al iniciar juego: {e}")
                                import traceback
                                print(f"   - Traceback: {traceback.format_exc()}")
                        elif "memoria" in texto or "recuerda" in texto or "secuencia" in texto:
                            print(" Juego 'Juego de Memoria' seleccionado")
                            try:
                                if not hasattr(state, 'gestor_juegos') or state.gestor_juegos is None:
                                    print(" Error: gestor_juegos no está inicializado")
                                elif "volver" in texto or "atrás" in texto or "salir" in texto:
                                    print("Volviendo al menú de juego")
                                    state.esperando_voz = False
                                    state.fase = "seleccion_juego"
                                else:
                                    state.gestor_juegos.establecer_modo(state.modo_juego)
                                    state.gestor_juegos.iniciar_juego("memoria")
                                    if (state.gestor_juegos.juego_activo is not None and
                                        state.gestor_juegos.estado_juego == "en_juego"):
                                        juego_iniciado = True
                                        print(" Juego iniciado correctamente")
                                    else:
                                        print(" Error: juego no se inició correctamente")
                            except Exception as e:
                                print(f" Error detallado al iniciar juego: {e}")
                                import traceback
                                print(f"   - Traceback: {traceback.format_exc()}")
                        elif "volver" in texto or "atrás" in texto or "salir" in texto:
                            print("Volviendo a menú de modos de juegos")
                            state.esperando_voz = False
                            state.fase = "seleccion_modo"
                    if juego_iniciado:
                        state.esperando_voz = False
                        state.fase = "jugando"
                        print(f" Cambiando a fase 'jugando'")
                    else:
                        print(" No se pudo iniciar el juego. Permaneciendo en selección de juego.")
                        state.esperando_voz = True
                elif state.fase == "jugando":
                    if "salir" in texto or "volver" in texto or "atrás" in texto:
                        print(" Volviendo al menú")
                        state.esperando_voz = False
                        state.fase = "menu_principal"
                        if hasattr(state.gestor_juegos, 'resetear'):
                            state.gestor_juegos.resetear()
                    else:
                        if (hasattr(state.gestor_juegos, 'juego_activo') and
                            hasattr(state.gestor_juegos.juego_activo, 'procesar_comando')):
                            resultado = state.gestor_juegos.juego_activo.procesar_comando(texto)
                            if resultado:
                                print(" Comando de voz procesado por el juego")
                                state.gestor_juegos.procesar_resultado_juego(resultado)
                                state.esperando_voz = False
                            else:
                                print(" Comando no reconocido por el juego")
                elif state.fase == "esperando_respuesta" and hasattr(state, 'info_modelo_actual') and state.info_modelo_actual:
                    respuesta_correcta = state.info_modelo_actual['respuesta_correcta']
                    if verificar_respuesta(texto, respuesta_correcta):
                        state.respuesta_recibida = texto
                        state.respuesta_correcta = True
                        state.puntuacion += 1
                        if hasattr(state, 'marcadores_respondidos') and hasattr(state, 'marker_id_actual'):
                            state.marcadores_respondidos.add(state.marker_id_actual)
                        if hasattr(state, 'marcadores_pendientes') and hasattr(state, 'marker_id_actual'):
                            state.marcadores_pendientes.discard(state.marker_id_actual)
                        print(f" ¡Respuesta correcta! Puntuación: {state.puntuacion}")
                    else:
                        state.respuesta_recibida = texto
                        state.respuesta_correcta = False
                        print(f" Respuesta incorrecta. Esperaba: {respuesta_correcta}")
                    if hasattr(state, 'total_preguntas'):
                        state.total_preguntas += 1
                    if "volver" in texto or "atrás" in texto or "salir" in texto:
                        print("Volviendo al menú principal")
                        state.esperando_voz = False
                        state.fase = "menu_principal"
                    state.fase = "resultado"
                    state.esperando_voz = False
                    state.mostrar_resultado = True
                    state.tiempo_resultado = time.time()
                elif state.fase == "resultado":
                    if "continuar" in texto or "siguiente" in texto:
                        print("➡️ Continuando al siguiente...")
                        state.esperando_voz = False
                        state.fase = "jugando"
                        state.mostrar_resultado = False
                    if "volver" in texto or "atrás" in texto or "salir" in texto:
                        print("Volviendo al menú principal")
                        state.esperando_voz = False
                        state.fase = "menu_principal"
            except sr.WaitTimeoutError:
                print(" Timeout - reintentando...")
                if hasattr(state, 'fase') and state.fase in ["jugando", "esperando_respuesta"]:
                    state.error_mensaje = "No se escuchó respuesta, intenta de nuevo"
                continue
            except sr.UnknownValueError:
                print(" No se entendió el audio")
                state.error_mensaje = "No se entendió, habla más claro"
                continue
            except sr.RequestError as e:
                print(f" Error del servicio de reconocimiento: {e}")
                state.error_mensaje = "Error de conexión"
                time.sleep(1)
                continue
            except Exception as e:
                print(f" Error inesperado en reconocimiento: {e}")
                import traceback
                print(f"   - Traceback: {traceback.format_exc()}")
                state.error_mensaje = "Error inesperado"
                time.sleep(1)
                continue
        else:
            time.sleep(0.1)