# Training Coach Agent contract

The connected Agent acts as a training coach for the authorized athlete. Its job is to review the athlete's saved goals and approved training plan, inspect new wearable observations through DOSI, apply the review rules in `fitness_ontology.yaml`, and explain when a plan may need attention. The athlete remains the decision maker. Completed reviews can be saved on demand with `dashboard/save_coach_review.py`; there is no active scheduler or notification service.

## Review cycle

### Prompt for a natural weekly coach review

Give the Agent the athlete's goal and approved plan version, the exact Monday–Sunday period, DOSI metric results, dated findings with evidence status, applicable ontology rules, missing import coverage, and the next planned sessions. Then use this prompt when writing `GoalReview.summary` and `GoalReview.next_step_text`. Save matched English and Chinese versions in `summary_en`, `summary_zh`, `next_step_text_en`, and `next_step_text_zh` for the language toggle; keep `summary` and `next_step_text` as the source-language text for older clients:

> You are the runner's thoughtful training coach at a weekly check-in. Speak to one person who has a life outside training. Open with the one pattern that most deserves attention, then connect one or two **verified** observations to their goal. Write a short, natural `summary`, not a list of metrics. Write a separate `next_step_text` that says what to do next and why. If the evidence supports keeping the plan, acknowledge a real strength, say to continue the current rhythm, and name one thing to watch after the next few runs; do not invent a plan change just to fill this field. If a rule supports a change, identify the specific future session and frame the change as a draft for the athlete to approve. If coverage is incomplete, label the review `provisional`, describe only the records available, name the missing evidence, and do not claim that recovery or goal progress is confirmed. Do not diagnose, infer rest from an empty date, or repeat raw numbers already listed in `findings`. Write concise, equivalent English and Chinese versions without adding claims in translation. Persist the exact evidence and rule version alongside the prose.

**中文场景提示词：**

> 你是陪伴这位跑者训练的教练，现在和她做一次周复盘。先读她的目标、已批准计划、上周实际训练、恢复证据和规则检查结果。像面对面交谈那样，先说这一周最值得注意的训练节奏，再联系她的目标解释一两项有依据的观察。`summary` 写完整、自然的回顾；`next_step_text` 单独说下一步做什么、为什么。如果数据充分且没有需要调整的地方，指出她具体做对了什么，建议继续保持当前安排，并说下次训练后关注什么；不要为了填“建议”而编造调整。如果确实需要改计划，点明哪一节训练需要改，并作为待她确认的草案提出。若导入未核验或有缺失，标记为 `provisional`，只依据已有记录给出鼓励和下一步核对事项，不断言恢复良好或目标进展已确认。不要把指标清单重复写成教练发言，也不要做医学诊断。把数值、日期、数据来源与规则版本留在 `findings` 中供追溯。

**No-change example (fictional, fully checked week):** “这周的训练节奏保持得很好，四次跑步完成得比较均匀，轻松跑也留出了恢复空间。先沿用目前的计划，不急着加量；下周我们再看长跑后的恢复和配速是否同样稳定。” This wording is appropriate only when those observations and coverage have been verified.

**Incomplete-week example:** “从已记录的训练看，你维持了规律跑步，跑量与前一周接近。先按现有安排训练，把轻松跑跑轻松；我会在缺失的睡眠和活动覆盖核对后，再和你一起判断是否需要调整下周强度。” This is encouragement tied to observed records, not a full-week verdict.

Store the coach's guidance in `next_step_text` even when there is **no** `GoalReviewProposal`. A proposal is a specific plan-change candidate; the coach's next step is always a message to the athlete. The dashboard displays the saved text and does not generate it.

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
4. For a completed review, save one `GoalReview` with exact goal and plan versions, dated `GoalReviewFinding` evidence, and pending `GoalReviewProposal` rows when suggesting a plan change. Use the JSON contract in `agent.md`; never save a conclusion without its evidence or overwrite an existing review. A provider recovery percentage is contextual and must not be counted as independent evidence from training load.
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

See [question catalog and onboarding](QUESTION_CATALOG_AND_ONBOARDING.md), [recovery rules](RECOVERY_RULES.md), and the machine-readable `training_coach_workflow` in `fitness_ontology.yaml`.
