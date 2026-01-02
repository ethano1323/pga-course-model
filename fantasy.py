def project_fantasy_points(df, difficulty_multiplier, scale=100):
    """
    Converts course-fit score into fantasy points,
    adjusted for course difficulty.
    """
    df["fantasy_points"] = (
        df["course_fit"] * scale * difficulty_multiplier
    )
    return df


