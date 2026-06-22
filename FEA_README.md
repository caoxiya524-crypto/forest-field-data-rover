# Wheel-leg Link Finite-Element Analysis

This folder contains a real local finite-element calculation using a 2D plane-stress, constant-strain triangular-element mesh. It is a local wheel-leg link verification model, rather than a full-vehicle finite-element model.

## Model

- Representative link: 180 × 25 × 8 mm.
- Material input: candidate 6061-series aluminum, E = 69 GPa, Poisson ratio = 0.33.
- Mesh: 840 CSTRI3 elements and 473 nodes.
- Constraint: chassis-side end fixed in x and y.
- Load: 150 N downward force distributed along the wheel-side interface.

Computed maxima: von Mises stress = 30.87 MPa; total displacement = 0.390 mm.

## Scope

This is a genuine finite-element solution under the stated assumptions. It does not yet include pin contact, bearing clearance, tire compliance, bolt preload, terrain-impact time histories, complete chassis compliance, or sensor payload mass. Those belong in the next full-assembly simulation stage.
