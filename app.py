import streamlit as st
import pandas as pd

from course_fit import calculate_course_fit
from fantasy import add_cut_and_round_expectations


st.set_page_config(page_title="PGA Course Fit Model", layout="wide")

st.title("🏌️ PGA Course-Adjusted SG & Fantasy Projection Model")

# -----------------------------------
# Upload Golfer Data (REQUIRED)
# -----------------------------------
st.subheader("Uploaded Golfer Data")
st.dataframe(golfers)

uploaded_file = st.sidebar.file_uploader(
    "Upload golfer SG CSV",
    type=["csv"]
)

if uploaded_file is None:
    st.warning("Please upload a golfer SG CSV to continue.")
    st.stop()

golfers = pd.read_csv(uploaded_file)

st.write("Columns detected:", list(golfers.columns))


# -----------------------------------
# Validate Columns
# -----------------------------------
required_columns = {
    "player",
    "base_sg",
    "sg_app",
    "sg_atg",
    "sg_putt",
    "sg_ott"
}

missing_cols = required_columns - set(golfers.columns)

if missing_cols:
    st.error(f"Missing required columns: {', '.join(missing_cols)}")
    st.stop()

st.subheader("Uploaded Golfer Data")
)

# -----------------------------------
# Course Weights
# -----------------------------------
st.sidebar.header("Course Skill Weights")

w_app  = st.sidebar.slider("Approach", 0.0, 1.0, 0.33)
w_ott  = st.sidebar.slider("Off the Tee", 0.0, 1.0, 0.25)
w_atg  = st.sidebar.slider("Around the Green", 0.0, 1.0, 0.17)
w_putt = st.sidebar.slider("Putting", 0.0, 1.0, 0.25)

st.sidebar.caption(
    "Weights represent how much the course rewards each skill.\n"
    "They do NOT need to sum to 1."
)

weights = {
    "app": w_app,
    "ott": w_ott,
    "atg": w_atg,
    "putt": w_putt
}

# -----------------------------------
# Course Weights
# -----------------------------------
st.sidebar.header("Event Structure")

total_rounds = st.sidebar.number_input(
    "Total Rounds",
    min_value=2,
    max_value=5,
    value=4,
    step=1
)

cut_size = st.sidebar.number_input(
    "Golfers Making the Cut",
    min_value=1,
    max_value=len(golfers),
    value=65,
    step=1
)

all_play_all = st.sidebar.checkbox(
    "All golfers play all rounds",
    value=False
)


# -----------------------------------
# Course Difficulty
# -----------------------------------
st.sidebar.header("Course Difficulty")

course_avg_score = st.sidebar.number_input(
    "Average Course Score (Par 72)",
    min_value=65.0,
    max_value=75.0,
    value=71.5,
    step=0.1
)

difficulty_multiplier = 72 / course_avg_score
st.sidebar.caption(
    f"Difficulty Multiplier: {difficulty_multiplier:.3f}"
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

# 1️⃣ Build the display dataframe FIRST
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

# 2️⃣ Define the color function
def efficiency_color(val):
    if val >= 0:
        return f"background-color: rgba(0, 128, 0, {min(abs(val), 1)})"
    else:
        return f"background-color: rgba(139, 0, 0, {min(abs(val), 1)})"

# 3️⃣ Display with styling
st.dataframe(
    display_df.style.applymap(
        efficiency_color,
        subset=["efficiency"]
    )
)



# -----------------------------------
# Download
# -----------------------------------
st.download_button(
    "Download Results CSV",
    ranked.to_csv(index=False),
    "pga_course_adjusted_sg_output.csv",
    "text/csv"
)

