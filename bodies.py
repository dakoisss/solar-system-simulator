"""bodies.py - Datos astronómicos y cálculo orbital (mecánica kepleriana).

Unidades: distancias en UA, tiempos en días terrestres.
Made With ❤️ By Dakoi
"""
import math
from collections import deque

from pygame.math import Vector2

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
AU_KM = 149_597_870.0                  # 1 UA en km
YEAR_DAYS = 365.25
GM = 4 * math.pi ** 2                  # UA^3 / año^2 (Sol)
UA_PER_YEAR_TO_KMS = AU_KM / (YEAR_DAYS * 86400.0)
TRAIL_LEN = 500                        # puntos máximos por estela

# nombre, a (UA), e, T (días), radio visual (px), color RGB
PLANET_DATA = [
    ("Mercurio", 0.3871, 0.2056, 87.97,    3,  (150, 150, 150)),
    ("Venus",    0.7233, 0.0068, 224.70,   5,  (230, 200, 120)),
    ("Tierra",   1.0000, 0.0167, 365.25,   5,  (70, 130, 220)),
    ("Marte",    1.5237, 0.0934, 686.97,   4,  (200, 80, 50)),
    ("Júpiter",  5.2026, 0.0489, 4332.59,  10, (210, 160, 110)),
    ("Saturno",  9.5549, 0.0565, 10759.22, 9,  (220, 200, 140)),
    ("Urano",    19.2184, 0.0457, 30688.5, 7,  (150, 220, 230)),
    ("Neptuno",  30.110, 0.0113, 60182.0,  7,  (60, 90, 200)),
]

SUN_COLOR = (255, 210, 60)
SUN_RADIUS_PX = 18


# ---------------------------------------------------------------------------
# Núcleo matemático
# ---------------------------------------------------------------------------
def solve_kepler(M, e, tol=1e-8, max_iter=20):
    """Resuelve E - e*sin(E) = M con Newton-Raphson."""
    E = M
    for _ in range(max_iter):
        f = E - e * math.sin(E) - M
        fp = 1 - e * math.cos(E)
        dE = f / fp
        E -= dE
        if abs(dE) < tol:
            break
    return E


def orbital_position(a, e, period, t):
    """Posición (Vector2, en UA) con el Sol en el origen, en el tiempo t (días)."""
    M = (2 * math.pi * t / period) % (2 * math.pi)
    E = solve_kepler(M, e)
    nu = 2 * math.atan2(math.sqrt(1 + e) * math.sin(E / 2),
                        math.sqrt(1 - e) * math.cos(E / 2))
    r = a * (1 - e * math.cos(E))
    return Vector2(r * math.cos(nu), r * math.sin(nu))


# ---------------------------------------------------------------------------
# Clase Body
# ---------------------------------------------------------------------------
class Body:
    def __init__(self, name, a, e, period, radius_px, color, phase_days=0.0):
        self.name = name
        self.a = a
        self.e = e
        self.period = period
        self.radius_px = radius_px
        self.color = color
        self.angle_offset = phase_days          # fase inicial (en días)
        self.trail = deque(maxlen=TRAIL_LEN)    # posiciones pasadas en UA
        self.pos = orbital_position(a, e, period, phase_days)
        self._orbit_pts = self._compute_orbit()

    def update(self, t, record_trail=False):
        """Actualiza la posición para el tiempo simulado t (días)."""
        self.pos = orbital_position(self.a, self.e, self.period,
                                    t + self.angle_offset)
        if record_trail:
            self.trail.append(Vector2(self.pos))

    @property
    def distance(self):
        """Distancia actual al Sol (UA)."""
        return self.pos.length()

    @property
    def speed_kms(self):
        """Velocidad instantánea (km/s): v = sqrt(GM (2/r - 1/a))."""
        v = math.sqrt(GM * (2 / self.distance - 1 / self.a))
        return v * UA_PER_YEAR_TO_KMS

    def _compute_orbit(self, n=360):
        """Puntos de la elipse completa (UA), parametrizada por E."""
        b = self.a * math.sqrt(1 - self.e ** 2)
        pts = []
        for i in range(n):
            E = 2 * math.pi * i / n
            pts.append(Vector2(self.a * (math.cos(E) - self.e),
                               b * math.sin(E)))
        return pts

    @property
    def orbit_points(self):
        return self._orbit_pts


def make_bodies(random_phase=True, rng=None):
    import random
    rng = rng or random
    bodies = []
    for name, a, e, T, r, col in PLANET_DATA:
        phase = rng.random() * T if random_phase else 0.0
        bodies.append(Body(name, a, e, T, r, col, phase))
    return bodies


# ---------------------------------------------------------------------------
# Pruebas de verificación (python bodies.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    for name, a, e, T, *_ in PLANET_DATA:
        p0 = orbital_position(a, e, T, 0.0)
        p1 = orbital_position(a, e, T, T)
        assert (p0 - p1).length() < 1e-3, f"{name}: no cierra la órbita"
        # Tercera ley: T^2 = a^3 (años, UA)
        assert abs((T / YEAR_DAYS) ** 2 - a ** 3) / a ** 3 < 0.02, name
    print("OK: cierre de órbita y 3ª ley de Kepler")

    merc = PLANET_DATA[0]
    rs = [orbital_position(merc[1], merc[2], merc[3], merc[3] * i / 2000).length()
          for i in range(2000)]
    print(f"Mercurio: r_min={min(rs):.3f} (≈0.307)  r_max={max(rs):.3f} (≈0.467)")

    b = make_bodies(random_phase=False)
    print("Velocidades en t=0 (km/s):",
          {x.name: round(x.speed_kms, 1) for x in b})
