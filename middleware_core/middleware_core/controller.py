"""Tradução do erro normalizado (geometry.py) em comando de navegação
normalizado. Implementação atual: proporcional puro + zona morta +
saturação — deliberadamente simples, pois os ganhos "foram definidos de
forma exploratória" (cf. dissertação, seção 5.4) e ainda precisam passar
por um processo formal de sintonia (etapa futura do cronograma).

A estrutura já está pronta para evoluir para PID: basta adicionar os
termos integral/derivativo em ControllerParams e no cálculo de
`_apply_axis` sem alterar a assinatura pública de `track_to_command`.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ControllerParams:
    kp_x: float = 0.5
    kp_y: float = 0.5
    deadzone: float = 0.05  # erro abaixo disso é tratado como zero
    max_output: float = 1.0  # saturação de saída, deve respeitar [-1, 1]

    def __post_init__(self) -> None:
        if not 0.0 <= self.deadzone < 1.0:
            raise ValueError("deadzone deve estar em [0.0, 1.0)")
        if not 0.0 < self.max_output <= 1.0:
            raise ValueError("max_output deve estar em (0.0, 1.0]")


def _apply_axis(error: float, kp: float, params: ControllerParams) -> float:
    if abs(error) < params.deadzone:
        return 0.0
    command = kp * error
    return max(-params.max_output, min(params.max_output, command))


def track_to_command(err_x: float, err_y: float, params: ControllerParams) -> tuple[float, float]:
    """Retorna (vx, vy) normalizados em [-max_output, max_output]."""
    vx = _apply_axis(err_x, params.kp_x, params)
    vy = _apply_axis(err_y, params.kp_y, params)
    return vx, vy
