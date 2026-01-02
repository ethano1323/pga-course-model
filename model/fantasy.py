def project_fantasy_points(df, difficulty_multiplier, scale=100):
    """
    Converts course-fit score into fantasy point projection.
    Difficulty multiplier adjusts scoring for course toughness.
    """

    df["fantasy_points"] = (
        df["course_fit"] * scale * difficulty_multiplier
    )

    return df

