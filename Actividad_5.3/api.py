import requests
from concurrent.futures import ThreadPoolExecutor

API_URL = "http://api.open-notify.org/iss-now.json"
REQUEST_TIMEOUT = (1.2, 2.8)
_SESSION = requests.Session()
_LAST_KNOWN = {"lat": "0.0", "lon": "0.0"}

def get_iss_position(retries=2):
    """
    Obtiene la posición actual de la ISS desde una API pública.

    Returns:
        dict: latitud y longitud
    """
    for _ in range(retries + 1):
        try:
            response = _SESSION.get(API_URL, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            position = {
                "lat": data["iss_position"]["latitude"],
                "lon": data["iss_position"]["longitude"]
            }
            _LAST_KNOWN.update(position)
            return position
        except requests.RequestException:
            continue

    return dict(_LAST_KNOWN)


def get_iss_positions_parallel(count=5):
    """
    Obtiene varias posiciones de la ISS en paralelo para reducir latencia total.

    Args:
        count (int): número de muestras.

    Returns:
        list[dict]: posiciones de la ISS
    """
    workers = max(1, min(count, 3))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(lambda _: get_iss_position(retries=1), range(count)))