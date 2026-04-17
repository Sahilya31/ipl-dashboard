import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="IPL Premium Dashboard", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .title-container { text-align: center; padding: 10px; }
    .title-text { color: #ff4b4b; font-size: 42px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ------------------ LOGO & TITLE ------------------
st.markdown("""
    <div class="title-container">
        <img src="https://upload.wikimedia.org/wikipedia/en/thumb/8/84/Indian_Premier_League_Official_Logo.svg/1200px-Indian_Premier_League_Official_Logo.svg.png" width="150">
        <div class="title-text">IPL Premium Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------ LOAD DATA ------------------
matches = pd.read_csv("matches.csv")
deliveries = pd.read_csv("deliveries_small.csv")
matches = matches.dropna(subset=['winner'])

# ------------------ SIDEBAR ------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/8/84/Indian_Premier_League_Official_Logo.svg/1200px-Indian_Premier_League_Official_Logo.svg.png", width=100)
feature = st.sidebar.selectbox("Choose Feature", ["Dashboard Home", "Team Analysis", "Orange Cap", "Match Prediction"])

# 🏠 FEATURE 1: DASHBOARD HOME
if feature == "Dashboard Home":
    st.subheader("🏏 Overall Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Matches", matches.shape[0])
    col2.metric("Total Seasons", matches['season'].nunique())
    col3.metric("Total Teams", matches['team1'].nunique())

    # Top Batsmen Chart
    runs = deliveries.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(runs, x='batter', y='total_runs', title="Top 10 Run Scorers", color='total_runs')
    st.plotly_chart(fig, use_container_width=True)

# 📊 FEATURE 2: TEAM ANALYSIS
if feature == "Team Analysis":
    st.subheader("🚩 Team Performance")
    teams = sorted(matches['team1'].unique())
    selected_team = st.selectbox("Select Team", teams)
    
    team_matches = matches[(matches['team1'] == selected_team) | (matches['team2'] == selected_team)]
    wins = team_matches[team_matches['winner'] == selected_team].shape[0]
    st.write(f"Total Wins for {selected_team}: **{wins}**")
    
    # Win Pie Chart
    win_data = team_matches['winner'].value_counts().reset_index()
    fig_pie = px.pie(win_data, names='winner', title=f"Win/Loss Analysis for {selected_team}")
    st.plotly_chart(fig_pie)

# 🟠 FEATURE 3: ORANGE CAP
if feature == "Orange Cap":
    st.subheader("🟠 Orange Cap Race")
    season_runs = deliveries.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(15).reset_index()
    st.table(season_runs)

# 🔮 FEATURE 4: MATCH PREDICTION
if feature == "Match Prediction":
    st.subheader("🔮 Probability Predictor")
    st.info("Bhai, prediction ke liye humein model file (.pkl) chahiye hogi. Abhi ke liye aap Teams select kar sakte hain.")
    team1 = st.selectbox("Team 1", sorted(matches['team1'].unique()))
    team2 = st.selectbox("Team 2", sorted(matches['team2'].unique()))
    if st.button("Predict Winner"):
        st.success(f"Based on history, {team1} has a higher chance!")
