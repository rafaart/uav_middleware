"""Ponto único de entrada do núcleo. A camada de integração ROS2 não deve
chamar geometry/controller/state_machine diretamente — ela monta um
FrameContext e chama `TrackingPipeline.process(frame)`, recebendo de volta
um NavigationCommand pronto para ser traduzido em setpoint real.

Manter um único ponto de entrada facilita testar o núcleo por completo
(teste de integração dentro do próprio pacote, sem nenhum nó ROS) e reduz
a superfície que a camada de integração precisa conhecer.
"""

from __future__ import annotations

from middleware_core.contracts import FrameContext, NavigationCommand, TrackerState
from middleware_core.controller import ControllerParams, track_to_command
from middleware_core.geometry import compute_error
from middleware_core.state_machine import TargetSelector, TrackingFSM


class TrackingPipeline:
    def __init__(
        self,
        controller_params: ControllerParams | None = None,
        lost_timeout_frames: int = 15,
    ) -> None:
        self.params = controller_params or ControllerParams()
        self.fsm = TrackingFSM(lost_timeout_frames=lost_timeout_frames)

    def process(self, frame: FrameContext) -> NavigationCommand:
        target = TargetSelector.select(frame.detections)
        state = self.fsm.update(has_detection=target is not None)

        if target is not None and state == TrackerState.TRACKING:
            err_x, err_y = compute_error(target.bbox, frame.image_width, frame.image_height)
            vx, vy = track_to_command(err_x, err_y, self.params)
        else:
            # SEARCHING ou LOST: nenhum comando de correção é gerado aqui.
            # Uma política de "busca" (ex.: manobra de varredura) ou de
            # failsafe (ex.: RTL) fica a cargo da camada de integração,
            # que tem acesso ao AutopilotStatus e pode decidir com mais
            # contexto do que o núcleo isoladamente.
            vx, vy = 0.0, 0.0

        return NavigationCommand(vx=vx, vy=vy, vz=0.0, yaw_rate=0.0, state=state)
