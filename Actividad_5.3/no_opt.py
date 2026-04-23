from api import get_iss_position

def obtener_datos_no_opt():
    """
    Versión NO optimizada:
    - Repite cálculos
    - Usa listas innecesarias
    - Múltiples bucles
    """
    data = []

    for _ in range(5):
        pos = get_iss_position()
        data.append(pos)

    latitudes = []
    for d in data:
        latitudes.append(float(d["lat"]))

    suma = 0
    for lat in latitudes:
        suma += lat

    promedio = suma / len(latitudes)

    return {
        "promedio_lat": promedio,
        "datos": data
    }