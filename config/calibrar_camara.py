"""
Script de calibración de cámara para el proyecto.
Al ejecutarlo, captura automáticamente imágenes del tablero ChArUco,
calcula la matriz intrínseca y los coeficientes de distorsión, y
guarda los resultados en 'camara.py'.
"""

import cv2
import numpy as np
import time
import os

def calibrar_camara(n_fotos=20, salida='camara.py'):
    # Configuración del tablero ChArUco
    FILAS = 7
    COLUMNAS = 11
    TAMCASILLA = 0.025  # metros
    TAMMARCADOR = 0.018 # metros
    DICARUCO = cv2.aruco.DICT_5X5_50
    DICCIONARIO = cv2.aruco.getPredefinedDictionary(DICARUCO)
    tablero = cv2.aruco.CharucoBoard((FILAS, COLUMNAS), TAMCASILLA, TAMMARCADOR, DICCIONARIO)
    detector = cv2.aruco.CharucoDetector(tablero)

    # Captura de cámara
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        return

    wframe = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    hframe = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    esquinas = []
    marcadores = []
    fotos_capturadas = 0
    CPS = 1  # Capturas por segundo
    tiempo = 1.0 / CPS
    antes = time.time()

    print(f"Se van a capturar {n_fotos} imágenes del tablero ChArUco.")
    print("Mantén el tablero visible y plano frente a la cámara.")
    print("Pulsa ESC cuando quieras finalizar la captura anticipadamente.")

    while fotos_capturadas < n_fotos:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bboxs, ids, _, _ = detector.detectBoard(frame)

        if ids is not None and ids.size > 8 and (time.time() - antes > tiempo):
            antes = time.time()
            cv2.aruco.drawDetectedCornersCharuco(frame, bboxs, ids)
            esquinas.append(bboxs)
            marcadores.append(ids)
            fotos_capturadas += 1
            print(f"Imagen capturada: {fotos_capturadas}/{n_fotos}")

        cv2.putText(frame, f"{fotos_capturadas}/{n_fotos}", (50,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        cv2.imshow("Captura ChArUco", frame)

        if cv2.waitKey(20) == 27:  # ESC para salir
            break

    cap.release()
    cv2.destroyAllWindows()

    if fotos_capturadas == 0:
        print("No se capturaron imágenes suficientes para calibrar.")
        return

    print("Calculando parámetros de calibración...")
    cameraMatrixInt = np.array([[1000, 0, hframe/2],
                                [0, 1000, wframe/2],
                                [0, 0, 1]])
    distCoeffsInt = np.zeros((5,1))
    flags = (cv2.CALIB_USE_INTRINSIC_GUESS + cv2.CALIB_RATIONAL_MODEL + cv2.CALIB_FIX_ASPECT_RATIO)

    ret, cameraMatrix, distCoeffs, rvecs, tvecs, stdInt, stdExt, errores = cv2.aruco.calibrateCameraCharucoExtended(
        charucoCorners=esquinas,
        charucoIds=marcadores,
        board=tablero,
        imageSize=(hframe, wframe),
        cameraMatrix=cameraMatrixInt,
        distCoeffs=distCoeffsInt,
        flags=flags,
        criteria=(cv2.TERM_CRITERIA_EPS & cv2.TERM_CRITERIA_COUNT, 10000, 1e-9)
    )

    # Guardar parámetros en camara.py
    with open(salida, 'w') as f:
        f.write("import numpy as np\n\n")
        f.write(f"cameraMatrix = np.array({repr(cameraMatrix.tolist())})\n")
        f.write(f"distCoeffs = np.array({repr(distCoeffs.tolist())})\n")

    print(f"Calibración completada. Los parámetros se han guardado en '{salida}'.")

if __name__ == "__main__":
    calibrar_camara()
