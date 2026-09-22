"""Cálculo do vetor de erro entre o centro do bounding box detectado e o
centro da imagem. O erro é normalizado por metade da dimensão da imagem,
de forma que o núcleo funcione independente da resolução da câmera usada
em cada simulação/hardware."""

from __future__ import annotations

from middleware_core.contracts import BoundingBox


def compute_error(bbox: BoundingBox, image_width: int, image_height: int) -> tuple[float, float]:
    """Retorna (err_x, err_y) normalizados em aproximadamente [-1.0, 1.0].

    err_x > 0  => alvo está à direita do centro da imagem
    err_y > 0  => alvo está abaixo do centro da imagem
    """
    if image_width <= 0 or image_height <= 0:
        raise ValueError("image_width e image_height devem ser positivos")

    img_cx = image_width / 2.0
    img_cy = image_height / 2.0

    err_x = (bbox.x_center - img_cx) / img_cx
    err_y = (bbox.y_center - img_cy) / img_cy

    return err_x, err_y
