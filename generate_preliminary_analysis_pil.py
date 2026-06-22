"""Create repeatable preliminary analytical-check graphics without external plotting packages.

The results are explicitly analytical screening estimates, not finite-element results.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "simulations"
OUT.mkdir(exist_ok=True)

E = 69e9
YIELD = 276e6
RHO = 2700.0
L = 0.180
B = 0.025
T = 0.008
DESIGN_LOAD = 150.0
LOADS = [90.0, 120.0, 150.0]
CASE_NAMES = ["Nominal traverse", "Uneven terrain", "Obstacle contact"]
AREA = B * T
I = B * T**3 / 12.0
C = T / 2.0


def stress_mpa(load: float) -> float:
    return load * L * C / I / 1e6


def deflection_mm(load: float) -> float:
    return load * L**3 / (3.0 * E * I) * 1e3


SIGMA = stress_mpa(DESIGN_LOAD)
DEFLECTION = deflection_mm(DESIGN_LOAD)
SF = YIELD / (SIGMA * 1e6)
BETA = 1.87510407
F1 = (BETA**2 / (2.0 * math.pi * L**2)) * math.sqrt(E * I / (RHO * AREA))


BG = "#F7F8F7"
INK = "#1E2528"
MUTED = "#596467"
GRID = "#D9DFDD"
GREEN = "#1B8A5A"
ORANGE = "#D95F02"
BLUE = "#4F7D9A"
RED = "#B2473D"
DARK = "#414B4E"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


F_TITLE = font(42, True)
F_SUB = font(24)
F_BODY = font(21)
F_SMALL = font(17)
F_BOLD = font(21, True)


def canvas(width: int = 1800, height: int = 1000) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    return image, draw


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, f=F_BODY, fill: str = INK, anchor: str | None = None) -> None:
    draw.text(xy, value, font=f, fill=fill, anchor=anchor)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int = 20) -> None:
    draw.rounded_rectangle(box, radius, fill="#FFFFFF", outline="#D7DEDA", width=2)


def badge(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str) -> None:
    x, y = xy
    box = draw.textbbox((x, y), value, font=F_SMALL)
    draw.rounded_rectangle((x - 12, y - 8, box[2] + 12, box[3] + 8), 11, fill="#E8EFEC", outline="#A9BBB1", width=1)
    text(draw, (x, y), value, F_SMALL, "#3D4B4D")


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str, width: int = 4) -> None:
    draw.line((*start, *end), fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    size = 17
    p1 = (end[0] - size * math.cos(angle - 0.5), end[1] - size * math.sin(angle - 0.5))
    p2 = (end[0] - size * math.cos(angle + 0.5), end[1] - size * math.sin(angle + 0.5))
    draw.polygon([end, p1, p2], fill=color)


def static_link_plot() -> None:
    image, draw = canvas()
    text(draw, (70, 52), "Wheel-leg link preliminary static check", F_TITLE)
    text(draw, (72, 110), "Analytical cantilever model; screening only, not a finite-element result.", F_SUB, MUTED)
    panel(draw, (70, 175, 890, 895))
    panel(draw, (935, 175, 1730, 895))
    badge(draw, (105, 210), "Peak stress occurs at the fixed end")

    # Link schematic with stress-like analytical colour mapping.
    x0, x1, y = 185, 780, 485
    draw.rectangle((140, 320, 185, 650), fill=DARK, outline=INK, width=2)
    for idx in range(52):
        f = idx / 51
        r = int(210 + 35 * (1 - f))
        g = int(80 + 130 * f)
        b = int(50 + 120 * f)
        sx = int(x0 + (x1 - x0) * f)
        ex = int(x0 + (x1 - x0) * (f + 1 / 51))
        draw.rectangle((sx, y - 22, ex + 1, y + 22), fill=(r, g, b))
    draw.line((x0, y - 22, x1, y - 22), fill=INK, width=3)
    draw.line((x0, y + 22, x1, y + 22), fill=INK, width=3)
    arrow(draw, (x1, 355), (x1, y - 28), ORANGE, 5)
    text(draw, (x1 - 8, 315), "150 N", F_BOLD, "#B94700", anchor="ma")
    text(draw, (195, 665), "fixed joint", F_SMALL, MUTED)
    draw.line((185, 635, 260, 640), fill=MUTED, width=2)
    text(draw, (420, 560), "L = 180 mm", F_BODY, MUTED, anchor="ma")
    text(draw, (405, 607), "25 x 8 mm candidate aluminum link", F_SMALL, MUTED, anchor="ma")
    text(draw, (185, 720), f"Analytical peak stress: {SIGMA:.1f} MPa", F_BOLD, GREEN)
    text(draw, (185, 755), f"Analytical tip deflection: {DEFLECTION:.2f} mm", F_BOLD, BLUE)
    text(draw, (185, 790), f"Yield-reference screening factor: {SF:.2f}", F_BOLD, ORANGE)

    # Stress and deflection curves.
    badge(draw, (970, 210), f"Design point: {DESIGN_LOAD:.0f} N / {DEFLECTION:.2f} mm")
    gx0, gx1, gy0, gy1 = 1015, 1670, 360, 745
    draw.line((gx0, gy1, gx1, gy1), fill=INK, width=2)
    draw.line((gx0, gy0, gx0, gy1), fill=INK, width=2)
    for tick in range(0, 181, 30):
        x = gx0 + (gx1 - gx0) * tick / 180
        draw.line((x, gy1, x, gy1 + 8), fill=INK, width=2)
        text(draw, (int(x), gy1 + 17), str(tick), F_SMALL, MUTED, anchor="ma")
    for tick in range(0, 121, 20):
        yy = gy1 - (gy1 - gy0) * tick / 120
        draw.line((gx0 - 8, yy, gx1, yy), fill=GRID, width=1)
        text(draw, (gx0 - 14, int(yy)), str(tick), F_SMALL, MUTED, anchor="rm")
    points_stress = []
    points_def = []
    for load in range(0, 181, 3):
        x = gx0 + (gx1 - gx0) * load / 180
        points_stress.append((int(x), int(gy1 - (gy1 - gy0) * stress_mpa(load) / 120)))
        points_def.append((int(x), int(gy1 - (gy1 - gy0) * deflection_mm(load) / 5.0)))
    draw.line(points_stress, fill=GREEN, width=5)
    draw.line(points_def, fill=BLUE, width=4)
    yield_y = int(gy1 - (gy1 - gy0) * (YIELD / 1e6) / 120)
    draw.line((gx0, yield_y, gx1, yield_y), fill=RED, width=2)
    draw.text((gx1 - 4, yield_y - 25), "candidate yield reference", font=F_SMALL, fill=RED, anchor="ra")
    dx = int(gx0 + (gx1 - gx0) * DESIGN_LOAD / 180)
    dy = int(gy1 - (gy1 - gy0) * SIGMA / 120)
    draw.line((dx, gy0, dx, gy1), fill=ORANGE, width=2)
    draw.ellipse((dx - 8, dy - 8, dx + 8, dy + 8), fill=ORANGE, outline="#FFFFFF", width=2)
    text(draw, (dx + 16, dy - 50), f"{SIGMA:.1f} MPa\nSF = {SF:.2f}", F_BODY, INK)
    text(draw, (gx0, 790), "Applied link load (N)", F_BODY, INK)
    text(draw, (gx0, 320), "Green: stress (MPa)    Blue: tip deflection (mm, scaled)", F_SMALL, MUTED)
    image.save(OUT / "static_link_check.png", quality=96)


def load_case_plot() -> None:
    image, draw = canvas(1600, 950)
    text(draw, (70, 48), "Preliminary terrain-load cases", F_TITLE)
    text(draw, (72, 107), "Input loads are design assumptions for comparative screening; they are not measured field loads.", F_SUB, MUTED)
    panel(draw, (70, 170, 1530, 850))
    badge(draw, (106, 207), "Single-link analytical comparison")
    base_y, top_y = 710, 330
    left = 175
    group_gap = 390
    max_stress = 125.0
    for idx, (name, load) in enumerate(zip(CASE_NAMES, LOADS)):
        cx = left + idx * group_gap
        draw.line((cx - 90, base_y, cx + 160, base_y), fill=GRID, width=2)
        stress = stress_mpa(load)
        de = deflection_mm(load)
        bar_h = int((base_y - top_y) * stress / max_stress)
        color = ["#4A8F73", "#D99A3D", "#C65A4A"][idx]
        draw.rounded_rectangle((cx, base_y - bar_h, cx + 105, base_y), 8, fill=color)
        text(draw, (cx + 52, base_y - bar_h - 33), f"{stress:.1f} MPa", F_BOLD, INK, anchor="ma")
        text(draw, (cx + 52, base_y + 23), f"{int(load)} N", F_BODY, MUTED, anchor="ma")
        # Deflection marker on a separate right-side display scale.
        line_x = cx + 165
        dot_y = base_y - int((base_y - top_y) * de / 5.0)
        draw.line((line_x, base_y, line_x, top_y), fill="#C8D3D7", width=4)
        draw.ellipse((line_x - 10, dot_y - 10, line_x + 10, dot_y + 10), fill=BLUE, outline="#FFFFFF", width=2)
        text(draw, (line_x, dot_y - 40), f"{de:.2f} mm", F_BOLD, BLUE, anchor="ma")
        text(draw, (cx + 52, 760), name, F_SMALL, INK, anchor="ma")
    draw.line((135, 264, 135, 710), fill=INK, width=2)
    for tick in range(0, 121, 20):
        yy = base_y - int((base_y - top_y) * tick / max_stress)
        draw.line((135, yy, 1430, yy), fill=GRID, width=1)
        text(draw, (120, yy), str(tick), F_SMALL, MUTED, anchor="rm")
    text(draw, (135, 235), "Bending stress (MPa)", F_BODY, INK)
    text(draw, (1070, 250), "Bars: stress     Blue dot: tip deflection", F_BODY, MUTED)
    text(draw, (1070, 770), f"Candidate yield reference: {YIELD / 1e6:.0f} MPa", F_BODY, RED)
    text(draw, (1070, 807), "No contact, clearance, tire compliance or full-chassis flexibility is included.", F_SMALL, MUTED)
    image.save(OUT / "terrain_load_cases.png", quality=96)


def modal_plot() -> None:
    image, draw = canvas()
    text(draw, (70, 52), "Wheel-leg link first bending frequency estimate", F_TITLE)
    text(draw, (72, 110), "Euler-Bernoulli cantilever estimate for the isolated link; wheels, joints and chassis are excluded.", F_SUB, MUTED)
    panel(draw, (70, 175, 1040, 875))
    panel(draw, (1080, 175, 1730, 875))
    badge(draw, (105, 210), f"Estimated isolated-link f1 = {F1:.0f} Hz")
    gx0, gx1, mid_y = 160, 955, 520
    draw.line((gx0, mid_y, gx1, mid_y), fill="#606A6D", width=2)
    draw.rectangle((130, mid_y - 140, 160, mid_y + 140), fill=DARK, outline=INK, width=2)
    beta = BETA
    alpha = (math.cosh(beta) + math.cos(beta)) / (math.sinh(beta) + math.sin(beta))
    points = []
    for i in range(181):
        xi = i / 180
        phi = math.cosh(beta * xi) - math.cos(beta * xi) - alpha * (math.sinh(beta * xi) - math.sin(beta * xi))
        # normalize with the known tip value from a dense sample
        tip = math.cosh(beta) - math.cos(beta) - alpha * (math.sinh(beta) - math.sin(beta))
        yy = mid_y - phi / tip * 155
        xx = gx0 + (gx1 - gx0) * xi
        points.append((int(xx), int(yy)))
    draw.line(points, fill=ORANGE, width=7)
    # soft fill between mode shape and neutral line
    polygon = [(gx0, mid_y)] + points + [(gx1, mid_y)]
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.polygon(polygon, fill=(242, 193, 125, 110))
    image.alpha_composite(overlay) if image.mode == "RGBA" else None
    text(draw, (510, 725), "Link length: 180 mm", F_BODY, MUTED, anchor="ma")
    text(draw, (510, 765), "Orange curve is display-scaled mode shape", F_SMALL, MUTED, anchor="ma")
    text(draw, (108, 810), "Undeformed link", F_SMALL, MUTED)

    rows = [
        ("Material candidate", "6061-series aluminum"),
        ("Elastic modulus", "69 GPa"),
        ("Density", "2700 kg/m3"),
        ("Link section", "25 x 8 mm"),
        ("Effective length", "180 mm"),
        ("Estimated f1", f"{F1:.1f} Hz"),
    ]
    y = 270
    for label, value in rows:
        text(draw, (1130, y), label, F_BODY, MUTED)
        text(draw, (1500, y), value, F_BOLD, "#1F3439", anchor="ra")
        draw.line((1130, y + 40, 1665, y + 40), fill=GRID, width=2)
        y += 84
    text(draw, (1130, 760), "Interpretation", F_BOLD, INK)
    text(draw, (1130, 802), "A component-level estimate only.", F_SMALL, MUTED)
    text(draw, (1130, 830), "Full modal work must include joints, wheels,", F_SMALL, MUTED)
    text(draw, (1130, 855), "chassis and sensor payload mass.", F_SMALL, MUTED)
    image.save(OUT / "modal_frequency_estimate.png", quality=96)


def write_metadata() -> None:
    data = {
        "analysis_type": "preliminary analytical screening; not finite element analysis",
        "model": "single wheel-leg link treated as a cantilever beam",
        "inputs": {
            "material_candidate": "6061-series aluminum",
            "elastic_modulus_pa": E,
            "yield_reference_pa": YIELD,
            "density_kg_m3": RHO,
            "effective_length_m": L,
            "section_width_m": B,
            "section_thickness_m": T,
            "design_load_n": DESIGN_LOAD,
        },
        "results": {
            "second_moment_m4": I,
            "design_stress_mpa": SIGMA,
            "design_tip_deflection_mm": DEFLECTION,
            "screening_safety_factor": SF,
            "isolated_link_first_bending_frequency_hz": F1,
        },
        "limitations": [
            "No contact, joint clearance, fastener preload, tire compliance or chassis flexibility is included.",
            "Load cases are comparative design assumptions, not measured field loads.",
            "The modal estimate excludes wheel, motor, sensor payload and joint compliance.",
        ],
    }
    (OUT / "preliminary_analysis_results.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Preliminary Structural Verification\n\n"
        "These files show repeatable analytical screening calculations for the rover wheel-leg link. "
        "They are **not** SolidWorks Simulation or ANSYS finite-element results.\n\n"
        "## Model\n\n"
        "A 180 mm long, 25 x 8 mm rectangular candidate 6061-series aluminum link is treated as a cantilever beam. "
        "The calculation uses `sigma = M*c/I`, `delta = P*L^3/(3*E*I)`, and an Euler-Bernoulli first bending-mode estimate.\n\n"
        f"At the 150 N design case: stress = {SIGMA:.1f} MPa, tip deflection = {DEFLECTION:.2f} mm, "
        f"screening safety factor = {SF:.2f}, and isolated-link first bending estimate = {F1:.1f} Hz.\n\n"
        "## Limits\n\n"
        "A detailed design decision requires material certificates, measured terrain loads, joint contact/clearance, "
        "wheel and payload mass, and full-assembly finite-element/modal analysis.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    static_link_plot()
    load_case_plot()
    modal_plot()
    write_metadata()
    print(f"Generated {OUT}")
