# plan.toml schema — reference

Strict parsing: unknown keys anywhere are errors (`deny_unknown_fields`).
All paths resolve against the plan file's directory at parse time.

## [meta]
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | string | yes | run name |
| repo | string | no | git repo path; required by red_first / protected_paths / test_list_cmd / model rungs / parallel execution. Must exist and contain `.git`. |

## [[unit]]
| Field | Type | Default | Notes |
|-------|------|---------|-------|
| name | string | — | unique; `::` forbidden (reserved for `<unit>::integration` labels) |
| role | string | "executor" | journal/cost label |
| adapter | string | — | `claude` or `codex` |
| model | string | adapter default | per-unit model tier (P3) |
| prompt_file | path | — | must exist at parse time; read fail-closed at run time |
| permission | string | "accept-edits" | `accept-edits` \| `unrestricted` \| `read-only` |
| controlled | bool | true | `false` tags harvested surprises `[uncontrolled]` (P11) |
| depends_on | [string] | [] | DAG; cycles rejected; `tests_from` implies a dependency |

## [unit.verify]
| Field | Type | Default | Notes |
|-------|------|---------|-------|
| oracle | [string] | [] | rung 1 commands |
| property | [string] | [] | rung 2 commands |
| property_runs | int | 1 | repetitions, all must pass |
| held_out | [string] | [] | rung 3 hidden commands; requires non-empty oracle; leak-checked against the exact spawned prompt |
| hacking_gap_threshold | float | 0.3 | rung 3; finite, [0,1] |
| adversarial | bool | false | rung 4 |
| judge | bool | false | rung 5 |
| judge_gap_threshold | float | 0.3 | rung 5; finite, [0,1] |
| peer_review | bool | false | rung 6 |
| red_first | bool | false | requires `tests_from` + `red_first_cmds` + `protected_paths` + repo |
| red_first_cmds | [string] | [] | the calibration instruments (only these are red-checked) |
| tests_from | string | — | predecessor unit authoring the tests |
| protected_paths | [string] | [] | opt-in per unit (extends defaults, any-depth). INV-4 protects evidence from the CONSUMER (implementer), never from its author — test-author units declare none |
| test_list_cmd | string | "" (opt-in) | test-name preservation baseline |

## Cross-unit rules
- Model rungs need two adapter families configured and `repo` set.
- Same-depth units (repo set): one shared adapter family per level (the other
  family arbitrates) and ≥1 deterministic rung each (integration re-verify).
- Runs refuse to start on a dirty repo (`DirtyRepo`) or a locked run dir
  (`RunLocked`); resume requires the identical plan text (`PlanChanged`).
