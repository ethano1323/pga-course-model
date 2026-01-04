def calculate_course_fit(df, weights):
    """
    Course-adjusted Strokes Gained (SG).

    base_sg is the golfer's true talent level.
    Skill SGs add or subtract based on course demands.
    """

    df["course_sg"] = (
        df["base_sg"]
        + df["sg_app"]  * weights["app"]
        + df["sg_ott"]  * weights["ott"]
        + df["sg_atg"]  * weights["atg"]
        + df["sg_putt"] * weights["putt"]
    )

    # Difference from baseline (course fit impact)
    df["sg_delta"] = df["course_sg"] - df["base_sg"]

    return df.sort_values("course_sg", ascending=False)
