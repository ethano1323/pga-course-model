import numpy as np

# -----------------------------------
# PGA Tour Baseline Weights
# -----------------------------------
BASELINE_WEIGHTS = {
    "app": 0.32,
    "ott": 0.28,
    "atg": 0.18,
    "putt": 0.22
}

def calculate_course_fit(df, course_weights, ch_weight=0.15):
    baseline = BASELINE_WEIGHTS

    # Baseline SG decomposition
    df["baseline_calc_sg"] = (
        baseline["app"]  * df["sg_app"] +
        baseline["ott"]  * df["sg_ott"] +
        baseline["atg"]  * df["sg_atg"] +
        baseline["putt"] * df["sg_putt"]
    )

    # Course-specific adjustment (delta from baseline)
    df["delta_sg"] = (
        (course_weights["app"]  - baseline["app"])  * df["sg_app"] +
        (course_weights["ott"]  - baseline["ott"])  * df["sg_ott"] +
        (course_weights["atg"]  - baseline["atg"])  * df["sg_atg"] +
        (course_weights["putt"] - baseline["putt"]) * df["sg_putt"]
    )

    # Course-adjusted SG
    df["course_sg"] = df["base_sg"] + df["delta_sg"]

    # -----------------------------------
    # Apply Course History Adjustment
    # -----------------------------------
    df["course_sg"] = (
        df["course_sg"] * (1 - ch_weight)
        + df["ch_sg"] * ch_weight
    )

    # Differential vs baseline
    df["differential"] = df["course_sg"] - df["base_sg"]

    # Efficiency metric
    # Course efficiency (stable across all skill levels)
    k = 0.35  # sensitivity scale (≈ meaningful SG swing)
    df["efficiency"] = np.tanh(df["differential"] / k)


    # Rounding for display
    df["course_sg"] = df["course_sg"].round(2)
    df["differential"] = df["differential"].round(2)
    df["efficiency"] = df["efficiency"].round(2)

    return df.sort_values("course_sg", ascending=False)
