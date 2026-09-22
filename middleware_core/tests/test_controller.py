import pytest

from middleware_core.controller import ControllerParams, track_to_command


def test_erro_dentro_da_zona_morta_gera_comando_zero():
    params = ControllerParams(kp_x=1.0, kp_y=1.0, deadzone=0.1)
    vx, vy = track_to_command(err_x=0.05, err_y=-0.05, params=params)
    assert vx == 0.0
    assert vy == 0.0


def test_erro_acima_da_zona_morta_gera_comando_proporcional():
    params = ControllerParams(kp_x=0.5, kp_y=0.5, deadzone=0.05)
    vx, vy = track_to_command(err_x=0.5, err_y=-0.5, params=params)
    assert vx == pytest.approx(0.25)
    assert vy == pytest.approx(-0.25)


def test_comando_satura_no_limite_maximo():
    params = ControllerParams(kp_x=2.0, kp_y=2.0, deadzone=0.0, max_output=1.0)
    vx, vy = track_to_command(err_x=1.0, err_y=-1.0, params=params)
    assert vx == 1.0
    assert vy == -1.0


def test_deadzone_invalida_levanta_erro():
    with pytest.raises(ValueError):
        ControllerParams(deadzone=1.5)


def test_max_output_invalido_levanta_erro():
    with pytest.raises(ValueError):
        ControllerParams(max_output=0.0)
