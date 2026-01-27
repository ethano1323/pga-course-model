import numpy as np

def calculate_course_fit(df, course_weights):
    baseline = BASELINE_WEIGHTS

    # Baseline SG (what base_sg SHOULD look like if decomposed)
    df["baseline_calc_sg"] = (
        baseline["app"]  * df["sg_app"] +
        baseline["ott"]  * df["sg_ott"] +
        baseline["atg"]  * df["sg_atg"] +
        baseline["putt"] * df["sg_putt"]
    )

    # Delta from course emphasis
    df["delta_sg"] = (
        (course_weights["app"]  - baseline["app"])  * df["sg_app"] +
        (course_weights["ott"]  - baseline["ott"])  * df["sg_ott"] +
        (course_weights["atg"]  - baseline["atg"])  * df["sg_atg"] +
        (course_weights["putt"] - baseline["putt"]) * df["sg_putt"]
    )

    # Course-adjusted SG
    df["course_sg"] = df["base_sg"] + df["delta_sg"]

    # Differential vs base
    df["differential"] = df["course_sg"] - df["base_sg"]

    # Efficiency (course sensitivity ratio)
    df["efficiency"] = df["differential"] / df["base_sg"].replace(0, 0.01)

    # Rounding
    df["course_sg"] = df["course_sg"].round(2)
    df["differential"] = df["differential"].round(2)
    df["efficiency"] = df["efficiency"].round(2)

    return df.sort_values("course_sg", ascending=False)
