# MNEMOS Experimentation

`experiments/protocols/mnemos_ablation.yaml` is the authoritative initial
protocol. It defines matched-seed, four-configuration comparisons and the
environment changes needed to test stale-memory rejection rather than merely
show repeated-route performance.

The `mnemos_evaluation` package stores one row per trial. It intentionally
keeps failures and collision events in the denominator; use `summary()` only
after recording every planned attempt and preserve ROS bags alongside the
SQLite ledger. No result data ships with the repository, so this project makes
no performance claim at this stage.
