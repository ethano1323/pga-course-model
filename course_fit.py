def calculate_course_fit(df, weights):
    """
    Calculates course-adjusted Strokes Gained (SG) in true SG units.

    base_sg = overall golfer strength
    sg_*    = baseline skill splits

    Course SG redistributes base SG according to course demands.
    """

    # Sum of baseline skill SG components
    df["skill_sum"] = (
        df["sg_app"] +
        df["sg_ott"] +
        df["sg_atg"] +
        df["sg_putt"]
    )

    # Weighted skill SG based on course emphasis
    df["weighted_skill_sg"] = (
        df["sg_app"]  * weights["app"] +
        df["sg_ott"]  * weights["ott"] +
        df["sg_atg"]  * weights["atg"] +
        df["sg_putt"] * weights["putt"]
    )

    # Course-adjusted SG (remains in SG units)
    df["course_sg"] = (
        df["weighted_skill_sg"] +
        (df["base_sg"] - df["skill_sum"])
    )

    return df.sort_values("course_sg", ascending=False)

