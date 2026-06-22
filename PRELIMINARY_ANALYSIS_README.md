# Preliminary Structural Verification

These files show repeatable analytical screening calculations for the rover wheel-leg link. They are **not** SolidWorks Simulation or ANSYS finite-element results.

## Model

A 180 mm long, 25 x 8 mm rectangular candidate 6061-series aluminum link is treated as a cantilever beam. The calculation uses `sigma = M*c/I`, `delta = P*L^3/(3*E*I)`, and an Euler-Bernoulli first bending-mode estimate.

At the 150 N design case: stress = 101.2 MPa, tip deflection = 3.96 mm, screening safety factor = 2.73, and isolated-link first bending estimate = 201.6 Hz.

## Limits

A detailed design decision requires material certificates, measured terrain loads, joint contact/clearance, wheel and payload mass, and full-assembly finite-element/modal analysis.
