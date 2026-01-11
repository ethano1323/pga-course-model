import numpy as np
import pandas as pd


def probability_to_american_odds(p):
    if p <= 0:
        return np.nan
    if p >= 1:
        return -10000
    if p >= 0.5:
        return -110 * (p / (1 - p))
    else:
        return 110 * ((1 - p) / p)


def calculate_true_odds(df, alpha=1.0, sg_floor=0.75):
    df = df.copy()

    # Soft floor adjustment
    df["adj_sg"] = df["course_sg"] + sg_floor

    # Exponential skill
    df["skill"] = np.exp(alpha * df["adj_sg"])

    # Normalize to win probabilities
    total_skill = df["skill"].sum()
    df["win_prob"] = df["skill"] / total_skill

    # Finish probabilities
    df["top5_prob"] = np.minimum(df["win_prob"] * 4.5, 1.0)
    df["top10_prob"] = np.minimum(df["win_prob"] * 8.5, 1.0)
    df["top20_prob"] = np.minimum(df["win_prob"] * 16.0, 1.0)

    # Convert to odds
    df["Winner Odds"] = df["win_prob"].apply(probability_to_american_odds)
    df["Top 5 Odds"] = df["top5_prob"].apply(probability_to_american_odds)
    df["Top 10 Odds"] = df["top10_prob"].apply(probability_to_american_odds)
    df["Top 20 Odds"] = df["top20_prob"].apply(probability_to_american_odds)

    # Percent columns
    df["Win %"] = df["win_prob"] * 100
    df["Top 5 %"] = df["top5_prob"] * 100
    df["Top 10 %"] = df["top10_prob"] * 100
    df["Top 20 %"] = df["top20_prob"] * 100

    # Clean up
    return df[
        [
            "player",
            "Winner Odds",
            "Win %",
            "Top 5 Odds",
            "Top 5 %",
            "Top 10 Odds",
            "Top 10 %",
            "Top 20 Odds",
            "Top 20 %",
        ]
    ].round(
        {
            "Win %": 2,
            "Top 5 %": 2,
            "Top 10 %": 2,
            "Top 20 %": 2,
        }
    )
