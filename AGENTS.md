# AGENTS.md

This repository is organized as a small scientific software project rather than a notebook dump.

Conventions:
- Keep public logic in `src/hhl_lab/` with type hints and concise doctrings.
- Preserve the default HHL problem instance unless a change is explicitly intentional:
  - `A = [[1, -1/3], [-1/3, 1]]`
  - `b = [1, 0]`
  - `t = 3*pi/4`
- Prefer pure functions for linear algebra and circuit construction.
- Keep the notebook educational and thin; reusable logic belongs in the package.
- Add comments only when they clarify mathematics or qubit ordering.
- Regenerate figures through `scripts/generate_figures.py`.
- Run `python -m pytest` after nontrivial changes.
