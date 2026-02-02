import streamlit as st
import pandas as pd
import numpy as np

from course_fit import calculate_course_fit
from fantasy import add_cut_and_round_expectations
from true_odds import calculate_true_odds

# -----------------------------------
# Styling Helpers
# -----------------------------------
def efficiency_percentile_colors(series):
    ranks = series.rank(method="min", ascending=False, pct=True)

    styles = []
    for pct in ranks:
        if pct <= 0.10:
            styles.append("background-color: darkgreen; color: white;")
        elif pct <= 0.20:
            styles.append("background-color: lightgreen;")
        elif pct >= 0.90:
            styles.append("background-color: darkred; color: white;")
        elif pct >= 0.80:
            styles.append("background-color: lightcoral;")
        else:
            styles.append("")

    return styles


BASELINE_WEIGHTS = {
    "app": 0.32,
    "ott": 0.28,
    "atg": 0.18,
    "putt": 0.22
}

def prob_to_american(prob):
    """Convert probability to American odds"""
    prob = max(min(prob, 0.999), 0.001)  # safety clamp

    if prob >= 0.5:
        return -round(100 * prob / (1 - prob))
    else:
        return round(100 * (1 - prob) / prob)


def simulate_true_odds(
    df,
    n_sims=10_000,
    sigma=1.6,
    seed=42
):
    """
    Monte Carlo simulation for true betting odds
    based on course_sg
    """

    np.random.seed(seed)

    players = df["player"].values
    means = df["course_sg"].values
    n_players = len(players)

    # Counters
    win = np.zeros(n_players)
    top5 = np.zeros(n_players)
    top10 = np.zeros(n_players)
    top20 = np.zeros(n_players)

    for _ in range(n_sims):
        player_sigma = sigma * (1 + 0.25 * np.abs(means))
        performance = means + np.random.normal(0, player_sigma)
        ranks = performance.argsort()[::-1]

        win[ranks[0]] += 1
        top5[ranks[:5]] += 1
        top10[ranks[:10]] += 1
        top20[ranks[:20]] += 1

    odds_df = pd.DataFrame({
        "player": players,
        "Win %": win / n_sims,
        "Top 5 %": top5 / n_sims,
        "Top 10 %": top10 / n_sims,
        "Top 20 %": top20 / n_sims,
    })

    odds_df["Winner Odds"] = odds_df["Win %"].apply(prob_to_american)
    odds_df["Top 5 Odds"] = odds_df["Top 5 %"].apply(prob_to_american)
    odds_df["Top 10 Odds"] = odds_df["Top 10 %"].apply(prob_to_american)
    odds_df["Top 20 Odds"] = odds_df["Top 20 %"].apply(prob_to_american)

    # Column order
    odds_df = odds_df[
        [
            "player",
            "Winner Odds", "Win %",
            "Top 5 Odds", "Top 5 %",
            "Top 10 Odds", "Top 10 %",
            "Top 20 Odds", "Top 20 %",
        ]
    ]

    # Round percentages for display
    for col in odds_df.columns:
        if "%" in col:
            odds_df[col] = (odds_df[col] * 100).round(2)

    return odds_df.sort_values("Win %", ascending=False).reset_index(drop=True)


st.set_page_config(page_title="PGA Course Fit Model", layout="wide")

st.title("PGA Projection and Simulation Model")

# -----------------------------------
# Upload Golfer Data (REQUIRED)
# -----------------------------------
st.sidebar.header("Upload Golfer SG Data")

uploaded_L30 = st.sidebar.file_uploader(
    "Upload L30 Rounds Golfer SG CSV",
    type=["csv"],
)

uploaded_L200 = st.sidebar.file_uploader(
    "Upload L200 Rounds Golfer SG CSV",
    type=["csv"],
)


uploaded_course_history = st.sidebar.file_uploader(
    "Upload Course History CSV",
    type=["csv"],
)

if uploaded_L30 is None or uploaded_L200 is None:
    st.warning("Please upload All CSVs to continue.")
    st.stop()

if uploaded_course_history is not None:
    course_history = pd.read_csv(uploaded_course_history)

    if not {"player", "ch_sg"}.issubset(course_history.columns):
        st.error("Course history file must contain: player, ch_sg")
        st.stop()
else:
    course_history = None

golfers_l30 = pd.read_csv(uploaded_L30)
golfers_l200 = pd.read_csv(uploaded_L200)

# -----------------------------------
# Validate Columns
# -----------------------------------

required_columns = {
    "player",
    "base_sg",
    "sg_app",
    "sg_atg",
    "sg_putt",
    "sg_ott",
}

missing_l30 = required_columns - set(golfers_l30.columns)
missing_l200 = required_columns - set(golfers_l200.columns)

if missing_l30:
    st.error(f"L30 data missing columns: {', '.join(missing_l30)}")
    st.stop()

if missing_l200:
    st.error(f"L200 data missing columns: {', '.join(missing_l200)}")
    st.stop()

# -----------------------------------
# Merge the Data
# -----------------------------------

golfers = golfers_l30.merge(
    golfers_l200,
    on="player",
    suffixes=("_l30", "_l200"),
    how="inner",
)

# -----------------------------------
# Blend Base SG then keep 2025 Splits
# -----------------------------------

golfers["base_sg"] = (
    0.40 * golfers["base_sg_l30"]
    + 0.60 * golfers["base_sg_l200"]
)

golfers["sg_app"] = golfers["sg_app_l30"]
golfers["sg_ott"] = golfers["sg_ott_l30"]
golfers["sg_atg"] = golfers["sg_atg_l30"]
golfers["sg_putt"] = golfers["sg_putt_l30"]

# -----------------------------------
# Course History Integration
# -----------------------------------
if course_history is not None:
    golfers = golfers.merge(
        course_history[["player", "ch_sg", "experience_adjustment"]],
        on="player",
        how="left",
    )

    # Fill missing ch_sg with base_sg - experience_adjustment
    golfers["ch_sg"] = golfers.apply(
        lambda row: row["base_sg"] - row["experience_adjustment"]
        if pd.isna(row["ch_sg"]) or row["ch_sg"] == 0
        else row["ch_sg"],
        axis=1
    )
else:
    # If no course history CSV provided, just use base_sg - small default adjustment
    golfers["ch_sg"] = golfers["base_sg"] - 0.038

st.sidebar.header("Course History Weight")
ch_weight = st.sidebar.slider(
    "Course History Impact",
    min_value=0.10,
    max_value=0.20,
    value=0.15,
    step=0.01,
)

# -----------------------------------
# Calculate final Course SG
# -----------------------------------
# User-defined weight for course history (slider ch_weight)
base_weight = 1 - ch_weight

# Combine base SG (from L30/L200 blend) with course history
golfers["course_sg"] = (
    base_weight * golfers["base_sg"] +
    ch_weight * golfers["ch_sg"]
)

# -----------------------------------
# Event Structure
# -----------------------------------
st.sidebar.header("Event Structure")

total_rounds = st.sidebar.number_input(
    "Total Rounds",
    min_value=2,
    max_value=5,
    value=4,
    step=1,
)

cut_size = st.sidebar.number_input(
    "Golfers Making the Cut",
    min_value=1,
    max_value=len(golfers),
    value=65,
    step=1,
)

all_play_all = st.sidebar.checkbox(
    "All golfers play all rounds",
    value=False,
)

# -----------------------------------
# Player Filters
# -----------------------------------
st.sidebar.header("Player Filters")

hide_bad = st.sidebar.checkbox(
    "Hide players below -0.75 base SG",
    value=False,
)

hide_negative = st.sidebar.checkbox(
    "Hide players below 0.00 base SG",
    value=False,
)

# -----------------------------------
# Hiding Poor Values
# -----------------------------------

if hide_negative:
    golfers = golfers[golfers["base_sg"] >= 0.0]
elif hide_bad:
    golfers = golfers[golfers["base_sg"] >= -0.75]

# -----------------------------------
# Course Weights
# -----------------------------------
st.sidebar.header("Course Skill Weights")

w_app  = st.sidebar.slider("Approach", 0.0, 1.0, 0.32)
w_ott  = st.sidebar.slider("Off the Tee", 0.0, 1.0, 0.28)
w_atg  = st.sidebar.slider("Around the Green", 0.0, 1.0, 0.18)
w_putt = st.sidebar.slider("Putting", 0.0, 1.0, 0.22)

weights = {
    "app": w_app,
    "ott": w_ott,
    "atg": w_atg,
    "putt": w_putt,
}

# -----------------------------------
# Run Model
# -----------------------------------
ranked = calculate_course_fit(
    golfers.copy(),
    weights,
    ch_weight=ch_weight,
)

ranked = add_cut_and_round_expectations(
    ranked,
    total_rounds=total_rounds,
    cut_size=cut_size,
    all_play_all=all_play_all,
)

true_odds_df = simulate_true_odds(
    ranked,
    n_sims=10_000,
)

# -----------------------------------
# Results
# -----------------------------------
# Build display dataframe
display_df = ranked[
    [
        "player",
        "base_sg",
        "ch_sg",          
        "course_sg",
        "differential",
        "cut_prob",
        "expected_rounds",
        "efficiency",
    ]
].reset_index(drop=True)

# -----------------------------------
# Round values for display (CRITICAL)
# -----------------------------------
styled_df = (
    display_df
    .style
    .format({
        "base_sg": "{:.2f}",
        "ch_sg": "{:.2f}",       # <-- add formatting
        "course_sg": "{:.2f}",
        "differential": "{:.2f}",
        "cut_prob": "{:.2f}",
        "expected_rounds": "{:.2f}",
        "efficiency": "{:.2f}",
    })
    .apply(
        efficiency_percentile_colors,
        axis=0,
        subset=["efficiency"],
    )
)

st.subheader("Course-Adjusted SG Rankings")
st.dataframe(styled_df, use_container_width=True)

st.subheader("True Odds")

st.dataframe(
    true_odds_df.style.format({
        "Winner Odds": "{:+.0f}",
        "Top 5 Odds": "{:+.0f}",
        "Top 10 Odds": "{:+.0f}",
        "Top 20 Odds": "{:+.0f}",
        "Win %": "{:.2f}%",
        "Top 5 %": "{:.2f}%",
        "Top 10 %": "{:.2f}%",
        "Top 20 %": "{:.2f}%",
    }),
    use_container_width=True
)

# -----------------------------------
# Download
# -----------------------------------
st.download_button(
    label="Download Results CSV",
    data=ranked.to_csv(index=False),
    file_name="pga_course_adjusted_sg_output.csv",
    mime="text/csv",
)

