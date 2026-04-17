import streamlit as st
import pandas as pd
import pickle

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="IPL Dashboard", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .title { text-align: center; color: #ff4b4b; font-size: 40px; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="title">🏏 IPL Premium Dashboard</div>', unsafe_allow_html=True)

# ------------------ LOAD DATA ------------------
# GitHub par file paths fix kar diye hain
matches = pd.read_csv("matches.csv")
deliveries = pd.read_csv("deliveries_small.csv")

# ------------------ CLEAN DATA ------------------
matches = matches.dropna(subset=['team1', 'team2', 'toss_winner', 'toss_decision', 'winner'])

# ------------------ SIDEBAR ------------------
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
    # batsman_runs ko total_runs se replace kiya hai
    runs = data.groupby('batter')['total_runs'].sum()
    wickets = data[data['dismissal_kind'].notna()].groupby('bowler').size()
    
    col1, col2 = st.columns(2)
    col1.subheader("🔥 Top Batsmen")
    col1.bar_chart(runs.sort_values(ascending=False).head(5))
    
    col2.subheader("🎯 Top Bowlers")
    col2.bar_chart(wickets.sort_values(ascending=False).head(5))

# 🔮 MATCH PREDICTION
if feature == "Match Prediction":
    st.info("Prediction feature uses a pre-trained model.")
    # Add your prediction logic here if needed

# 📊 BALL BY BALL
if feature == "Ball-by-Ball":
    match_id = st.selectbox("Select Match ID", sorted(data['match_id'].unique()))
    ball_data = data[data['match_id'] == match_id]
    st.dataframe(ball_data.head(20))

# 🟠 ORANGE CAP
if feature == "Orange Cap":
    runs = data.groupby('batter')['total_runs'].sum()
    st.header("🟠 Orange Cap Leaderboard")
    st.table(runs.sort_values(ascending=False).head(10))
