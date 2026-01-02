import streamlit as st
import pandas as pd

from course_fit import calculate_course_fit
from fantasy import project_fantasy_points

st.set_page_config(page_title="PGA Course Fit Model", layout="wide")

st.title("🏌️ PGA Course-Adjusted SG & Fantasy Projection Model")

# -----------------------------------
# Upload Golfer Data (REQUIRED)
# -----------------------------------
st.sidebar.header("Upload Golfer SG Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload golfer SG CSV",
    type=["csv"]
)

if uploaded_file is None:
    st.warning("Please upload a golfer SG CSV to continue.")
    st.stop()

golfers = pd.read_csv(uploaded_file)

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
st.dataframe(golfers)

# -----------------------------------
# Course Weights
# -----------------------------------
st.sidebar.header("Course Skill Weights")

w_app  = st.sidebar.slider("Approach", 0.0, 1.0, 0.40)
w_ott  = st.sidebar.slider("Off the Tee", 0.0, 1.0, 0.25)
w_atg  = st.sidebar.slider("Around the Green", 0.0, 1.0, 0.20)
w_putt = st.sidebar.slider("Putting", 0.0, 1.0, 0.15)

weight_sum = w_app + w_ott + w_atg + w_putt
if abs(weight_sum - 1.0) > 0.001:
    st.sidebar.warning(f"Weights sum to {weight_sum:.2f} (recommended: 1.00)")

weights = {
    "app": w_app,
    "ott": w_ott,
    "atg": w_atg,
    "putt": w_putt
}

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
ranked = project_fantasy_points(
    ranked,
    difficulty_multiplier=difficulty_multiplier
)

# -----------------------------------
# Results
# -----------------------------------
st.subheader("Course-Adjusted SG Rankings")
st.dataframe(
    ranked[["player", "course_sg"]].reset_index(drop=True)
)

st.subheader("Fantasy Point Projections")
st.dataframe(
    ranked[["player", "fantasy_points"]].reset_index(drop=True)
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

