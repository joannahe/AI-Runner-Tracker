# Training Coach Agent contract

The connected Agent acts as a training coach for the authorized athlete. Its job is to review the athlete's saved goals and approved training plan, inspect new wearable observations through DOSI, apply the review rules in `coaching_knowledge.yaml`, and explain when a plan may need attention. The athlete remains the decision maker. This is a **product contract**, not an active scheduler or notification service in the current repository.

## Review cycle

| Moment | What the Agent reviews | Possible output |
| --- | --- | --- |
| After a successful wearable import | New local dates, data quality, duplicate activities and changed observations | Re-evaluate only affected dates and evidence windows; avoid a second alert for the same unchanged event. |
| After a verified road-race result | Official completion and course distance; upcoming dated plan actions | Review the athlete-configured easy/rest window and suggest a draft change if a high-intensity action falls inside it. Do not use watch distance as course distance. |
| Athlete-configured morning check | The latest available sleep, overnight HRV, resting HR and provider load ratio; today's approved workout, if any | Evidence-backed recovery review; a suggestion to reconsider today's key workout if a valid signal fires. Never presume the morning's data has arrived. |
| After each completed Monday–Sunday week | Two completed weeks of measured standalone running, training-focus labels, active goal criteria and next week's plan | Weekly mileage and high-focus session reviews, goal progress with evidence, and a plan-review summary. A partially imported week is not treated as complete. |
| When a new plan version is proposed or an approved plan is reviewed | Dated planned intensities, explicit easy/rest actions and any verified race recovery window | Check both `PostRaceRecoveryReview` and `HardEasySequenceReview` before presenting a plan as ready for athlete approval. |
| When the athlete asks a vague question or requests a plan review | Resolve the intended goal and period from saved context; inspect relevant ontology paths | Answer the question, disclose the chosen interpretation and limits, and suggest an approved-plan review when warranted. |

## Required coach checks for every relevant plan review

1. Select the authorized athlete, local timezone and exact `ActionPlan` version. Check both approved and proposed dated actions; never mix versions.
2. Look for a newly verified completed road race. Confirm official course distance and the athlete's effective `easy_or_rest_days_per_km` setting. Calculate the configured window, then inspect every uncompleted high-intensity action inside it. If either input is missing, return `insufficient_evidence` for `PostRaceRecoveryReview`.
3. Sort planned actions by local date. Identify adjacent high-intensity actions and verify whether an explicit easy run or rest day intervenes. If intensity is missing, or intervening dates are blank, return `unknown` for that interval rather than asserting a pass. Do not substitute completed COROS `training_focus` for planned intensity.
4. For each triggered rule, name the race or prior hard action, the affected future action, dates, configured policy and plan version. Check available biometric recovery data separately; do not treat a schedule rule as a diagnosis or as proof of readiness.
5. Offer a new draft plan version with an easy/rest or rescheduled action. Ask the athlete to approve it. Keep the approved version and wearable schedule untouched.

Run these checks after a verified race import, when proposing a plan, in an opted-in periodic review, and when an athlete asks vague questions such as “Is next week's plan sensible?” The current repository defines this behavior but does not schedule or execute it.

## Triggered event to reminder

1. Resolve `Athlete`, local timezone, active `Goal` version, `GoalCriterion`, approved `ActionPlan` version, dated `PlannedAction`, applicable athlete threshold override, and rule version.
2. Query mapped DOSI datasets and metrics. Check each rule's required dates, source, valid-day count, deduplication, comparability and import coverage. Preserve missing data as `insufficient_evidence`.
3. Evaluate the documented rules. `CompromisedRecovery` is a one-valid-signal review (RHR, personal HRV range or sleep score). `PossibleExerciseRelatedFatigueReview` needs two **distinct** signals among high load, seven-day sleep drop and seven-day RHR rise. The HRV signal does not silently become an extra composite vote. Weekly mileage and training-focus checks run only on completed weeks.
   Also inspect post-race recovery and hard/easy sequencing for the relevant athlete and plan version. If official race distance, athlete recovery setting, or structured planned intensity is absent, report the gap instead of claiming the plan passes.
4. If a rule fires, create an inspectable review event with observed value, personal baseline or provider range, threshold, source record/date, rule version and affected planned action. A provider recovery percentage is contextual and must not be counted as independent evidence from training load.
5. Send a plain-language reminder only if the athlete enabled reminders and the event is new or materially changed. Use a stable key of athlete, rule, period end, rule version and optional action ID to suppress duplicates. Do not send a trigger alert when evidence is insufficient.
6. If the event affects an uncompleted key workout, propose an easier option in a **new draft plan version**. State which action it would replace and why. The approved plan remains intact until the athlete accepts. No COROS or Garmin plan is edited automatically.
7. Record whether the athlete reviewed, dismissed or accepted a proposal when a future event log and notification channel exist. A dismissal is not evidence that the underlying measurement changed.

### Example reminder shape

> **Review today's planned workout** · Your morning resting HR is 6 bpm above its prior-seven-day average. The check used five valid baseline days and today's reading. You have a tempo run planned. Would you like to review an easy-run or rest-day draft? Your approved plan has not changed.

This is a **format example**, not a statement about the project owner's measurements. The Agent should show the actual date, value, baseline, source and threshold when an event is real. Avoid diagnostic language such as “you are overtrained.” If no structured workout subtype is available, omit the claim that a particular tempo or VO₂ Max session is affected and instead invite a general plan review.

### Race recovery and hard/easy review examples

| Dated evidence | Review result |
| --- | --- |
| Verified 10 km race, athlete-configured recovery window, high-intensity action inside that window | `PostRaceRecoveryReview`; propose an easy/rest draft, keeping the approved action unchanged. |
| Two high-intensity actions on consecutive days | `HardEasySequenceReview`; propose moving or easing the later action. |
| High intensity, then an explicit rest day, then high intensity | No hard/easy sequence flag from this rule. |
| High-intensity actions separated by dates with no recorded actions | Unknown intervening recovery; ask the athlete rather than declaring a pass. |
| Unverified race distance or missing structured planned intensity | Insufficient evidence; do not calculate a window or claim a high-intensity conflict. |

## Notification controls for onboarding

Ask whether the athlete wants proactive reviews, their timezone, preferred morning check time and reminder channel. Let them select daily, weekly or both; allow pause and frequency changes. Explain which wearable categories will be checked and that health data may appear in reminders. Show configurable thresholds and their effective dates. These settings are **not yet stored by the current schema** and must be implemented before a background coach is enabled.

## Implementation required before claiming this works automatically

- A deterministic evaluator that records dated `RecoveryState` and `RecoveryEvidence` for the athlete, with the effective rule version and baseline coverage. DOSI maps the data; it does not itself execute the rules.
- A reliable weekly coverage check and rule evaluator for mileage, training-focus share and goal criteria. Do not infer a complete week solely from the presence of some activities.
- Structured workout types and an imported or user-entered dated plan. Today's `PlannedAction.action_kind` is too generic to identify Tempo or VO₂ Max reliably.
- A verified road-race course-distance source, per-athlete recovery-window setting, structured planned intensity, and an evaluator for race windows and consecutive high-intensity actions. The optional one-day-per-mile example is not an active default. Empty calendar dates do not prove rest.
- A per-athlete override store and opt-in reminder preferences, plus a persistent review-event/notification log for deduplication and athlete responses.
- A scheduler and delivery channel that run under the selected athlete's authorization. The current project has neither. Until these exist, the Agent can perform an **on-demand review** and draft wording, but it must not promise periodic alerts.

See [question catalog and onboarding](QUESTION_CATALOG_AND_ONBOARDING.md), [recovery rules](RECOVERY_RULES.md), and the machine-readable `training_coach_workflow` in `coaching_knowledge.yaml`.
