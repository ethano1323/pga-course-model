def project_fantasy_points(df, difficulty_multiplier, scale=100):
    """
    Converts course-adjusted SG into fantasy points.
    """

    df["fantasy_points"] = (
        df["course_sg"] * scale * difficulty_multiplier
    )

    return df

