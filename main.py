"""main.py - Simulador del sistema solar con pygame.

Made With ❤️ By Dakoi

Controles:
  Rueda ratón ........ zoom (centrado en el cursor)
  Arrastrar (cen/der). mover la vista
  ESPACIO ............ pausa
  + / - .............. más rápido / más lento
  T .................. mostrar/ocultar estelas
  L .................. alternar escala lineal / logarítmica
  O .................. mostrar/ocultar órbitas
  R .................. reiniciar vista
  S .................. guardar captura
  ESC ................ salir
"""
import math
import random

import pygame
from pygame.math import Vector2

from bodies import SUN_COLOR, SUN_RADIUS_PX, make_bodies
from camera import Camera

W, H = 1280, 800
FPS = 60
TRAIL_EVERY = 2            # añadir punto a la estela cada N frames
TRAIL_CHUNKS = 12          # tramos de brillo creciente en cada estela
MIN_TS, MAX_TS = 0.125, 4096.0


def fade(color, f):
    """Atenúa un color hacia el negro (fondo negro)."""
    return (int(color[0] * f), int(color[1] * f), int(color[2] * f))


def make_stars(n=250):
    stars = []
    for _ in range(n):
        b = random.randint(40, 160)
        stars.append(((random.randrange(W), random.randrange(H)), (b, b, b)))
    return stars


def draw_trail(screen, cam, body):
    """Polilínea en tramos con brillo creciente hacia la posición actual."""
    pts = [cam.world_to_screen(p) for p in body.trail]
    n = len(pts)
    if n < 2:
        return
    chunk = max(2, n // TRAIL_CHUNKS)
    start = 0
    while start < n - 1:
        end = min(n, start + chunk + 1)        # +1: los tramos se solapan
        f = 0.12 + 0.88 * (end / n)
        pygame.draw.lines(screen, fade(body.color, f), False,
                          [(p.x, p.y) for p in pts[start:end]], 1)
        start += chunk


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Simulador del sistema solar")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas,menlo,monospace", 16)
    small = pygame.font.SysFont("consolas,menlo,monospace", 14)

    cam = Camera((W, H), log_scale=True)
    bodies = make_bodies(random_phase=True)
    stars = make_stars()

    t_sim = 0.0                 # días simulados
    time_scale = 2.0            # días por frame
    paused = False
    show_trails = True
    show_orbits = True
    dragging = False
    frame = 0
    shot_n = 0

    running = True
    while running:
        # ------------------------------------------------------------ eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                if event.y != 0:
                    cam.zoom_at(pygame.mouse.get_pos(), 1 if event.y > 0 else -1)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (2, 3):
                dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button in (2, 3):
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                cam.pan(event.rel)
            elif event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_ESCAPE:
                    running = False
                elif k == pygame.K_SPACE:
                    paused = not paused
                elif k in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    time_scale = min(MAX_TS, time_scale * 2)
                elif k in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    time_scale = max(MIN_TS, time_scale / 2)
                elif k == pygame.K_t:
                    show_trails = not show_trails
                elif k == pygame.K_l:
                    cam.toggle_log()
                elif k == pygame.K_o:
                    show_orbits = not show_orbits
                elif k == pygame.K_r:
                    cam.reset()
                elif k == pygame.K_s:
                    shot_n += 1
                    pygame.image.save(screen, f"captura_{shot_n:03d}.png")

        # --------------------------------------------------------- actualizar
        if not paused:
            t_sim += time_scale
            frame += 1
            record = frame % TRAIL_EVERY == 0
            for b in bodies:
                b.update(t_sim, record_trail=record)

        # ------------------------------------------------------------ dibujar
        screen.fill((0, 0, 0))
        for p, c in stars:
            screen.set_at(p, c)

        sun_pos = cam.world_to_screen(Vector2(0, 0))

        if show_orbits:
            for b in bodies:
                pts = [cam.world_to_screen(p) for p in b.orbit_points]
                pygame.draw.lines(screen, fade(b.color, 0.25), True,
                                  [(p.x, p.y) for p in pts], 1)

        if show_trails:
            for b in bodies:
                draw_trail(screen, cam, b)

        pygame.draw.circle(screen, SUN_COLOR, (int(sun_pos.x), int(sun_pos.y)),
                           SUN_RADIUS_PX)

        mouse = Vector2(pygame.mouse.get_pos())
        hovered = None
        for b in bodies:
            sp = cam.world_to_screen(b.pos)
            pygame.draw.circle(screen, b.color, (int(sp.x), int(sp.y)),
                               b.radius_px)
            if sp.distance_to(mouse) <= b.radius_px + 6:
                hovered = (b, sp)

        # Etiqueta al pasar el ratón
        if hovered:
            b, sp = hovered
            label = small.render(b.name, True, (255, 255, 255))
            screen.blit(label, (sp.x + b.radius_px + 6, sp.y - 8))

        # HUD
        years = t_sim / 365.25
        lines = [
            f"Tiempo simulado: {t_sim:,.0f} días  ({years:.2f} años)",
            f"Velocidad: {time_scale:g} días/frame"
            + ("   [PAUSA]" if paused else ""),
            f"Escala: {'logarítmica' if cam.log_scale else 'lineal'}   "
            f"zoom: {cam.scale:.1f} px/u",
            f"FPS: {clock.get_fps():.0f}",
        ]
        if hovered:
            b = hovered[0]
            lines.append(f"{b.name}: {b.distance:.3f} UA, {b.speed_kms:.1f} km/s, "
                         f"T={b.period:,.0f} d")
        for i, text in enumerate(lines):
            screen.blit(font.render(text, True, (220, 220, 220)), (10, 8 + i * 20))

        hint = small.render(
            "Rueda: zoom | Arrastrar: mover | Espacio: pausa | +/-: velocidad | "
            "T: estelas | L: escala | O: órbitas | R: reiniciar | S: captura",
            True, (130, 130, 130))
        screen.blit(hint, (10, H - 22))

        watermark = small.render("Made With ❤️ By Dakoi", True, (180, 180, 180))
        watermark.set_alpha(160)
        screen.blit(watermark, (W - watermark.get_width() - 10,
                                H - watermark.get_height() - 8))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
