def calculate_course_fit(df, weights):
    """
    Course-adjusted SG in true Strokes Gained units.

    base_sg is the anchor.
    Skill stats provide additive bonuses or penalties
    based on course emphasis.
    """

    df["course_sg"] = (
        df["base_sg"]
        + df["sg_app"]  * weights["app"]
        + df["sg_ott"]  * weights["ott"]
        + df["sg_atg"]  * weights["atg"]
        + df["sg_putt"] * weights["putt"]
    )

    return df.sort_values("course_sg", ascending=False)
