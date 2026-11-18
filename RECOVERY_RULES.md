# Recovery mapping and review rules

These are **user-configured review signals** for the fictional public fitness demo, not medical diagnoses or universal exercise thresholds. The structured, agent-facing version is in `fitness_ontology.yaml` under `recovery_rules`. The DOSI ontology maps the source observations; it does not execute the rules automatically.

The ontology contains a mapped `RecoveryRule` concept backed by `fitness_demo.recovery_rule`. Its rows are queryable from DOSI and carry bounds, labels, meanings, baseline requirements, and a `rule_origin` of `coros` or `user_configured`. A saved `RecoveryState` row links to the dated load, sleep, resting-HR and separate provider-recovery observations; `RecoveryEvidence` rows cite the source record and rule used in that review. These joins do **not** assert that sleep or resting HR enter COROS's own formula.

The fictional fixture saves three daily reviews and 13 evidence rows. All three reviews are `insufficient_evidence`: the fixture contains fewer than five prior valid days for seven-day comparisons and fewer than 28 for the 42-day sleep comparison. Provider bands can still be shown as source labels; they do not override the composite review. DOSI reads the saved assessment and evidence. A production evaluator must calculate new reviews from new source data, preserve the method version, and avoid overwriting earlier assessments.

| Recovery input | Ontology concept | Semantic dataset and field | Existing semantic metric |
| --- | --- | --- | --- |
| Short-term load | `DailyTrainingLoad` | `daily_training_load.short_term_load` | `avg_short_term_load` |
| Long-term load | `DailyTrainingLoad` | `daily_training_load.long_term_load` | `avg_long_term_load` |
| Provider load ratio | `DailyTrainingLoad` | `daily_training_load.load_ratio` | `avg_load_ratio` |
| Main sleep duration | `SleepObservation` | `daily_sleep.main_sleep_min`, keyed by wake date | `avg_main_sleep_minutes` |
| Resting heart rate | `RestingHeartRate` | `daily_resting_hr.rhr_bpm`, keyed by local date | `avg_resting_hr_bpm` |
| COROS recovery estimate | `ProviderRecoveryEstimate` | `recovery_observation.recovery_pct`, with observation time | `current_recovery_pct` |
| Interpretation range | `RecoveryRule` | `recovery_rule.metric_code`, bounds, label, origin | Rule facts; no automatic classifier metric |

`RecoveryState` combines these inputs as a review concept. Sleep and resting heart rate are **independent context**; they are not asserted to be inputs to the COROS recovery percentage. The provider ratio is stored as supplied, rather than being recalculated as a generic ACWR.

## Configurable high-load review

`fitness_ontology.yaml` defines the agent-facing default `coros_load_ratio_high: 1.5`. A dated COROS `daily_training_load.load_ratio` **strictly greater** than the applicable threshold produces the conceptual `OvertrainingRisk` review flag and a `ScaleBackVolume` suggestion for the runner to consider. At exactly 1.5, the COROS provider band is “excessive” while this separate user-configured flag does not fire. The flag name is not an overtraining diagnosis. Cite the athlete, observation date, provider value, configured threshold and rule version. A per-athlete override can replace the default in the rule configuration; the current ontology does not persist overrides or execute the rule. No plan is changed without the runner's approval.

## Biometric recovery review and draft workout change

`CompromisedRecovery` is an **Agent review flag** in `fitness_ontology.yaml`, not a DOSI-executed classifier or a diagnosis. Each signal is evaluated for the athlete and the local day of a planned workout:

- **Resting HR:** today's valid `daily_resting_hr.rhr_bpm` is strictly more than **5 bpm above** the mean of at least five valid observations in the preceding seven local days. The 5 bpm default is user-configurable and is not a COROS medical threshold.
- **Overnight HRV:** the COROS official daily overnight HRV estimate is **below the lower bound of that athlete's COROS normal range**. COROS builds this personal range from previous nights, initially after five nights. Do not compare against a population HRV cutoff or treat a missing range as low HRV. The COROS MCP returns the official assessment. It is mapped to `daily_hrv` and the `OvernightHRV` concept; the local importer saves daily assessments without raw sample points.
- **Sleep quality:** today's valid `daily_sleep.sleep_score` is strictly below **90% of the mean of the preceding 42 valid wake dates**. Require at least 28 valid prior scores. The 10% drop is a user-configurable project default; it is a comparison with personal sleep score, not with sleep duration.

One valid triggered signal is enough to request a review; missing or insufficient-baseline signals are reported separately. Cite the source value, baseline or provider lower bound, observation date, coverage, and rule version. This differs from `PossibleExerciseRelatedFatigueReview`, which requires two distinct signals. COROS's own Recovery percentage does not include sleep or HRV, so this review must be labelled separately. [COROS Overnight HRV](https://support.coros.com/hc/en-us/articles/20959044334612-Overnight-HRV), [COROS Sleep Score](https://support.coros.com/hc/en-us/articles/51716381180948-Understand-Your-COROS-Sleep-Score), [COROS Recovery Widget](https://support.coros.com/hc/en-us/articles/15406707571732-Understanding-the-Recovery-Widget).

If an uncompleted **Tempo or VO₂ Max** workout is scheduled for that local day, the intended action is to **generate a new draft ActionPlan version** proposing Active Recovery or Rest and notify the athlete. The approved plan and any COROS schedule stay unchanged until the athlete confirms. This is currently a documented workflow only: `PlannedAction.action_kind` does not encode those workout subtypes, and no evaluator, draft generator, or notifier is installed. A versioned rule-override store remains to be built.

## Weekly running-distance review

The separate `training_progression_rules` catalog uses `running_observation` and the existing `measured_run_distance_km` definition. Compare **two completed, consecutive Monday–Sunday weeks** for the same athlete, counting measured standalone running only. If the later week's distance is strictly greater than the previous week's distance × 1.10, emit `WeeklyMileageIncreaseReview` and suggest reviewing or scaling back the proposed increase. Require a positive previous-week distance and verified import coverage for both weeks; otherwise report insufficient evidence. The 10% value is configurable per athlete. This is a planning heuristic, not a medical threshold or a prediction of injury. A randomized trial did not find injury reduction from a 10% weekly progression program, and a later cohort associated abrupt *single-run* increases with injury while finding no association for week-to-week distance ratio. [Buist et al. (2008)](https://research.rug.nl/files/2727628/Buist_2008_Am_J_Sports_Med.pdf), [Brandt Frandsen et al. (2025)](https://www.klokeavskade.no/globalassets/publications/brandt-frandsen_2025_how-much-running-is-too-much.....pdf).

COROS's running recovery percentage bands are **0–19 exhausted, 20–69 fatigued, 70–89 normal, 90–100 fresh**. The provider load-ratio bands in the rule table are **0–<0.5 decreasing, 0.5–<0.8 resuming/performance, 0.8–<1.0 maintaining, 1.0–<1.5 optimized, ≥1.5 excessive**. Each band is a separate sourced rule row. The user-defined `>1.5` and `<0.8` review signals are additional rows and may overlap provider bands; `rule_kind` distinguishes them. [COROS fitness metrics](https://support.coros.com/hc/en-us/articles/360061452651-COROS-Fitness-Metrics-Explained), [COROS EvoLab](https://support.coros.com/hc/en-us/articles/26485283220884-EvoLab).

## Rules

All averages are per athlete and source. Compare daily sleep by local **wake date**, and resting heart rate or load by local date. The current observation is excluded from its historical baseline. A proposed minimum is five valid prior days for a seven-day baseline and 28 valid prior days for a 42-day baseline. These coverage requirements are configurable; otherwise return `insufficient_evidence`.

| Signal | Proposed comparison | Meaning |
| --- | --- | --- |
| High recent load | Provider ratio **> 1.5** | Review recent exercise stress and recovery before the next session. |
| Low recent load | Provider ratio **< 0.8** | Review whether lower load fits the goal, rest period, or taper. Do not label all values below 0.8 ineffective training. |
| Sleep-duration outlier | Latest main sleep duration **> 110% or < 90%** of the mean of prior valid 42 wake-days | Duration changed substantially. This alone does **not** establish poor sleep quality. |
| Recent sleep drop | Latest main sleep duration **< 90%** of the mean of prior valid seven wake-days | A short-term sleep-loss signal for fatigue review. |
| Resting-HR rise | Latest resting HR **> 110%** of the mean of prior valid seven local days | A possible fatigue-related signal requiring context. |
| Week-to-week resting-HR change | Current valid seven-day mean differs by **> 10%** from previous valid seven-day mean | Review a change; only an increase contributes to the fatigue signal. |

`PossibleExerciseRelatedFatigueReview` requires **at least two distinct available signals** among high recent load, recent sleep drop, and resting-HR rise. Do not double-count COROS recovery as independent of load: its provider calculation already uses training load. Present the values, baseline dates, missingness, and source before suggesting that a person review the plan. No automatic fatigue score or plan change is produced.

The 42-day sleep rule and seven-day sleep rule answer different questions: deviation from a longer personal pattern versus a recent downward change. The 10% sleep and resting-HR thresholds are proposed project rules supplied by the user, not provider-certified cutoffs. Longer sleep may reflect recovery, schedule changes, or other causes. Resting-HR changes may have causes unrelated to training.

COROS describes intensity trend above roughly 150% as excessive and 50–79% as a possible performance/taper range. This is why a ratio below 0.8 triggers a *context review*, not the conclusion that fitness cannot improve. [COROS EvoLab](https://support.coros.com/hc/en-us/articles/26485283220884-EvoLab), [COROS Recovery Widget](https://support.coros.com/hc/en-us/articles/15406707571732-Understanding-the-Recovery-Widget).
