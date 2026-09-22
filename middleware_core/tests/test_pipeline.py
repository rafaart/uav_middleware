from middleware_core.contracts import BoundingBox, Detection, FrameContext, TrackerState
from middleware_core.controller import ControllerParams
from middleware_core.pipeline import TrackingPipeline


def _frame(detections, width=640, height=480, ts=0):
    return FrameContext(image_width=width, image_height=height, timestamp_ns=ts, detections=detections)


def _det(x, y, confidence=0.9):
    return Detection(
        bbox=BoundingBox(x_center=x, y_center=y, width=30, height=30),
        class_id=0,
        class_name="person",
        confidence=confidence,
    )


def test_sem_deteccao_gera_comando_neutro_e_estado_searching():
    pipeline = TrackingPipeline(lost_timeout_frames=5)
    command = pipeline.process(_frame(detections=[]))
    assert command.vx == 0.0
    assert command.vy == 0.0
    assert command.state == TrackerState.SEARCHING


def test_deteccao_centralizada_gera_comando_neutro_em_estado_tracking():
    pipeline = TrackingPipeline()
    command = pipeline.process(_frame(detections=[_det(320, 240)]))
    assert command.vx == 0.0
    assert command.vy == 0.0
    assert command.state == TrackerState.TRACKING


def test_deteccao_deslocada_gera_comando_de_correcao():
    params = ControllerParams(kp_x=0.5, kp_y=0.5, deadzone=0.0)
    pipeline = TrackingPipeline(controller_params=params)
    command = pipeline.process(_frame(detections=[_det(640, 240)]))  # borda direita
    assert command.vx > 0.0
    assert command.state == TrackerState.TRACKING


def test_perda_prolongada_leva_a_lost_e_zera_comando():
    pipeline = TrackingPipeline(lost_timeout_frames=2)
    pipeline.process(_frame(detections=[_det(320, 240)]))  # TRACKING
    pipeline.process(_frame(detections=[]))  # SEARCHING (1)
    command = pipeline.process(_frame(detections=[]))  # LOST (2)
    assert command.state == TrackerState.LOST
    assert command.vx == 0.0
    assert command.vy == 0.0


def test_multiplas_deteccoes_seleciona_maior_confianca():
    params = ControllerParams(kp_x=0.5, kp_y=0.5, deadzone=0.0)
    pipeline = TrackingPipeline(controller_params=params)
    baixa_confianca_deslocada = _det(640, 240, confidence=0.2)
    alta_confianca_centralizada = _det(320, 240, confidence=0.95)
    command = pipeline.process(
        _frame(detections=[baixa_confianca_deslocada, alta_confianca_centralizada])
    )
    # o alvo de maior confiança está centralizado -> comando deve ser neutro
    assert command.vx == 0.0
    assert command.vy == 0.0
