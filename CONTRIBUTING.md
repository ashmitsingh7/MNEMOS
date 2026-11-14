# Contributing to MNEMOS

MNEMOS is a research platform. Contributions should preserve its safety
and reproducibility invariants.

## Principles
- Never let memory override current perception or collision checks.
- Memory influence must be bounded and attributable to an episode.
- On uncertainty, abstain.
- Preserve raw data and failed trials; never manufacture results.
- Do not claim an improvement without experimental evidence.

## Workflow
1. Fork and create a feature branch.
2. Keep changes focused and documented.
3. Add or update tests for pure-Python core changes.
4. Run `python3 -m unittest discover -s tests -v`.
5. Build with `colcon build --symlink-install` when touching ROS packages.
6. Open a pull request with a clear description and rationale.

## Code style
- Pure-Python core must remain ROS-free and independently testable.
- Prefer explainable, inspectable logic over opaque learned models.
- Add docstrings and type hints to new functions.

## Reporting issues
Use the `report` skill workflow or open a GitHub issue with reproduction steps,
environment details, and logs.
