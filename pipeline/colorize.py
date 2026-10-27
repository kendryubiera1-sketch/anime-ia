"""Paso 3: colorear viñetas.

Ahora mismo devuelve la imagen tal cual. Aquí se conecta un modelo de colorización
(manga-colorization, ControlNet + referencias de color por personaje, o una API).
Para que los colores no cambien entre escenas, guarda una imagen de referencia
por personaje en input/refs/ y pásala al modelo.
"""


def colorize_panel(image_path: str) -> str:
    return image_path
