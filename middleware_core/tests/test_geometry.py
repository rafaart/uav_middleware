import pytest

from middleware_core.contracts import BoundingBox
from middleware_core.geometry import compute_error


def test_bbox_centralizado_gera_erro_zero():
    bbox = BoundingBox(x_center=320, y_center=240, width=50, height=50)
    err_x, err_y = compute_error(bbox, image_width=640, image_height=480)
    assert err_x == pytest.approx(0.0)
    assert err_y == pytest.approx(0.0)


def test_bbox_deslocado_a_direita_gera_erro_positivo():
    bbox = BoundingBox(x_center=640, y_center=240, width=50, height=50)  # borda direita
    err_x, _ = compute_error(bbox, image_width=640, image_height=480)
    assert err_x == pytest.approx(1.0)


def test_bbox_deslocado_a_esquerda_gera_erro_negativo():
    bbox = BoundingBox(x_center=0, y_center=240, width=50, height=50)  # borda esquerda
    err_x, _ = compute_error(bbox, image_width=640, image_height=480)
    assert err_x == pytest.approx(-1.0)


def test_bbox_deslocado_abaixo_gera_erro_y_positivo():
    bbox = BoundingBox(x_center=320, y_center=480, width=50, height=50)  # borda inferior
    _, err_y = compute_error(bbox, image_width=640, image_height=480)
    assert err_y == pytest.approx(1.0)


def test_dimensoes_invalidas_geram_erro():
    bbox = BoundingBox(x_center=1, y_center=1, width=1, height=1)
    with pytest.raises(ValueError):
        compute_error(bbox, image_width=0, image_height=480)
