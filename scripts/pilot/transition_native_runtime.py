"""Plan or commit the proof-only runtime transition for incomplete native Goal pairs.

The default command prints a read-only JSON plan. To apply, supply that saved
plan, its SHA-256, the status SHA-256 and the clearance used in planning.
Clearance uses the wall-budget transition schema, replacing the target budget
revision field with target_runtime_scope_revision and target_runtime_config_sha256.
Each interrupted attempt needs its own entry binding the review, archive and
current storage preflight. A commit requeues a matching fresh off/on pair.
"""

from transition_native_wall_budget import main


if __name__ == '__main__':
    main(runtime=True, description=__doc__)
