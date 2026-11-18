"""Translate source warehouse DDL comments for the English release package."""

import re


COMMENT_TRANSLATIONS = {
    "按原时区换算的活动日期": "Activity date in the source time zone",
    "UTC Unix毫秒": "UTC Unix timestamp in milliseconds",
    "平台统一分类，源sport_type仍保留": "Normalized sport category; original sport_type is retained",
    "源Workout Time，不等同FIT timer": "Source Workout Time; distinct from the FIT timer",
    "源Total Time/历时": "Source Total Time / elapsed duration",
    "源平均配速": "Source average pace",
    "官方成绩来源及口径，不能混入手表总用时": "Official result source and timing basis; keep separate from watch elapsed time",
    "逐字段证据：user_confirmed/poster/inferred及时间": "Field-level evidence: user_confirmed, poster, or inferred, with timestamp",
    "recorder/hr_sensor/power_sensor/footpod等": "Device role, such as recorder, hr_sensor, power_sensor, or footpod",
    "分析口径选定的一组，不同时累计不同group": "Canonical group selected for analysis; do not sum across groups",
    "平台内部不可变UUID，不用昵称/邮箱作主键": "Immutable platform UUID; do not use nickname or email as the primary key",
    "平台资料字段：female/male/other/unknown": "Platform profile value: female, male, other, or unknown",
    "height_cm/weight_kg/body_fat_pct/vo2max_ml_kg_min等": "Measurement type, such as height_cm, weight_kg, body_fat_pct, or vo2max_ml_kg_min",
    "实际测量时间；不能用抓取时间冒充": "Actual measurement time; do not substitute the fetch time",
    "用户/来源明确声明的生效时间，可为空": "Effective time explicitly stated by the user or source; may be null",
    "只有知道测量设备时才填": "Set only when the measurement device is known",
    "account_profile/manual/scale/lab等": "Measurement method, such as account_profile, manual, scale, or lab",
    "account_bound/owned/borrowed/shared等": "Device relationship: account_bound, owned, borrowed, or shared",
    "absolute_bpm/max_hr/lthr/hrr等": "Zone calculation method, such as absolute_bpm, max_hr, lthr, or hrr",
    "平台内部设备UUID": "Internal platform device UUID",
    "与pace_distance_m同口径的时间分子": "Time numerator using the same basis as pace_distance_m",
    "只纳入实测且口径匹配的距离": "Include only measured distance with a matching timing basis",
    "真实有效样本覆盖秒数；只有均值则NULL": "Seconds covered by valid samples; null when only a mean is available",
    "bilateral_steps_per_min/unknown等": "Cadence definition, such as bilateral_steps_per_min or unknown",
    "项目要求的距离/次数/负重/规则已核对才为true": "True only after required distance, repetitions, load, and rules are verified",
    "仅核实条件后生成；严格同条件比较的分组键": "Group key for strict like-for-like comparison; create only after conditions are verified",
    "一次真实运动；跨平台副本归到同一事件": "One real workout; cross-platform copies map to the same event",
    "running/hybrid_fitness/cycling等统一分类": "Normalized category, such as running, hybrid_fitness, or cycling",
    "是否被确认为正式赛事，不代表已有官方成绩": "Confirmed official race; does not imply an official result is available",
}


def translate_comments(ddl: str) -> str:
    def replace(match: re.Match) -> str:
        comment = match.group(1)
        if not re.search(r"[\u3400-\u9fff]", comment):
            return match.group(0)
        if comment not in COMMENT_TRANSLATIONS:
            raise ValueError(f"Untranslated StarRocks comment: {comment}")
        return f'COMMENT "{COMMENT_TRANSLATIONS[comment]}"'

    result = re.sub(r'COMMENT "([^"]*)"', replace, ddl)
    if re.search(r"[\u3400-\u9fff]", result):
        raise ValueError("Chinese text remains in StarRocks schema")
    return result
