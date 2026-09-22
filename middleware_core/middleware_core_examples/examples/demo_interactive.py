"""Demonstração INTERATIVA do núcleo do middleware (middleware_core), sem
ROS2/MAVROS/YOLO/simulador. Você digita a posição do "alvo detectado" a
cada rodada e vê, em tempo real, o comando de navegação que o núcleo
geraria a partir disso — o mesmo tipo de objeto NavigationCommand que a
camada de integração ROS2 receberia em produção.

Uso:
    python examples/demo_interactive.py
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


def parse_input(raw: str):
    """Retorna None (sem detecção) ou (x, y) a partir do texto digitado."""
    raw = raw.strip().lower()
    if raw in ("", "vazio", "nenhum", "none"):
        return None
    parts = raw.replace(",", " ").split()
    if len(parts) != 2:
        raise ValueError("digite duas coordenadas: 'x y' (ex.: 450 200)")
    return float(parts[0]), float(parts[1])


def main() -> None:
    pipeline = TrackingPipeline(lost_timeout_frames=5)
    frame_counter = 0

    print("=" * 72)
    print("DEMONSTRAÇÃO INTERATIVA — middleware_core (sem ROS2/YOLO/simulador)")
    print(f"Resolução simulada da imagem: {IMAGE_WIDTH}x{IMAGE_HEIGHT}")
    print("Digite as coordenadas do alvo detectado, ex.: 450 200")
    print("Digite 'vazio' para simular um frame sem detecção.")
    print("Digite 'sair' para encerrar.")
    print("=" * 72)

    while True:
        try:
            raw = input("\n> ")
        except (EOFError, KeyboardInterrupt):
            break

        if raw.strip().lower() in ("sair", "quit", "exit"):
            break

        try:
            parsed = parse_input(raw)
        except ValueError as exc:
            print(f"entrada inválida: {exc}")
            continue

        frame_counter += 1
        detections = []
        bbox = None
        if parsed is not None:
            x, y = parsed
            bbox = BoundingBox(x_center=x, y_center=y, width=40, height=40)
            detections = [
                Detection(bbox=bbox, class_id=0, class_name="person", confidence=0.9)
            ]

        frame = FrameContext(
            image_width=IMAGE_WIDTH,
            image_height=IMAGE_HEIGHT,
            timestamp_ns=frame_counter,
            detections=detections,
        )
        command = pipeline.process(frame)

        print(render_frame(IMAGE_WIDTH, IMAGE_HEIGHT, bbox, command))

    print("\nEncerrado.")


if __name__ == "__main__":
    main()
