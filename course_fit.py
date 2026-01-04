import numpy as np

def calculate_course_fit(df, weights):
    """
    Course-adjusted Strokes Gained (SG).

    Adds:
    - differential: absolute SG change from course
    - fit_ratio: course impact normalized by player talent
    """

    df["course_sg"] = (
        df["base_sg"]
        + df["sg_app"]  * weights["app"]
        + df["sg_ott"]  * weights["ott"]
        + df["sg_atg"]  * weights["atg"]
        + df["sg_putt"] * weights["putt"]
    )

    # Absolute course impact
    df["differential"] = df["course_sg"] - df["base_sg"]

    # Talent-normalized course fit ratio (stable)
    df["fit_ratio"] = df["differential"] / df["base_sg"].abs().clip(lower=0.50)

    # Round outputs
    df["course_sg"] = df["course_sg"].round(2)
    df["differential"] = df["differential"].round(2)
    df["fit_ratio"] = df["fit_ratio"].round(2)

    return df.sort_values("course_sg", ascending=False)
