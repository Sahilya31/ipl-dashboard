import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="IPL Premium Dashboard", layout="wide")

# Custom CSS for better UI
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .title-container { text-align: center; padding: 10px; border-bottom: 2px solid #ff4b4b; margin-bottom: 20px; }
    .title-text { color: #ff4b4b; font-size: 45px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ------------------ LOGO & TITLE ------------------
st.markdown("""
    <div class="title-container">
        <img src="https://upload.wikimedia.org/wikipedia/en/thumb/8/84/Indian_Premier_League_Official_Logo.svg/1200px-Indian_Premier_League_Official_Logo.svg.png" width="150">
        <div class="title-text">IPL Analytics Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    m = pd.read_csv("matches.csv")
    d = pd.read_csv("deliveries_small.csv")
    m = m.dropna(subset=['winner'])
    return m, d

matches, deliveries = load_data()

# ------------------ SIDEBAR ------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/8/84/Indian_Premier_League_Official_Logo.svg/1200px-Indian_Premier_League_Official_Logo.svg.png", width=100)
st.sidebar.title("Navigation")
feature = st.sidebar.selectbox("Choose Analysis", ["Overall Dashboard", "Season Wise Analysis", "Team Analysis", "Player Stats"])

# 🏠 FEATURE 1: OVERALL DASHBOARD
if feature == "Overall Dashboard":
    st.header("🏏 IPL Overall Stats (All Seasons)")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Matches", matches.shape[0])
    col2.metric("Total Teams", matches['team1'].nunique())
    col3.metric("Total Runs", deliveries['total_runs'].sum())

    # Top Run Scorers Bar Chart
    runs = deliveries.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
    fig1 = px.bar(runs, x='batter', y='total_runs', title="Top 10 Batsmen of All Time", color='total_runs', color_continuous_scale='Reds')
    st.plotly_chart(fig1, use_container_width=True)

    # Top Wicket Takers Bar Chart
    wickets = deliveries[deliveries['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10).reset_index()
    wickets.columns = ['bowler', 'wickets']
    fig2 = px.bar(wickets, x='bowler', y='wickets', title="Top 10 Bowlers of All Time", color='wickets', color_continuous_scale='Purples')
    st.plotly_chart(fig2, use_container_width=True)

# 📅 FEATURE 2: SEASON WISE ANALYSIS
if feature == "Season Wise Analysis":
    selected_year = st.sidebar.selectbox("Select Season", sorted(matches['season'].unique(), reverse=True))
    st.header(f"🏆 Season {selected_year} Analysis")

    # Filter data
    m_year = matches[matches['season'] == selected_year]
    d_year = deliveries[deliveries['match_id'].isin(m_year['id'])]

    c1, c2 = st.columns(2)
    
    # Orange Cap
    with c1:
        st.subheader("🟠 Orange Cap Race")
        oc = d_year.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(5).reset_index()
        fig_oc = px.bar(oc, x='total_runs', y='batter', orientation='h', color='total_runs', color_continuous_scale='Oranges')
        st.plotly_chart(fig_oc, use_container_width=True)

    # Purple Cap
    with c2:
        st.subheader("🟣 Purple Cap Race")
        pc = d_year[d_year['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(5).reset_index()
        pc.columns = ['bowler', 'wickets']
        fig_pc = px.bar(pc, x='wickets', y='bowler', orientation='h', color='wickets', color_continuous_scale='Purples')
        st.plotly_chart(fig_pc, use_container_width=True)

# 🚩 FEATURE 3: TEAM ANALYSIS
if feature == "Team Analysis":
    team = st.selectbox("Select Team", sorted(matches['team1'].unique()))
    st.header(f"Performance of {team}")
    
    team_data = matches[(matches['team1'] == team) | (matches['team2'] == team)]
    wins = team_data[team_data['winner'] == team].shape[0]
    losses = team_data.shape[0] - wins
    
    # Win-Loss Pie Chart
    fig_pie = px.pie(values=[wins, losses], names=['Wins', 'Losses'], title=f"Win vs Loss for {team}", color_discrete_sequence=['#2ecc71', '#e74c3c'])
    st.plotly_chart(fig_pie)

# 👤 FEATURE 4: PLAYER STATS
if feature == "Player Stats":
    player = st.selectbox("Select Batsman", sorted(deliveries['batter'].unique()))
    p_data = deliveries[deliveries['batter'] == player]
    total_p_runs = p_data['total_runs'].sum()
    st.metric(f"Total Runs for {player}", total_p_runs)
    
    # Season-wise runs for player
    p_runs_year = deliveries[deliveries['batter'] == player].merge(matches[['id', 'season']], left_on='match_id', right_on='id')
    yearly_stats = p_runs_year.groupby('season')['total_runs'].sum().reset_index()
    fig_line = px.line(yearly_stats, x='season', y='total_runs', title=f"Performance Graph: {player}")
    st.plotly_chart(fig_line)
