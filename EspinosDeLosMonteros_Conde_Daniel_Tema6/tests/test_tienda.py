from unittest.mock import MagicMock, mock_open, patch

import pytest

import tienda


@pytest.fixture
def lineas_validas():
    return [
        {"producto": "teclado", "cantidad": 2},
        {"producto": "raton", "cantidad": 1},
    ]


def test_obtener_producto_devuelve_producto_existente():
    producto = tienda.obtener_producto("teclado")
    assert producto["precio"] == 25.0
    assert producto["stock"] == 10


def test_obtener_producto_inexistente_lanza_keyerror():
    with pytest.raises(KeyError):
        tienda.obtener_producto("altavoz")


def test_calcular_subtotal_pedido_valido(lineas_validas):
    assert tienda.calcular_subtotal(lineas_validas) == 65.0


def test_calcular_subtotal_pedido_vacio_lanza_excepcion():
    with pytest.raises(tienda.PedidoInvalidoError, match="vacío"):
        tienda.calcular_subtotal([])


@pytest.mark.parametrize("cantidad", [0, -1, -10])
def test_calcular_subtotal_cantidad_no_valida_lanza_excepcion(cantidad):
    lineas = [{"producto": "usb", "cantidad": cantidad}]
    with pytest.raises(tienda.PedidoInvalidoError, match="mayor que cero"):
        tienda.calcular_subtotal(lineas)


def test_calcular_subtotal_stock_insuficiente_lanza_excepcion():
    lineas = [{"producto": "monitor", "cantidad": 6}]
    with pytest.raises(tienda.ProductoNoDisponibleError, match="Stock insuficiente"):
        tienda.calcular_subtotal(lineas)


def test_calcular_subtotal_producto_inexistente_lanza_keyerror():
    lineas = [{"producto": "webcam", "cantidad": 1}]
    with pytest.raises(KeyError):
        tienda.calcular_subtotal(lineas)


@pytest.mark.parametrize(
    "subtotal, es_vip, cupon, esperado",
    [
        (100.0, False, None, 100.0),
        (100.0, True, None, 90.0),
        (100.0, False, "PROMO5", 95.0),
        (100.0, False, "PROMO10", 90.0),
        (100.0, True, "PROMO10", 80.0),
        (100.0, True, "PROMO5", 85.0),
        (100.0, False, "CUPON_INVALIDO", 100.0),
    ],
)
def test_aplicar_descuento_parametrizado(subtotal, es_vip, cupon, esperado):
    assert tienda.aplicar_descuento(subtotal, es_vip=es_vip, cupon=cupon) == esperado


def test_aplicar_descuento_limite_maximo_20_por_ciento():
    assert tienda.aplicar_descuento(250.0, es_vip=True, cupon="PROMO10") == 200.0


@pytest.mark.parametrize(
    "subtotal, provincia, urgente, esperado",
    [
        (100.0, "Madrid", False, 0.0),
        (99.99, "Madrid", False, 6.5),
        (80.0, "Canarias", False, 14.5),
        (80.0, "Baleares", True, 19.5),
        (120.0, "canarias", True, 13.0),
        (120.0, "Barcelona", True, 5.0),
    ],
)
def test_calcular_envio_parametrizado(subtotal, provincia, urgente, esperado):
    assert tienda.calcular_envio(subtotal, provincia, urgente=urgente) == esperado


def test_calcular_total_integracion_basica(lineas_validas):
    # Subtotal: 65.0, descuento VIP: 58.5, envio: 6.5 -> total 65.0
    total = tienda.calcular_total(lineas_validas, "Madrid", es_vip=True)
    assert total == 65.0


@pytest.mark.parametrize(
    "lineas, provincia, es_vip, cupon, urgente, esperado",
    [
        ([{"producto": "monitor", "cantidad": 1}], "Madrid", False, None, False, 120.0),
        ([{"producto": "monitor", "cantidad": 1}], "Madrid", True, None, False, 108.0),
        ([{"producto": "teclado", "cantidad": 1}], "Canarias", False, None, True, 44.5),
    ],
)
def test_calcular_total_parametrizado(lineas, provincia, es_vip, cupon, urgente, esperado):
    assert tienda.calcular_total(lineas, provincia, es_vip=es_vip, cupon=cupon, urgente=urgente) == esperado


@pytest.mark.parametrize(
    "codigo, esperado",
    [
        ("OK123", {"estado": "en reparto", "incidencia": False}),
        ("ERR404", {"estado": "desconocido", "incidencia": True}),
    ],
)
def test_consultar_estado_envio_respuestas_esperadas(codigo, esperado):
    assert tienda.consultar_estado_envio(codigo) == esperado


def test_consultar_estado_envio_fallo_conexion():
    with pytest.raises(ConnectionError):
        tienda.consultar_estado_envio("XYZ")


def test_guardar_pedido_mockeando_open_y_json_dump():
    pedido = {"cliente": "Ana", "lineas": [{"producto": "usb", "cantidad": 2}]}
    m_open = mock_open()

    with patch("builtins.open", m_open), patch("tienda.json.dump") as mock_dump:
        resultado = tienda.guardar_pedido("pedido.json", pedido)

    assert resultado is True
    m_open.assert_called_once()
    mock_dump.assert_called_once()


def test_cargar_pedido_mockeando_open_y_json_load():
    pedido_esperado = {"cliente": "Luis", "lineas": [{"producto": "raton", "cantidad": 3}]}
    m_open = mock_open(read_data='{"cliente": "Luis"}')

    with patch("builtins.open", m_open), patch("tienda.json.load", return_value=pedido_esperado) as mock_load:
        pedido = tienda.cargar_pedido("pedido.json")

    assert pedido == pedido_esperado
    m_open.assert_called_once()
    mock_load.assert_called_once()


def test_mocking_consultar_estado_envio_con_patch_object():
    fake = MagicMock(return_value={"estado": "entregado", "incidencia": False})

    with patch.object(tienda, "consultar_estado_envio", fake):
        respuesta = tienda.consultar_estado_envio("CUALQUIERA")

    assert respuesta == {"estado": "entregado", "incidencia": False}
    fake.assert_called_once_with("CUALQUIERA")