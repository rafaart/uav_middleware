"""Máquina de estados de rastreamento e critério de seleção de alvo entre
múltiplas detecções da mesma classe.

O critério de seleção (`TargetSelector`) é isolado em sua própria classe
propositalmente: hoje é "maior confiança" (igual ao protótipo descrito na
dissertação), mas pode ser trocado por outro critério (ex.: alvo mais
próximo do centro, ou o alvo já sendo rastreado no frame anterior) sem
tocar na FSM."""

from __future__ import annotations

from middleware_core.contracts import Detection, TrackerState


class TargetSelector:
    """Estratégia de seleção de alvo entre múltiplas detecções."""

    @staticmethod
    def select(detections: list[Detection]) -> Detection | None:
        if not detections:
            return None
        return max(detections, key=lambda d: d.confidence)


class TrackingFSM:
    """Controla a transição TRACKING -> SEARCHING -> LOST conforme o
    número de frames consecutivos sem detecção."""

    def __init__(self, lost_timeout_frames: int = 15) -> None:
        if lost_timeout_frames <= 0:
            raise ValueError("lost_timeout_frames deve ser positivo")
        self.lost_timeout_frames = lost_timeout_frames
        self._frames_without_detection = 0
        self._state = TrackerState.IDLE

    @property
    def state(self) -> TrackerState:
        return self._state

    @property
    def frames_without_detection(self) -> int:
        return self._frames_without_detection

    def update(self, has_detection: bool) -> TrackerState:
        if has_detection:
            self._frames_without_detection = 0
            self._state = TrackerState.TRACKING
        else:
            self._frames_without_detection += 1
            if self._frames_without_detection >= self.lost_timeout_frames:
                self._state = TrackerState.LOST
            else:
                self._state = TrackerState.SEARCHING
        return self._state

    def reset(self) -> None:
        self._frames_without_detection = 0
        self._state = TrackerState.IDLE
