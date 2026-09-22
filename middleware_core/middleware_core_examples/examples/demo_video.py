"""Gera um VÍDEO (mp4 e gif) demonstrando o rastreamento sintético do
núcleo do middleware — sem ROS2, MAVROS, YOLO ou simulador.

A ideia é a mesma dos outros demos (demo_scripted.py / demo_interactive.py):
alimentar o TrackingPipeline com uma trajetória sintética do "alvo" e
observar o comando de navegação gerado a cada frame. A diferença aqui é
que, em vez de imprimir texto, cada frame é desenhado como uma imagem e
todas as imagens são unidas em um arquivo de vídeo.

Dependências extras (só para este script — não fazem parte do núcleo):

    pip install matplotlib "imageio[ffmpeg]"

O extra [ffmpeg] baixa um binário PORTÁTIL do ffmpeg automaticamente no
primeiro uso (não precisa instalar ffmpeg no sistema operacional).

Uso:
    python examples/demo_video.py

Saída:
    examples/output/tracking_demo.mp4
    examples/output/tracking_demo.gif
"""

import math
import sys
from pathlib import Path

try:
    from middleware_core import BoundingBox, Detection, FrameContext, TrackingPipeline
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from middleware_core import BoundingBox, Detection, FrameContext, TrackingPipeline

import matplotlib

matplotlib.use("Agg")  # renderiza sem precisar de tela/display
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
BOX_SIZE = 60
FPS = 12

STATE_COLORS = {
    "TRACKING": "#2e7d32",  # verde
    "SEARCHING": "#f9a825",  # amarelo
    "LOST": "#c62828",  # vermelho
    "IDLE": "#9e9e9e",  # cinza
}


def build_trajectory(n_frames: int = 150):
    """Trajetória sintética: o alvo se move em uma curva pela imagem e
    desaparece por um trecho no meio, para demonstrar a recuperação de
    rastreamento (TRACKING -> SEARCHING -> LOST -> TRACKING)."""
    traj = []
    for i in range(n_frames):
        t = i / n_frames
        x = IMAGE_WIDTH * 0.5 + (IMAGE_WIDTH * 0.4) * math.sin(2 * math.pi * t * 1.5)
        y = IMAGE_HEIGHT * 0.5 + (IMAGE_HEIGHT * 0.35) * math.sin(2 * math.pi * t * 0.8 + 1.0)

        lost = 0.40 <= t <= 0.55  # simula oclusão/perda de detecção
        traj.append(None if lost else (x, y, 0.9))
    return traj


def run_pipeline(trajectory):
    """Roda o núcleo real (TrackingPipeline) sobre a trajetória sintética
    e retorna, para cada frame, o bbox usado (ou None) e o comando gerado."""
    pipeline = TrackingPipeline(lost_timeout_frames=8)
    frames_data = []

    for i, det in enumerate(trajectory):
        detections = []
        if det is not None:
            x, y, conf = det
            detections.append(
                Detection(
                    bbox=BoundingBox(x_center=x, y_center=y, width=BOX_SIZE, height=BOX_SIZE),
                    class_id=0,
                    class_name="person",
                    confidence=conf,
                )
            )
        frame = FrameContext(
            image_width=IMAGE_WIDTH,
            image_height=IMAGE_HEIGHT,
            timestamp_ns=i,
            detections=detections,
        )
        command = pipeline.process(frame)
        bbox = detections[0].bbox if detections else None
        frames_data.append((bbox, command))

    return frames_data


def render_frame_array(fig, ax, idx: int, bbox, command) -> np.ndarray:
    """Desenha um frame e retorna como array numpy RGB (H, W, 3)."""
    ax.clear()
    ax.set_xlim(0, IMAGE_WIDTH)
    ax.set_ylim(IMAGE_HEIGHT, 0)  # eixo Y invertido (origem no topo, como em imagem)
    ax.set_facecolor("#101418")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    cx, cy = IMAGE_WIDTH / 2, IMAGE_HEIGHT / 2
    ax.plot(cx, cy, marker="+", color="white", markersize=14, mew=2)

    if bbox is not None:
        rect = patches.Rectangle(
            (bbox.x_center - bbox.width / 2, bbox.y_center - bbox.height / 2),
            bbox.width,
            bbox.height,
            linewidth=2,
            edgecolor="#00e5ff",
            facecolor="none",
        )
        ax.add_patch(rect)
        ax.plot(bbox.x_center, bbox.y_center, marker="o", color="#00e5ff", markersize=5)

    scale = 150
    if abs(command.vx) > 0.01 or abs(command.vy) > 0.01:
        ax.arrow(
            cx, cy, command.vx * scale, command.vy * scale,
            head_width=12, head_length=14, fc="yellow", ec="yellow", linewidth=2,
        )

    color = STATE_COLORS.get(command.state.name, "white")
    ax.text(
        10, 25,
        f"frame {idx:03d}  estado={command.state.name}  vx={command.vx:+.2f}  vy={command.vy:+.2f}",
        color=color, fontsize=10, fontfamily="monospace",
        bbox=dict(facecolor="black", alpha=0.6, edgecolor="none", pad=4),
    )
    ax.set_title(
        "Demonstração sintética do núcleo do middleware (sem ROS2/YOLO/simulador)",
        color="white", fontsize=9,
    )
    fig.patch.set_facecolor("#101418")

    fig.canvas.draw()
    buf = np.asarray(fig.canvas.buffer_rgba())
    return buf[:, :, :3].copy()  # descarta o canal alfa


def main() -> None:
    trajectory = build_trajectory()
    frames_data = run_pipeline(trajectory)

    fig, ax = plt.subplots(figsize=(6.4, 4.8), dpi=100)
    rgb_frames = [
        render_frame_array(fig, ax, i, bbox, command)
        for i, (bbox, command) in enumerate(frames_data)
    ]
    plt.close(fig)

    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    import imageio.v2 as imageio

    mp4_path = output_dir / "tracking_demo.mp4"
    imageio.mimwrite(mp4_path, rgb_frames, fps=FPS, quality=8)
    print(f"Vídeo mp4 salvo em: {mp4_path}")

    gif_path = output_dir / "tracking_demo.gif"
    imageio.mimsave(gif_path, rgb_frames, fps=FPS)
    print(f"Gif salvo em: {gif_path}")


if __name__ == "__main__":
    main()
