"""Contrato de dados que atravessa a fronteira entre o núcleo de decisão
(este pacote) e a camada de integração ROS2 (`middleware_bridge`).

Regras deste módulo (não relaxar sem atualizar a dissertação/documentação):

1. Nenhum tipo aqui pode depender de ROS2, MAVROS, OpenCV ou qualquer
   outro framework — só a stdlib do Python.
2. Todo tipo é imutável (`frozen=True`): a camada de integração recebe um
   valor e não pode alterá-lo "por baixo" do núcleo.
3. Unidades são sempre explícitas em comentário/docstring (pixels vs.
   comando normalizado vs. metros), porque é exatamente essa ambiguidade
   que costuma gerar bugs na transição sim-to-real.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


@dataclass(frozen=True)
class BoundingBox:
    """Coordenadas em pixels,  origem no canto superior-esquerdo da imagem."""

    x_center: float  # px
    y_center: float  # px
    width: float  # px
    height: float  # px


@dataclass(frozen=True)
class Detection:
    """Uma detecção individual, já traduzida do formato do detector de IA
    (ex.: vision_msgs/Detection2D) para o tipo do núcleo."""

    bbox: BoundingBox
    class_id: int
    class_name: str
    confidence: float  # [0.0, 1.0]

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"confidence deve estar em [0.0, 1.0], recebido: {self.confidence}"
            )


@dataclass(frozen=True)
class FrameContext:
    """Tudo que o núcleo precisa saber sobre um frame para decidir o que
    fazer. `detections` pode vir vazia (nenhum alvo detectado no frame)."""

    image_width: int  # px
    image_height: int  # px
    timestamp_ns: int
    detections: list[Detection] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.image_width <= 0 or self.image_height <= 0:
            raise ValueError("image_width e image_height devem ser positivos")


@dataclass(frozen=True)
class AutopilotStatus:
    """Status do autopiloto normalizado — nada de MAVLink/mavros_msgs aqui.
    A camada de integração é responsável por preencher isso a partir do
    tópico /mavros/state (ou equivalente de outro autopiloto)."""

    armed: bool
    mode: str
    connected: bool
    battery_pct: float | None = None  # None quando desconhecido


class TrackerState(Enum):
    IDLE = auto()
    TRACKING = auto()
    SEARCHING = auto()  # perdeu o alvo há N frames, ainda dentro do timeout
    LOST = auto()  # timeout de perda excedido


@dataclass(frozen=True)
class NavigationCommand:
    """Comando de navegação NORMALIZADO, sem unidade física. A conversão
    para m/s ou rad/s reais (um "setpoint" de verdade) é responsabilidade
    exclusiva da camada de integração — isso é o que garante que o núcleo
    não precisa saber qual autopiloto está do outro lado."""

    vx: float  # [-1.0, 1.0] — avanço/recuo
    vy: float  # [-1.0, 1.0] — lateral
    vz: float  # [-1.0, 1.0] — altitude
    yaw_rate: float  # [-1.0, 1.0]
    state: TrackerState

    def __post_init__(self) -> None:
        for name in ("vx", "vy", "vz", "yaw_rate"):
            value = getattr(self, name)
            if not -1.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} deve estar em [-1.0, 1.0], recebido: {value}")
