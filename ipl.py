import streamlit as st
import pandas as pd

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="IPL Dashboard", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .title-container { text-align: center; padding: 10px; }
    .title-text { color: #ff4b4b; font-size: 42px; font-weight: bold; margin-bottom: 0px; }
    </style>
    """, unsafe_allow_html=True)

# ------------------ LOGO & TITLE ------------------
st.markdown(
    """
    <div class="title-container">
        <img src="https://upload.wikimedia.org/wikipedia/en/thumb/8/84/Indian_Premier_League_Official_Logo.svg/1200px-Indian_Premier_League_Official_Logo.svg.png" width="150">
        <div class="title-text">IPL Premium Dashboard</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------ LOAD DATA ------------------
matches = pd.read_csv("matches.csv")
deliveries = pd.read_csv("deliveries_small.csv")

# ------------------ CLEAN DATA ------------------
matches = matches.dropna(subset=['team1', 'team2', 'toss_winner', 'toss_decision', 'winner'])

# ------------------ SIDEBAR ------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/8/84/Indian_Premier_League_Official_Logo.svg/1200px-Indian_Premier_League_Official_Logo.svg.png", width=100)
st.sidebar.title("⚙️ Controls")
view_type = st.sidebar.radio("View Type", ["Overall", "Year-wise"])
feature = st.sidebar.selectbox("Feature", ["Dashboard Home", "Match Prediction", "Ball-by-Ball", "Orange Cap"])

# Filter Logic
if view_type == "Overall":
    data = deliveries
    match_data = matches
else:
    season = st.sidebar.selectbox("Season", sorted(matches['season'].unique()))
    match_ids = matches[matches['season'] == season]['id']
    data = deliveries[deliveries['match_id'].isin(match_ids)]
    match_data = matches[matches['season'] == season]

# 🏠 DASHBOARD HOME
if feature == "Dashboard Home":
    runs = data.groupby('batter')['total_runs'].sum()
    wickets = data[data['dismissal_kind'].notna()].groupby('bowler').size()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔥 Top Batsmen")
        st.bar_chart(runs.sort_values(ascending=False).head(10))
    
    with col2:
        st.subheader("🎯 Top Bowlers")
        st.bar_chart(wickets.sort_values(ascending=False).head(10))

# 🔮 MATCH PREDICTION
if feature == "Match Prediction":
    st.info("🔮 Match Prediction feature is coming soon with Machine Learning!")

# 📊 BALL BY BALL
if feature == "Ball-by-Ball":
    match_id = st.selectbox("Select Match ID", sorted(data['match_id'].unique()))
    ball_data = data[data['match_id'] == match_id]
    st.dataframe(ball_data.head(50))

# 🟠 ORANGE CAP
if feature == "Orange Cap":
    runs = data.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10)
    st.header("🟠 Orange Cap Leaderboard")
    st.table(runs)
