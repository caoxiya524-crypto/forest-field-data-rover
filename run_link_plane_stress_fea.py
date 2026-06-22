"""Local 2D plane-stress FEA for the rover's representative lower wheel-leg link.

The model is intentionally scoped: a rectangular link is meshed with constant-strain
triangular elements, fixed at the chassis-side joint interface, and loaded at the
wheel-side interface. It writes mesh, von Mises stress, total deformation figures and
machine-readable results. This is a real numerical finite-element calculation, not an
illustrative stress map.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "fea"
OUT.mkdir(exist_ok=True)

# Representative lower wheel-leg link and scenario inputs.
L = 0.180  # m, chassis-side joint to wheel-side joint effective span
W = 0.025  # m, in-plane link width
THICKNESS = 0.008  # m, out-of-plane thickness
E = 69e9  # Pa, candidate 6061-series aluminium elastic modulus
NU = 0.33
RHO = 2700.0  # kg/m^3, retained as a documented material input
TOTAL_LOAD = 150.0  # N, downward load distributed over distal joint interface
NX = 42
NY = 10

BG = "#F7F8F7"
INK = "#1E2528"
MUTED = "#596467"
GRID = "#D9DFDD"
ORANGE = "#D95F02"
DARK = "#404B4E"


def font(size: int, bold: bool = False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


F_TITLE = font(41, True)
F_SUB = font(23)
F_BODY = font(20)
F_BOLD = font(21, True)
F_SMALL = font(16)


def draw_text(draw, xy, value, f=F_BODY, fill=INK, anchor=None):
    draw.text(xy, value, font=f, fill=fill, anchor=anchor)


def draw_panel(draw, box, radius=20):
    draw.rounded_rectangle(box, radius, fill="#FFFFFF", outline="#D7DEDA", width=2)


def draw_badge(draw, xy, value):
    x, y = xy
    bb = draw.textbbox((x, y), value, font=F_SMALL)
    draw.rounded_rectangle((x - 11, y - 8, bb[2] + 11, bb[3] + 8), 10, fill="#E8EFEC", outline="#A9BBB1", width=1)
    draw_text(draw, (x, y), value, F_SMALL, "#3D4B4D")


def arrow(draw, start, end, color=ORANGE, width=4):
    draw.line((*start, *end), fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    size = 16
    p1 = (end[0] - size * math.cos(angle - 0.52), end[1] - size * math.sin(angle - 0.52))
    p2 = (end[0] - size * math.cos(angle + 0.52), end[1] - size * math.sin(angle + 0.52))
    draw.polygon([end, p1, p2], fill=color)


def colormap(value: float, vmin: float, vmax: float) -> tuple[int, int, int]:
    """Blue-cyan-yellow-red engineering contour map."""
    if vmax <= vmin:
        t = 0.0
    else:
        t = max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))
    stops = [
        (0.00, (35, 68, 146)),
        (0.25, (34, 157, 197)),
        (0.50, (92, 190, 115)),
        (0.73, (248, 214, 74)),
        (1.00, (204, 54, 41)),
    ]
    for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
        if t <= t1:
            alpha = (t - t0) / (t1 - t0)
            return tuple(round(c0[k] + alpha * (c1[k] - c0[k])) for k in range(3))
    return stops[-1][1]


def build_mesh():
    xs = np.linspace(0.0, L, NX + 1)
    ys = np.linspace(-W / 2.0, W / 2.0, NY + 1)
    nodes = np.array([(x, y) for y in ys for x in xs], dtype=float)

    def node(i: int, j: int) -> int:
        return j * (NX + 1) + i

    elements = []
    for j in range(NY):
        for i in range(NX):
            n0, n1 = node(i, j), node(i + 1, j)
            n2, n3 = node(i + 1, j + 1), node(i, j + 1)
            elements.append((n0, n1, n2))
            elements.append((n0, n2, n3))
    return nodes, np.array(elements, dtype=int), node


def triangle_b_matrix(coords: np.ndarray):
    x1, y1 = coords[0]
    x2, y2 = coords[1]
    x3, y3 = coords[2]
    twice_area = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    if twice_area <= 0:
        raise ValueError("Element orientation must be counter-clockwise")
    b = np.array([y2 - y3, y3 - y1, y1 - y2], dtype=float)
    c = np.array([x3 - x2, x1 - x3, x2 - x1], dtype=float)
    B = np.array(
        [
            [b[0], 0.0, b[1], 0.0, b[2], 0.0],
            [0.0, c[0], 0.0, c[1], 0.0, c[2]],
            [c[0], b[0], c[1], b[1], c[2], b[2]],
        ],
        dtype=float,
    ) / twice_area
    return B, twice_area / 2.0


def solve_fea():
    nodes, elements, node = build_mesh()
    ndof = nodes.shape[0] * 2
    k_global = np.zeros((ndof, ndof), dtype=float)
    dmat = E / (1.0 - NU**2) * np.array([[1.0, NU, 0.0], [NU, 1.0, 0.0], [0.0, 0.0, (1.0 - NU) / 2.0]])

    element_data = []
    for element in elements:
        coords = nodes[element]
        bmat, area = triangle_b_matrix(coords)
        ke = THICKNESS * area * (bmat.T @ dmat @ bmat)
        dofs = np.array([2 * element[0], 2 * element[0] + 1, 2 * element[1], 2 * element[1] + 1, 2 * element[2], 2 * element[2] + 1])
        k_global[np.ix_(dofs, dofs)] += ke
        element_data.append((bmat, dofs, area))

    force = np.zeros(ndof, dtype=float)
    right_nodes = [node(NX, j) for j in range(NY + 1)]
    for n in right_nodes:
        force[2 * n + 1] = -TOTAL_LOAD / len(right_nodes)
    fixed_nodes = [node(0, j) for j in range(NY + 1)]
    fixed_dofs = np.array([d for n in fixed_nodes for d in (2 * n, 2 * n + 1)], dtype=int)
    free_dofs = np.setdiff1d(np.arange(ndof), fixed_dofs)

    displacement = np.zeros(ndof, dtype=float)
    displacement[free_dofs] = np.linalg.solve(k_global[np.ix_(free_dofs, free_dofs)], force[free_dofs])

    stresses = []
    for bmat, dofs, _ in element_data:
        strain = bmat @ displacement[dofs]
        sx, sy, txy = dmat @ strain
        von_mises = math.sqrt(sx * sx - sx * sy + sy * sy + 3.0 * txy * txy)
        stresses.append((sx, sy, txy, von_mises))
    stresses = np.array(stresses)
    ux = displacement[0::2]
    uy = displacement[1::2]
    total_disp = np.sqrt(ux**2 + uy**2)
    return nodes, elements, displacement.reshape(-1, 2), total_disp, stresses, right_nodes, fixed_nodes


def map_point(point, box, deformed=None, scale=1.0):
    x0, y0, x1, y1 = box
    x, y = point
    if deformed is not None:
        x += scale * deformed[0]
        y += scale * deformed[1]
    px = x0 + (x / L) * (x1 - x0)
    py = (y0 + y1) / 2.0 - (y / W) * (y1 - y0)
    return int(round(px)), int(round(py))


def draw_colorbar(draw, box, vmin, vmax, label, decimals=1):
    x0, y0, x1, y1 = box
    for iy in range(y0, y1):
        value = vmax - (vmax - vmin) * (iy - y0) / max(1, y1 - y0 - 1)
        draw.line((x0, iy, x1, iy), fill=colormap(value, vmin, vmax), width=1)
    draw.rectangle(box, outline=INK, width=1)
    for t in [0.0, 0.5, 1.0]:
        y = int(y1 - (y1 - y0) * t)
        val = vmin + (vmax - vmin) * t
        draw.line((x1, y, x1 + 7, y), fill=INK, width=1)
        draw_text(draw, (x1 + 12, y), f"{val:.{decimals}f}", F_SMALL, MUTED, anchor="lm")
    draw_text(draw, (x0, y0 - 31), label, F_SMALL, INK)


def draw_mesh_figure(nodes, elements, right_nodes, fixed_nodes):
    image = Image.new("RGB", (1800, 1000), BG)
    draw = ImageDraw.Draw(image)
    draw_text(draw, (70, 52), "Wheel-leg link finite-element mesh & boundary conditions", F_TITLE)
    draw_text(draw, (72, 110), "2D plane-stress CSTRI3 mesh; each triangle is solved numerically.", F_SUB, MUTED)
    draw_panel(draw, (70, 175, 1730, 895))
    draw_badge(draw, (105, 210), f"{len(elements)} triangular elements · {len(nodes)} nodes")
    box = (220, 330, 1450, 640)
    for element in elements:
        points = [map_point(nodes[n], box) for n in element]
        draw.line(points + [points[0]], fill="#90A0A2", width=1)
    # Fixed edge and supports.
    fixed_x = map_point(nodes[fixed_nodes[0]], box)[0]
    draw.rectangle((fixed_x - 22, 300, fixed_x, 670), fill=DARK, outline=INK, width=2)
    for y in range(308, 670, 18):
        draw.line((fixed_x - 22, y, fixed_x, y + 18), fill="#AFC0C0", width=1)
    draw_text(draw, (175, 710), "Fixed: ux = uy = 0", F_BODY, INK)
    draw.line((245, 692, fixed_x - 2, 650), fill=MUTED, width=2)
    # Distributed load at distal edge.
    right_x = map_point(nodes[right_nodes[0]], box)[0]
    for y in np.linspace(290, 342, 4):
        arrow(draw, (right_x, int(y)), (right_x, int(y + 53)), ORANGE, 3)
    draw_text(draw, (right_x - 4, 244), "150 N distributed on distal interface", F_BODY, ORANGE, anchor="ma")
    draw_text(draw, (220, 770), "Geometry: 180 × 25 × 8 mm representative lower link", F_BODY, MUTED)
    draw_text(draw, (220, 806), "Material input: candidate 6061-series aluminium, E = 69 GPa, ν = 0.33", F_BODY, MUTED)
    draw_text(draw, (220, 842), "Boundary condition is a conservative chassis-side fixed interface approximation.", F_SMALL, MUTED)
    image.save(OUT / "mesh_boundary_conditions.png", quality=96)


def draw_field_figure(nodes, elements, field, title, subtitle, label, unit, output_name, right_nodes, fixed_nodes, deformed=None, scale=1.0):
    image = Image.new("RGB", (1800, 1000), BG)
    draw = ImageDraw.Draw(image)
    draw_text(draw, (70, 52), title, F_TITLE)
    draw_text(draw, (72, 110), subtitle, F_SUB, MUTED)
    draw_panel(draw, (70, 175, 1470, 895))
    draw_panel(draw, (1510, 175, 1730, 895))
    box = (180, 335, 1320, 625)
    vmin = float(np.min(field))
    vmax = float(np.max(field))
    for element, value in zip(elements, field):
        points = [map_point(nodes[n], box, None if deformed is None else deformed[n], scale) for n in element]
        draw.polygon(points, fill=colormap(float(value), vmin, vmax), outline="#415052")
    # Fixed support.
    base_point = map_point(nodes[fixed_nodes[0]], box, None if deformed is None else deformed[fixed_nodes[0]], scale)
    draw.rectangle((base_point[0] - 20, 306, base_point[0], 653), fill=DARK, outline=INK, width=2)
    for y in range(314, 652, 18):
        draw.line((base_point[0] - 20, y, base_point[0], y + 18), fill="#AFC0C0", width=1)
    right_point = map_point(nodes[right_nodes[len(right_nodes) // 2]], box, None if deformed is None else deformed[right_nodes[len(right_nodes) // 2]], scale)
    arrow(draw, (right_point[0], 290), (right_point[0], 330), ORANGE, 3)
    draw_text(draw, (right_point[0], 246), "150 N", F_SMALL, ORANGE, anchor="ma")
    draw_colorbar(draw, (1560, 320, 1602, 710), vmin, vmax, f"{label} ({unit})", 2 if vmax < 1 else 1)
    max_index = int(np.argmax(field))
    centroid = nodes[elements[max_index]].mean(axis=0)
    centroid_p = map_point(centroid, box, None if deformed is None else deformed[elements[max_index]].mean(axis=0), scale)
    draw.ellipse((centroid_p[0] - 7, centroid_p[1] - 7, centroid_p[0] + 7, centroid_p[1] + 7), fill="#FFFFFF", outline=INK, width=2)
    draw.line((centroid_p[0] + 8, centroid_p[1] - 6, 1190, 740), fill=INK, width=2)
    draw_text(draw, (1198, 717), f"Max {label.lower()}", F_SMALL, INK)
    draw_text(draw, (1198, 747), f"{vmax:.2f} {unit}", F_BOLD, INK)
    draw_badge(draw, (105, 210), "Numerical finite-element result")
    if deformed is not None:
        draw_text(draw, (180, 770), f"Deformed shape shown with display scale ×{scale:.1f}; color is true displacement magnitude.", F_BODY, MUTED)
    else:
        draw_text(draw, (180, 770), "Element contours show the computed von Mises stress field for this boundary condition.", F_BODY, MUTED)
    draw_text(draw, (180, 815), "Scope: representative link only; joint clearance, tire compliance and full chassis coupling are not included.", F_SMALL, MUTED)
    image.save(OUT / output_name, quality=96)


def write_metadata(results):
    (OUT / "fea_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Wheel-leg Link Finite-Element Analysis\n\n"
        "This folder contains a real local finite-element calculation using a 2D plane-stress, constant-strain triangular-element mesh. "
        "It is a local wheel-leg link verification model, rather than a full-vehicle finite-element model.\n\n"
        "## Model\n\n"
        "- Representative link: 180 × 25 × 8 mm.\n"
        "- Material input: candidate 6061-series aluminum, E = 69 GPa, Poisson ratio = 0.33.\n"
        "- Mesh: 840 CSTRI3 elements and 473 nodes.\n"
        "- Constraint: chassis-side end fixed in x and y.\n"
        "- Load: 150 N downward force distributed along the wheel-side interface.\n\n"
        f"Computed maxima: von Mises stress = {results['results']['max_von_mises_mpa']:.2f} MPa; total displacement = {results['results']['max_total_displacement_mm']:.3f} mm.\n\n"
        "## Scope\n\n"
        "This is a genuine finite-element solution under the stated assumptions. It does not yet include pin contact, bearing clearance, tire compliance, bolt preload, terrain-impact time histories, complete chassis compliance, or sensor payload mass. Those belong in the next full-assembly simulation stage.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    nodes, elements, disp, total_disp, stress, right_nodes, fixed_nodes = solve_fea()
    von_mises_mpa = stress[:, 3] / 1e6
    disp_mm = total_disp * 1e3
    element_disp_mm = disp_mm[elements].mean(axis=1)
    draw_mesh_figure(nodes, elements, right_nodes, fixed_nodes)
    draw_field_figure(
        nodes,
        elements,
        von_mises_mpa,
        "Wheel-leg link finite-element von Mises stress",
        "2D plane-stress CSTRI3 solution under the defined 150 N distal joint load.",
        "von Mises stress",
        "MPa",
        "von_mises_stress.png",
        right_nodes,
        fixed_nodes,
    )
    max_u = float(np.max(total_disp))
    display_scale = min(8.0, 0.018 / max(max_u, 1e-12))
    draw_field_figure(
        nodes,
        elements,
        element_disp_mm,
        "Wheel-leg link finite-element total deformation",
        "The contour is total displacement; geometry is displayed in an amplified deformed configuration.",
        "total displacement",
        "mm",
        "total_deformation.png",
        right_nodes,
        fixed_nodes,
        deformed=disp,
        scale=display_scale,
    )
    result_data = {
        "analysis_type": "2D plane-stress finite-element analysis using constant-strain triangular elements",
        "geometry": {"length_m": L, "width_m": W, "thickness_m": THICKNESS},
        "material_candidate": {"name": "6061-series aluminum", "elastic_modulus_pa": E, "poisson_ratio": NU, "density_kg_m3": RHO},
        "boundary_condition": "all in-plane DOFs fixed at chassis-side end",
        "load_case": {"total_force_n": TOTAL_LOAD, "direction": "negative global y", "application": "distributed over distal wheel-side edge"},
        "mesh": {"element_type": "CSTRI3 plane stress", "elements": int(len(elements)), "nodes": int(len(nodes)), "dof": int(nodes.shape[0] * 2)},
        "results": {"max_von_mises_mpa": float(np.max(von_mises_mpa)), "max_total_displacement_mm": float(np.max(disp_mm)), "display_deformation_scale": display_scale},
        "limitations": [
            "Representative lower-link model only, not full rover assembly.",
            "No pin contact, joint clearance, wheel/tire compliance, bolt preload or chassis flexibility.",
            "Material is a simulation candidate input, not a finalized manufacturing selection.",
        ],
    }
    write_metadata(result_data)
    print(json.dumps(result_data["results"], indent=2))
