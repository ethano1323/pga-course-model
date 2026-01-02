def calculate_course_fit(df, weights):
    """
    Calculates course-fit score by anchoring to base_sg
    and reweighting skill distribution based on course demands.
    """

    skill_total = (
        df["sg_app"] +
        df["sg_ott"] +
        df["sg_atg"] +
        df["sg_putt"]
    )

    df["skill_weighted"] = (
        df["sg_app"]  * weights["app"] +
        df["sg_ott"]  * weights["ott"] +
        df["sg_atg"]  * weights["atg"] +
        df["sg_putt"] * weights["putt"]
    )

    df["course_fit"] = df["base_sg"] * (df["skill_weighted"] / skill_total)

    return df.sort_values("course_fit", ascending=False)

