from dataclasses import dataclass, asdict


@dataclass
class CoachResult:
    readiness_score: float
    projected_score: float
    status: str
    pass_probability: float
    support_needed: str
    weak_areas: list[str]
    teaching_actions: list[str]
    scenario_note: str


def clamp(value: float, low=0.0, high=100.0) -> float:
    return max(low, min(high, float(value)))


def evaluate(metrics: dict) -> CoachResult:
    previous_sem = clamp(metrics["previous_semester_average"])
    year = metrics.get("year")
    year = int(year) if year is not None else 1
    
    historical_factors = [(previous_sem, 2.0)]
    if year > 1 and metrics.get("year1_average") is not None:
        historical_factors.append((clamp(metrics["year1_average"]), 1.0))
    if year > 2 and metrics.get("year2_average") is not None:
        historical_factors.append((clamp(metrics["year2_average"]), 1.5))
    if year > 3 and metrics.get("year3_average") is not None:
        historical_factors.append((clamp(metrics["year3_average"]), 1.5))
        
    total_w = sum(w for _, w in historical_factors)
    weighted_history = sum(v * w for v, w in historical_factors) / total_w if total_w else previous_sem

    i1 = clamp(metrics["current_internal_1"])
    i2 = clamp(metrics["current_internal_2"])
    assignment = clamp(metrics["assignment_score"])
    lab = clamp(metrics["lab_score"])
    attendance = clamp(metrics["attendance_pct"])
    backlogs = int(metrics["backlogs"])
    threshold = clamp(metrics.get("pass_threshold", 40))

    current_average = (i1 + i2 + assignment + lab) / 4.0
    projected = 0.50 * current_average + 0.30 * weighted_history + 0.20 * attendance
    projected = clamp(projected)
    readiness = clamp(0.65 * projected + 0.35 * current_average)

    weak = []
    actions = []
    if attendance < 75:
        weak.append("Attendance")
        actions.append("Create an attendance recovery plan and prioritize the next consecutive classes.")
    if i1 < threshold:
        weak.append("Internal 1")
        actions.append("Run a short topic-gap revision and a targeted 20-question practice set.")
    if i2 < threshold:
        weak.append("Internal 2")
        actions.append("Re-teach the lowest-scoring concepts and schedule a second formative check.")
    if assignment < threshold:
        weak.append("Assignments")
        actions.append("Break the next assignment into checkpoints and review the first draft early.")
    if lab < threshold:
        weak.append("Lab")
        actions.append("Schedule guided lab practice with one worked example followed by independent execution.")
    if previous < threshold:
        weak.append("Previous-semester foundation")
        actions.append("Add prerequisite revision before introducing the next unit.")
    if backlogs > 0:
        weak.append("Backlogs")
        actions.append("Create a backlog-specific weekly slot and track completion separately from current-semester work.")

    gap = max(0.0, threshold - projected)
    if projected >= threshold + 12:
        status = "On track"
        support = "Low"
    elif projected >= threshold:
        status = "Pass possible — monitor"
        support = "Moderate"
    elif projected >= threshold - 8:
        status = "At risk — targeted support"
        support = "High"
    else:
        status = "High risk — intensive support"
        support = "Very high"

    # This is an interpretable scenario model, not a calibrated probability model.
    pass_probability = clamp(50 + (projected - threshold) * 4.5)
    if attendance < 75:
        pass_probability = clamp(pass_probability - 12)
    if backlogs > 0:
        pass_probability = clamp(pass_probability - min(18, backlogs * 6))

    if not actions:
        actions.append("Keep the current study rhythm and use weekly formative checks to catch regression early.")

    return CoachResult(
        readiness_score=round(readiness, 1),
        projected_score=round(projected, 1),
        status=status,
        pass_probability=round(pass_probability, 1),
        support_needed=support,
        weak_areas=weak,
        teaching_actions=actions,
        scenario_note=(
            "Scenario estimate based on the configured weighted academic-readiness formula. "
            "It is not a causal effect estimate and should not be reported as a guaranteed outcome."
        ),
    )


def simulate(metrics_rows: list[dict], support_marks: float, attendance_uplift: float, threshold_override: float | None):
    baseline_results = []
    supported_results = []
    for row in metrics_rows:
        baseline = evaluate(row)
        adjusted = dict(row)
        adjusted["current_internal_1"] = clamp(row["current_internal_1"] + support_marks)
        adjusted["current_internal_2"] = clamp(row["current_internal_2"] + support_marks)
        adjusted["assignment_score"] = clamp(row["assignment_score"] + support_marks)
        adjusted["lab_score"] = clamp(row["lab_score"] + support_marks)
        adjusted["attendance_pct"] = clamp(row["attendance_pct"] + attendance_uplift)
        if threshold_override is not None:
            adjusted["pass_threshold"] = threshold_override
        supported = evaluate(adjusted)
        baseline_results.append((row, baseline))
        supported_results.append((row, supported))

    def passed(result: CoachResult, row: dict) -> bool:
        return result.projected_score >= (threshold_override if threshold_override is not None else row.get("pass_threshold", 40))

    baseline_pass = sum(passed(result, row) for row, result in baseline_results)
    supported_pass = sum(passed(result, row) for row, result in supported_results)

    return {
        "total_students": len(metrics_rows),
        "baseline_pass_count": baseline_pass,
        "supported_pass_count": supported_pass,
        "additional_students_reaching_threshold": max(0, supported_pass - baseline_pass),
        "support_marks": support_marks,
        "attendance_uplift": attendance_uplift,
        "note": "The supported-pass count is a what-if scenario, not evidence that the intervention caused those outcomes.",
        "students": [
            {
                "public_ref": row["public_ref"],
                "name": row["name"],
                "baseline": asdict(baseline),
                "supported": asdict(supported),
                "improved": supported.projected_score > baseline.projected_score,
            }
            for (row, baseline), (_, supported) in zip(baseline_results, supported_results)
        ],
    }
