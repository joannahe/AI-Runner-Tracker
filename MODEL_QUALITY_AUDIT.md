# Semantic model and ontology quality audit

This audit separates Apache Ossie schema validity from DOSI authoring advice. The pinned Ossie 0.2 schemas and DOSI 0.2.2 accept both standalone projects. The advice below does not represent query failures.

## First increment

The initial DOSI audit reported 86 `underdeclared_field` warnings in each dialect project: 40 key-like fields, 10 time-like fields, and 36 measurement-like fields. This increment marks `workout_event.started_at_local` and `running_observation.observation_date` as time dimensions. Both identify when a workout or running observation occurred. The saved coaching review adds three provenance or audit-field hints, making the current warning count 87 per project, with no validation issues or compile errors.

Do not suppress all warnings mechanically. The pinned Ossie `Field` schema does **not** define an `is_dimension` property, even though the DOSI authoring hint suggests `is_dimension: false`. Adding that property would fail the project's required schema check. In particular:

- `sport_code`, race format, and similar categorical fields may be useful dimensions.
- `source_snapshot_id`, candidate event IDs, and other provenance fields need a deliberate exposure decision. They are not automatically join keys.
- Audit timestamps should not be marked as business time dimensions merely to silence a warning.
- `time_quality` and `distance_basis` are categorical fields that the name heuristic flags as time-like or measurement-like.
- `weekly_running_distance.growth_ratio` is used by a queryable derived subtype; hiding or replacing it requires a regression query.

## Unmapped concept edges

DOSI initially reported 15 ontology edges without a link mapping. The race edge is now represented by a queryable subtype, and the saved coach review maps its two goal/plan links. Twelve conceptual or reverse edges remain:

| Group | Count | Current decision |
| --- | ---: | --- |
| Inference and generic recommendation concepts (`InferredState`, `Recommendation`) | 5 | Conceptual rule catalog; saved goal reviews and concrete proposals are separate mapped entities. |
| Recovery and provider context edges | 5 | Map only if a dated, explicit record key exists; the provider's private recovery formula is not a join. |
| Reverse arrows (`Goal.has_criterion`, `GoalProgressAssessment.supported_by`) | 2 | Query from the mapped child concept and its `belongs_to` or `supports` link. |
| `RaceEvent.completed_as` | 1 resolved | `RaceEvent` now extends `TrainingSession` and DOSI executes its race filter. |

The planned intensity field is already mapped. Post-race and hard/easy plan reviews still require their stated evidence and an external evaluator; the ontology does not schedule or approve changes.

## Next decisions

Review the remaining 87 field hints in small batches. For each field, decide whether it is a user-facing dimension, a real measure needing a semantic metric, a queryable evidence attribute, or internal provenance. Preserve Ossie schema compliance and existing metric/ontology queries after every change. For race coaching, select a known race-format distance or a canonical watch distance; report missing distance rather than inventing it. Intentionally conceptual edges do not need fabricated mappings.
