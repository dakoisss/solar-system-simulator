"""camera.py - Zoom, desplazamiento y conversión mundo <-> pantalla.

Made With ❤️ By Dakoi
"""
import math

from pygame.math import Vector2

ZOOM_FACTOR = 1.1
MIN_SCALE = 2.0
MAX_SCALE = 50_000.0

# Escala inicial (px por unidad visual) según el modo
DEFAULT_SCALE = {False: 12.0,    # lineal: Neptuno (30 UA) ≈ 360 px
                 True: 100.0}    # log: Neptuno ≈ 100·ln(31) ≈ 343 px


def compress(pos_ua, k=1.0):
    """Escala logarítmica de distancia preservando la dirección."""
    r = pos_ua.length()
    if r == 0:
        return Vector2(0, 0)
    return pos_ua * (k * math.log(1 + r) / r)


class Camera:
    def __init__(self, screen_size, log_scale=True):
        self.screen_size = screen_size
        self.log_scale = log_scale
        self.reset()

    def reset(self):
        w, h = self.screen_size
        self.offset = Vector2(w / 2, h / 2)       # posición del Sol en pantalla
        self.scale = DEFAULT_SCALE[self.log_scale]

    def toggle_log(self):
        self.log_scale = not self.log_scale
        self.reset()

    # --- conversiones -----------------------------------------------------
    def _to_visual(self, pos_ua):
        return compress(pos_ua) if self.log_scale else pos_ua

    def world_to_screen(self, pos_ua):
        """screen = offset + world · scale (world = vector visual)."""
        return self.offset + self._to_visual(pos_ua) * self.scale

    def screen_to_world(self, screen_pos):
        """Devuelve el vector visual (no UA si la escala es log)."""
        return (Vector2(screen_pos) - self.offset) / self.scale

    # --- zoom y pan -------------------------------------------------------
    def zoom_at(self, mouse_pos, direction):
        """Zoom centrado en el cursor: el punto bajo el ratón queda fijo."""
        mouse = Vector2(mouse_pos)
        world_before = (mouse - self.offset) / self.scale
        factor = ZOOM_FACTOR if direction > 0 else 1 / ZOOM_FACTOR
        self.scale = max(MIN_SCALE, min(MAX_SCALE, self.scale * factor))
        self.offset = mouse - world_before * self.scale

    def pan(self, delta):
        self.offset += Vector2(delta)
