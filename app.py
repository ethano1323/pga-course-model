import streamlit as st
import pandas as pd

from course_fit import calculate_course_fit
from fantasy import add_cut_and_round_expectations

st.set_page_config(page_title="PGA Course Fit Model", layout="wide")

st.title("🏌️ PGA Course-Adjusted SG & Fantasy Projection Model")

# -----------------------------------
# Upload Golfer Data (REQUIRED)
# -----------------------------------
st.sidebar.header("Upload Golfer SG Data")

uploaded_2025 = st.sidebar.file_uploader(
    "Upload 2025 Golfer SG CSV",
    type=["csv"],
)

uploaded_3yr = st.sidebar.file_uploader(
    "Upload 3-Year Historical SG CSV",
    type=["csv"],
)

if uploaded_2025 is None or uploaded_3yr is None:
    st.warning("Please upload BOTH the 2025 and 3-Year SG CSVs to continue.")
    st.stop()

golfers_2025 = pd.read_csv(uploaded_2025)
golfers_3yr = pd.read_csv(uploaded_3yr)

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

missing_2025 = required_columns - set(golfers_2025.columns)
missing_3yr = required_columns - set(golfers_3yr.columns)

if missing_2025:
    st.error(f"2025 data missing columns: {', '.join(missing_2025)}")
    st.stop()

if missing_3yr:
    st.error(f"3-Year data missing columns: {', '.join(missing_3yr)}")
    st.stop()

# -----------------------------------
# Merge the Data
# -----------------------------------

golfers = golfers_2025.merge(
    golfers_3yr,
    on="player",
    suffixes=("_2025", "_3yr"),
    how="inner",
)

# -----------------------------------
# Blend Base SG then keep 2025 Splits
# -----------------------------------

golfers["base_sg"] = (
    0.7 * golfers["base_sg_2025"]
    + 0.3 * golfers["base_sg_3yr"]
)

golfers["sg_app"] = golfers["sg_app_2025"]
golfers["sg_ott"] = golfers["sg_ott_2025"]
golfers["sg_atg"] = golfers["sg_atg_2025"]
golfers["sg_putt"] = golfers["sg_putt_2025"]

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
# Run Model
# -----------------------------------
ranked = calculate_course_fit(golfers.copy(), weights)

ranked = add_cut_and_round_expectations(
    ranked,
    total_rounds=total_rounds,
    cut_size=cut_size,
    all_play_all=all_play_all,
)

# -----------------------------------
# Results
# -----------------------------------
st.subheader("Course-Adjusted SG Rankings")

display_df = ranked[
    [
        "player",
        "base_sg",
        "course_sg",
        "differential",
        "cut_prob",
        "expected_rounds",
        "efficiency",
    ]
].reset_index(drop=True)

def efficiency_color(val):
    if val > 0.25:
        return "background-color: #1b7837"  # dark green
    elif val < -0.25:
        return "background-color: #762a83"  # dark red
    else:
        return ""

styled_df = (
    display_df
    .style
    .format({
        "base_sg": "{:.2f}",
        "course_sg": "{:.2f}",
        "differential": "{:.2f}",
        "cut_prob": "{:.2f}",
        "expected_rounds": "{:.2f}",
        "efficiency": "{:.2f}",
    })
    .applymap(
        efficiency_color,
        subset=["efficiency"],
    )
)

st.dataframe(styled_df)

# -----------------------------------
# Download
# -----------------------------------
st.download_button(
    label="Download Results CSV",
    data=ranked.to_csv(index=False),
    file_name="pga_course_adjusted_sg_output.csv",
    mime="text/csv",
)

