import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def add_cut_and_round_expectations(
    df,
    total_rounds,
    cut_size,
    all_play_all
):
    """
    Adds:
    - cut_prob: probability of making the cut
    - expected_rounds: expected number of rounds played

    Uses only course-adjusted SG rankings.
    """

    if all_play_all:
        df["cut_prob"] = 1.0
        df["expected_rounds"] = total_rounds
        return df

    # Sort by course SG
    df = df.sort_values("course_sg", ascending=False).reset_index(drop=True)

    # Determine SG at the cut line
    cut_index = min(cut_size - 1, len(df) - 1)
    cut_line_sg = df.loc[cut_index, "course_sg"]

    # Volatility parameter (empirical PGA SG noise)
    volatility = 0.75

    # Cut probability via logistic curve
    df["cut_prob"] = sigmoid(
        (df["course_sg"] - cut_line_sg) / volatility
    )

    # Expected rounds played
    df["expected_rounds"] = (
        2 + df["cut_prob"] * (total_rounds - 2)
    )

    # Round for display
    df["cut_prob"] = df["cut_prob"].round(2)
    df["expected_rounds"] = df["expected_rounds"].round(2)

    return df
