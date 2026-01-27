import numpy as np

BASELINE_WEIGHTS = {
    "app": 0.32,
    "ott": 0.28,
    "atg": 0.18,
    "putt": 0.22,
}

def calculate_course_fit(df, course_weights, ch_weight=0.15):
    """
    Calculates course-adjusted SG with normalized course history weighting.
    """

    # -------------------------------
    # Normalize course weights
    # -------------------------------
    total_w = sum(course_weights.values())
    norm_w = {k: v / total_w for k, v in course_weights.items()}

    # -------------------------------
    # Baseline skill expectation
    # -------------------------------
    df["baseline_skill_sg"] = (
        BASELINE_WEIGHTS["app"]  * df["sg_app"] +
        BASELINE_WEIGHTS["ott"]  * df["sg_ott"] +
        BASELINE_WEIGHTS["atg"]  * df["sg_atg"] +
        BASELINE_WEIGHTS["putt"] * df["sg_putt"]
    )

    # -------------------------------
    # Course-weighted skill output
    # -------------------------------
    df["course_skill_sg"] = (
        norm_w["app"]  * df["sg_app"] +
        norm_w["ott"]  * df["sg_ott"] +
        norm_w["atg"]  * df["sg_atg"] +
        norm_w["putt"] * df["sg_putt"]
    )

    # -------------------------------
    # Skill-based adjustment
    # -------------------------------
    df["skill_delta"] = df["course_skill_sg"] - df["baseline_skill_sg"]

    # Add skill delta to base SG
    df["skill_adjusted_sg"] = df["base_sg"] + df["skill_delta"]

    # -------------------------------
    # NORMALIZED COURSE HISTORY BLEND
    # -------------------------------
    df["course_sg"] = (
        (1 - ch_weight) * df["skill_adjusted_sg"]
        + ch_weight * df["ch_sg"]
    )

    # -------------------------------
    # Outputs
    # -------------------------------
    df["differential"] = df["course_sg"] - df["base_sg"]

    # Efficiency: stable, symmetric scaling
    df["efficiency"] = df["differential"] / (1 + df["base_sg"].abs())

    return df.sort_values("course_sg", ascending=False).reset_index(drop=True)

