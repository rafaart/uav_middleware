import pytest

from middleware_core.contracts import BoundingBox, Detection, TrackerState
from middleware_core.state_machine import TargetSelector, TrackingFSM


def _det(confidence: float, class_id: int = 0) -> Detection:
    return Detection(
        bbox=BoundingBox(x_center=100, y_center=100, width=20, height=20),
        class_id=class_id,
        class_name="person",
        confidence=confidence,
    )


class TestTargetSelector:
    def test_lista_vazia_retorna_none(self):
        assert TargetSelector.select([]) is None

    def test_seleciona_maior_confianca(self):
        low = _det(0.3)
        high = _det(0.9)
        mid = _det(0.6)
        assert TargetSelector.select([low, high, mid]) is high


class TestTrackingFSM:
    def test_estado_inicial_e_idle(self):
        fsm = TrackingFSM()
        assert fsm.state == TrackerState.IDLE

    def test_deteccao_leva_a_tracking(self):
        fsm = TrackingFSM(lost_timeout_frames=3)
        state = fsm.update(has_detection=True)
        assert state == TrackerState.TRACKING
        assert fsm.frames_without_detection == 0

    def test_perda_temporaria_leva_a_searching(self):
        fsm = TrackingFSM(lost_timeout_frames=3)
        fsm.update(has_detection=True)
        state = fsm.update(has_detection=False)
        assert state == TrackerState.SEARCHING

    def test_perda_prolongada_leva_a_lost(self):
        fsm = TrackingFSM(lost_timeout_frames=3)
        fsm.update(has_detection=True)
        fsm.update(has_detection=False)  # 1
        fsm.update(has_detection=False)  # 2
        state = fsm.update(has_detection=False)  # 3 -> timeout atingido
        assert state == TrackerState.LOST

    def test_deteccao_apos_lost_volta_a_tracking(self):
        fsm = TrackingFSM(lost_timeout_frames=2)
        fsm.update(has_detection=True)
        fsm.update(has_detection=False)
        fsm.update(has_detection=False)  # LOST
        state = fsm.update(has_detection=True)
        assert state == TrackerState.TRACKING
        assert fsm.frames_without_detection == 0

    def test_timeout_invalido_levanta_erro(self):
        with pytest.raises(ValueError):
            TrackingFSM(lost_timeout_frames=0)

    def test_reset_volta_para_idle(self):
        fsm = TrackingFSM(lost_timeout_frames=2)
        fsm.update(has_detection=True)
        fsm.reset()
        assert fsm.state == TrackerState.IDLE
        assert fsm.frames_without_detection == 0
