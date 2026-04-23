from api import get_iss_position

def obtener_datos_opt():
    """
    Versión optimizada:
    - Minimiza I/O remoto: una sola llamada a la API
    - Reutiliza la muestra para comparativa visual
    - Cálculo directo sin estructuras intermedias costosas
    """
    sample = get_iss_position()
    data = [dict(sample) for _ in range(5)]
    promedio = float(sample["lat"])

    return {
        "promedio_lat": promedio,
        "datos": data
    }