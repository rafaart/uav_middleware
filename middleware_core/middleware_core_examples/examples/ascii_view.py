"""Renderização de texto (ASCII) do frame simulado + comando gerado pelo
núcleo. Não importa middleware_core nem nenhuma outra biblioteca — só
espera objetos com os atributos usados abaixo (duck typing), então
funciona com qualquer implementação compatível do contrato.

Usado pelos scripts demo_scripted.py e demo_interactive.py.
"""

from __future__ import annotations

_ARROWS = {
    (0, 0): "•",
    (1, 0): "→",
    (-1, 0): "←",
    (0, 1): "↓",
    (0, -1): "↑",
    (1, 1): "↘",
    (1, -1): "↗",
    (-1, 1): "↙",
    (-1, -1): "↖",
}


def direction_arrow(vx: float, vy: float, threshold: float = 0.02) -> str:
    h = 1 if vx > threshold else (-1 if vx < -threshold else 0)
    v = 1 if vy > threshold else (-1 if vy < -threshold else 0)
    return _ARROWS[(h, v)]


def render_frame(image_width: int, image_height: int, bbox, command, cols: int = 41, rows: int = 13) -> str:
    """bbox: objeto com x_center/y_center (em pixels), ou None se não há
    detecção no frame. command: objeto com vx, vy e state.name."""
    grid = [[" "] * cols for _ in range(rows)]

    center_col, center_row = cols // 2, rows // 2
    grid[center_row][center_col] = "O"  # centro da imagem (referência)

    if bbox is not None:
        col = int(bbox.x_center / image_width * (cols - 1))
        row = int(bbox.y_center / image_height * (rows - 1))
        col = max(0, min(cols - 1, col))
        row = max(0, min(rows - 1, row))
        grid[row][col] = "X"  # alvo escolhido pelo núcleo

    border = "+" + "-" * cols + "+"
    lines = [border] + ["|" + "".join(r) + "|" for r in grid] + [border]

    arrow = direction_arrow(command.vx, command.vy)
    lines.append(
        f"comando -> vx={command.vx:+.2f}  vy={command.vy:+.2f}  "
        f"direção={arrow}  estado={command.state.name}"
    )
    return "\n".join(lines)
