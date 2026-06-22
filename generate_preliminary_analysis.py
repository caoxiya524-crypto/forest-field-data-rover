"""Generate transparent, repeatable preliminary structural checks for the rover.

This is an analytical screening study, not a finite-element analysis. It uses a
single wheel-leg link as a cantilever beam and intentionally writes all inputs,
formulae, and limitations alongside the plots.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "simulations"
OUT.mkdir(exist_ok=True)

# Preliminary design assumptions for a single wheel-leg link.
E_PA = 69e9  # Pa, nominal elastic modulus for a 6061-series aluminum candidate.
YIELD_PA = 276e6  # Pa, candidate yield value used only for the screening estimate.
RHO = 2700.0  # kg/m^3
L_M = 0.180  # effective unsupported link length, m
B_M = 0.025  # link width, m
T_M = 0.008  # link thickness along bending axis, m
DESIGN_LOAD_N = 150.0  # one-link design load for obstacle traversal, N
LOAD_CASES_N = np.array([90.0, 120.0, 150.0])
LOAD_CASE_NAMES = ["Nominal traverse", "Uneven terrain", "Obstacle contact"]

AREA = B_M * T_M
I_M4 = B_M * T_M**3 / 12.0
C_M = T_M / 2.0


def stress_mpa(load_n: np.ndarray | float) -> np.ndarray | float:
    return np.asarray(load_n) * L_M * C_M / I_M4 / 1e6


def deflection_mm(load_n: np.ndarray | float) -> np.ndarray | float:
    return np.asarray(load_n) * L_M**3 / (3.0 * E_PA * I_M4) * 1e3


SIGMA_MPA = float(stress_mpa(DESIGN_LOAD_N))
DEFLECTION_MM = float(deflection_mm(DESIGN_LOAD_N))
SAFETY_FACTOR = YIELD_PA / (SIGMA_MPA * 1e6)

# Euler-Bernoulli cantilever first bending frequency for the isolated link only.
BETA_1 = 1.87510407
F1_HZ = (BETA_1**2 / (2.0 * np.pi * L_M**2)) * np.sqrt(E_PA * I_M4 / (RHO * AREA))


def style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.edgecolor": "#2E3436",
            "axes.labelcolor": "#2E3436",
            "xtick.color": "#2E3436",
            "ytick.color": "#2E3436",
            "text.color": "#1E2528",
            "axes.titleweight": "bold",
            "figure.facecolor": "#F7F8F7",
            "axes.facecolor": "#FFFFFF",
        }
    )


def add_badge(ax: plt.Axes, text: str) -> None:
    ax.text(
        0.02,
        0.95,
        text,
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=9,
        color="#3D4B4D",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "#E8EFEC", "edgecolor": "#A9BBB1"},
    )


def save_static_link_check() -> None:
    style()
    fig, (ax_link, ax_curve) = plt.subplots(1, 2, figsize=(13.5, 5.6), gridspec_kw={"width_ratios": [1.12, 1]})
    fig.suptitle("Wheel-leg link preliminary static check", x=0.05, ha="left", fontsize=17, fontweight="bold")
    fig.text(0.05, 0.90, "Analytical cantilever model; screening only, not a finite-element result.", fontsize=10, color="#596467")

    x_segments = np.linspace(0.0, L_M, 80)
    sigma_segments = stress_mpa(DESIGN_LOAD_N) * (1.0 - x_segments / L_M)
    cmap = plt.get_cmap("YlOrRd")
    norm = plt.Normalize(vmin=0, vmax=SIGMA_MPA)
    for x0, x1, sigma in zip(x_segments[:-1], x_segments[1:], sigma_segments[:-1]):
        ax_link.add_patch(Rectangle((x0, -T_M / 2), x1 - x0, T_M, color=cmap(norm(sigma)), ec="none"))
    ax_link.add_patch(Rectangle((-0.010, -0.032), 0.010, 0.064, color="#4B5659", ec="#202628", lw=1.4))
    ax_link.plot([0, L_M], [-T_M / 2, -T_M / 2], color="#202628", lw=1.3)
    ax_link.plot([0, L_M], [T_M / 2, T_M / 2], color="#202628", lw=1.3)
    ax_link.add_patch(FancyArrowPatch((L_M, 0.048), (L_M, 0.007), arrowstyle="-|>", mutation_scale=17, color="#D95F02", lw=2.2))
    ax_link.text(L_M - 0.004, 0.052, "150 N", ha="right", va="bottom", color="#B94700", fontweight="bold")
    ax_link.annotate("fixed joint", xy=(0.002, 0), xytext=(0.020, -0.050), arrowprops={"arrowstyle": "-", "color": "#566064"}, fontsize=9)
    ax_link.annotate("L = 180 mm", xy=(L_M / 2, -0.010), xytext=(L_M / 2, -0.055), ha="center", arrowprops={"arrowstyle": "-", "color": "#566064"}, fontsize=9)
    ax_link.text(0.002, 0.064, "25 x 8 mm 6061-series link", fontsize=9, color="#3D4B4D")
    ax_link.set_xlim(-0.025, 0.205)
    ax_link.set_ylim(-0.075, 0.080)
    ax_link.set_aspect("equal")
    ax_link.axis("off")
    add_badge(ax_link, "Peak stress occurs at the fixed end")

    loads = np.linspace(0, 180, 100)
    ax_curve.plot(loads, stress_mpa(loads), color="#1B8A5A", lw=2.8, label="Bending stress")
    ax_curve.set_xlabel("Applied link load (N)")
    ax_curve.set_ylabel("Bending stress (MPa)", color="#1B8A5A")
    ax_curve.grid(axis="y", color="#D9DFDD", lw=0.8)
    ax_curve.axhline(YIELD_PA / 1e6, color="#B2473D", lw=1.5, ls="--", label="Candidate yield reference")
    ax_curve.axvline(DESIGN_LOAD_N, color="#D95F02", lw=1.4, ls=":")
    ax_curve.scatter([DESIGN_LOAD_N], [SIGMA_MPA], s=55, color="#D95F02", zorder=5)
    ax_curve.text(DESIGN_LOAD_N + 4, SIGMA_MPA + 6, f"{SIGMA_MPA:.1f} MPa\nSF = {SAFETY_FACTOR:.2f}", fontsize=10, fontweight="bold")
    ax_defl = ax_curve.twinx()
    ax_defl.plot(loads, deflection_mm(loads), color="#4F7D9A", lw=2.2, label="Tip deflection")
    ax_defl.set_ylabel("Tip deflection (mm)", color="#4F7D9A")
    ax_defl.scatter([DESIGN_LOAD_N], [DEFLECTION_MM], s=42, color="#4F7D9A", zorder=5)
    handles, labels = ax_curve.get_legend_handles_labels()
    handles2, labels2 = ax_defl.get_legend_handles_labels()
    ax_curve.legend(handles + handles2, labels + labels2, loc="upper left", frameon=False)
    add_badge(ax_curve, f"Design point: {DESIGN_LOAD_N:.0f} N / {DEFLECTION_MM:.2f} mm")

    fig.subplots_adjust(left=0.06, right=0.94, bottom=0.14, top=0.84, wspace=0.34)
    fig.savefig(OUT / "static_link_check.png", dpi=220)
    plt.close(fig)


def save_load_cases() -> None:
    style()
    fig, ax1 = plt.subplots(figsize=(11.5, 5.7))
    fig.suptitle("Preliminary terrain-load cases for one wheel-leg link", x=0.08, ha="left", fontsize=17, fontweight="bold")
    fig.text(0.08, 0.90, "Input loads are design assumptions for comparative screening; they are not measured field loads.", fontsize=10, color="#596467")
    x = np.arange(len(LOAD_CASES_N))
    width = 0.32
    stress_values = stress_mpa(LOAD_CASES_N)
    deflection_values = deflection_mm(LOAD_CASES_N)
    bars = ax1.bar(x - width / 2, stress_values, width, color=["#4A8F73", "#D99A3D", "#C65A4A"], label="Bending stress")
    ax1.set_ylabel("Bending stress (MPa)")
    ax1.set_xticks(x, LOAD_CASE_NAMES)
    ax1.grid(axis="y", color="#D9DFDD", lw=0.8)
    for bar, value in zip(bars, stress_values):
        ax1.text(bar.get_x() + bar.get_width() / 2, value + 3, f"{value:.1f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax2 = ax1.twinx()
    ax2.plot(x + width / 2, deflection_values, color="#3E6B88", marker="o", lw=2.6, ms=7, label="Tip deflection")
    ax2.set_ylabel("Tip deflection (mm)", color="#3E6B88")
    for x0, value in zip(x + width / 2, deflection_values):
        ax2.text(x0, value + 0.13, f"{value:.2f}", ha="center", va="bottom", color="#31566F", fontsize=10, fontweight="bold")
    ax1.axhline(YIELD_PA / 1e6, color="#B2473D", lw=1.5, ls="--")
    ax1.text(2.38, YIELD_PA / 1e6 + 7, "candidate yield reference", ha="right", color="#9A3A32", fontsize=9)
    ax1.set_ylim(0, 310)
    ax2.set_ylim(0, max(deflection_values) * 1.45)
    handles, labels = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles + handles2, labels + labels2, loc="upper left", frameon=False)
    add_badge(ax1, "Single-link analytical comparison")
    fig.subplots_adjust(left=0.10, right=0.90, bottom=0.18, top=0.82)
    fig.savefig(OUT / "terrain_load_cases.png", dpi=220)
    plt.close(fig)


def save_modal_estimate() -> None:
    style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.4), gridspec_kw={"width_ratios": [1.1, 0.9]})
    fig.suptitle("Wheel-leg link first bending frequency estimate", x=0.06, ha="left", fontsize=17, fontweight="bold")
    fig.text(0.06, 0.90, "Euler-Bernoulli cantilever estimate for the isolated link; joint, wheel and chassis masses are excluded.", fontsize=10, color="#596467")
    xi = np.linspace(0, 1, 300)
    beta = BETA_1
    alpha = (np.cosh(beta) + np.cos(beta)) / (np.sinh(beta) + np.sin(beta))
    phi = np.cosh(beta * xi) - np.cos(beta * xi) - alpha * (np.sinh(beta * xi) - np.sin(beta * xi))
    phi = phi / np.max(np.abs(phi))
    x_mm = xi * L_M * 1000
    ax1.plot(x_mm, np.zeros_like(x_mm), color="#596467", lw=1.5, ls="--", label="Undeformed link")
    ax1.plot(x_mm, phi * 16, color="#D95F02", lw=3.0, label="First bending shape (scaled)")
    ax1.fill_between(x_mm, 0, phi * 16, where=phi >= 0, color="#F2C17D", alpha=0.45)
    ax1.add_patch(Rectangle((-8, -23), 8, 46, color="#4B5659", ec="#202628", lw=1.3))
    ax1.set_xlabel("Link length from fixed joint (mm)")
    ax1.set_ylabel("Relative deformation (display scale)")
    ax1.set_ylim(-25, 25)
    ax1.grid(axis="x", color="#D9DFDD", lw=0.8)
    ax1.legend(loc="upper left", frameon=False)
    add_badge(ax1, f"Estimated isolated-link f1 = {F1_HZ:.0f} Hz")

    ax2.axis("off")
    rows = [
        ("Material candidate", "6061-series aluminum"),
        ("Elastic modulus", "69 GPa"),
        ("Density", "2700 kg/m³"),
        ("Link section", "25 x 8 mm"),
        ("Effective length", "180 mm"),
        ("Estimated f1", f"{F1_HZ:.1f} Hz"),
    ]
    y = 0.83
    for label, value in rows:
        ax2.text(0.05, y, label, fontsize=11, color="#4D585B")
        ax2.text(0.56, y, value, fontsize=11, fontweight="bold", color="#1F3439")
        ax2.plot([0.05, 0.93], [y - 0.05, y - 0.05], color="#D7DEDA", lw=1)
        y -= 0.12
    ax2.text(0.05, 0.06, "Interpretation: this is a component-level estimate only.\nA complete modal study must include joints, wheels, chassis and payload mass.", fontsize=9.5, color="#596467", va="bottom")
    fig.subplots_adjust(left=0.06, right=0.95, bottom=0.14, top=0.82, wspace=0.20)
    fig.savefig(OUT / "modal_frequency_estimate.png", dpi=220)
    plt.close(fig)


def write_results() -> None:
    results = {
        "analysis_type": "preliminary analytical screening; not finite element analysis",
        "model": "single wheel-leg link as a cantilever beam",
        "assumptions": {
            "material_candidate": "6061-series aluminum",
            "elastic_modulus_pa": E_PA,
            "yield_reference_pa": YIELD_PA,
            "density_kg_m3": RHO,
            "effective_length_m": L_M,
            "section_width_m": B_M,
            "section_thickness_m": T_M,
            "design_load_n": DESIGN_LOAD_N,
        },
        "results": {
            "second_moment_m4": I_M4,
            "design_stress_mpa": SIGMA_MPA,
            "design_tip_deflection_mm": DEFLECTION_MM,
            "screening_safety_factor": SAFETY_FACTOR,
            "isolated_link_first_bending_frequency_hz": F1_HZ,
        },
        "limitations": [
            "No contact, joint clearance, bolt preload, tire compliance or chassis flexibility is modeled.",
            "The assumed terrain loads are for comparison only and require test or detailed FEA validation.",
            "The modal estimate excludes wheel, motor, sensor payload and joint compliance.",
        ],
    }
    (OUT / "preliminary_analysis_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "README.md").write_text(
        "# Preliminary structural verification\n\n"
        "These figures are repeatable analytical screening calculations for the rover wheel-leg link. "
        "They are **not** ANSYS or SolidWorks Simulation finite-element results.\n\n"
        "## Model\n\n"
        "A 180 mm long, 25 x 8 mm rectangular candidate 6061-series aluminum link is treated as a cantilever. "
        "The calculation uses `sigma = M*c/I`, `delta = P*L^3/(3*E*I)`, and the first cantilever bending-mode equation.\n\n"
        f"At the 150 N design case, the calculation gives {SIGMA_MPA:.1f} MPa stress, {DEFLECTION_MM:.2f} mm tip deflection, "
        f"and a screening safety factor of {SAFETY_FACTOR:.2f}. The isolated-link first bending estimate is {F1_HZ:.1f} Hz.\n\n"
        "## Limits\n\n"
        "These results are for portfolio-level method demonstration. A detailed design decision requires material certificates, "
        "real load spectra, joint contact/clearance, wheel and payload mass, and a full assembly finite-element/modal analysis.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    save_static_link_check()
    save_load_cases()
    save_modal_estimate()
    write_results()
    print(f"Generated preliminary analysis files in {OUT}")
