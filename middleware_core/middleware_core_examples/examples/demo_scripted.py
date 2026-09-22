"""Demonstra o núcleo do middleware (middleware_core) sem NENHUMA
dependência de ROS2, MAVROS, YOLO ou simulador. Roda em qualquer máquina
com Python 3.10+ — inclusive sem o pacote instalado via pip (o bloco
try/except abaixo resolve o import direto a partir da pasta do projeto).

Uso:
    python examples/demo_scripted.py

O script alimenta o TrackingPipeline com uma sequência fixa de "frames"
sintéticos (coordenadas de bounding box escritas em SCENARIO, abaixo) e
imprime, para cada um, o comando de navegação gerado — exatamente o tipo
de objeto que a camada de integração ROS2 (middleware_bridge) receberia
do núcleo em produção.
"""

import sys
from pathlib import Path

try:
    from middleware_core import BoundingBox, Detection, FrameContext, TrackingPipeline
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from middleware_core import BoundingBox, Detection, FrameContext, TrackingPipeline

from ascii_view import render_frame

IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

# Cada item: (rótulo do frame, lista de detecções como (x, y, confiança))
SCENARIO = [
    ("Alvo centralizado", [(320, 240, 0.95)]),
    ("Alvo se deslocando para a direita", [(450, 240, 0.93)]),
    ("Alvo na borda direita da imagem", [(620, 200, 0.90)]),
    ("Sem detecção (1/5 frames)", []),
    ("Sem detecção (2/5 frames)", []),
    ("Sem detecção (3/5 frames)", []),
    ("Sem detecção (4/5 frames)", []),
    ("Sem detecção (5/5 frames) -> timeout de perda", []),
    ("Alvo reaparece à esquerda", [(80, 300, 0.88)]),
    (
        "Duas detecções simultâneas: núcleo deve escolher a de maior confiança",
        [(600, 100, 0.40), (330, 245, 0.92)],
    ),
]


def build_frame(timestamp_ns: int, raw_detections):
    detections = [
        Detection(
            bbox=BoundingBox(x_center=x, y_center=y, width=40, height=40),
            class_id=0,
            class_name="person",
            confidence=conf,
        )
        for x, y, conf in raw_detections
    ]
    return FrameContext(
        image_width=IMAGE_WIDTH,
        image_height=IMAGE_HEIGHT,
        timestamp_ns=timestamp_ns,
        detections=detections,
    )


def main() -> None:
    pipeline = TrackingPipeline(lost_timeout_frames=5)

    print("=" * 72)
    print("DEMONSTRAÇÃO DO NÚCLEO DO MIDDLEWARE (middleware_core)")
    print("Sem ROS2, sem MAVROS, sem YOLO, sem simulador — só o pipeline puro.")
    print("=" * 72)

    for i, (label, raw_detections) in enumerate(SCENARIO, start=1):
        frame = build_frame(timestamp_ns=i, raw_detections=raw_detections)
        command = pipeline.process(frame)

        # bbox usada só para desenhar: o alvo que o núcleo efetivamente
        # escolheu (maior confiança), se houver mais de uma detecção.
        chosen_bbox = None
        if raw_detections:
            best = max(raw_detections, key=lambda d: d[2])
            chosen_bbox = BoundingBox(x_center=best[0], y_center=best[1], width=40, height=40)

        print(f"\n[frame {i}] {label}")
        print(render_frame(IMAGE_WIDTH, IMAGE_HEIGHT, chosen_bbox, command))

    print("\nFim da demonstração.")


if __name__ == "__main__":
    main()
