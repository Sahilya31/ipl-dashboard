import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="IPL Premium Dashboard", layout="wide")

# Professional UI Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .title-container { text-align: center; padding: 20px; border-bottom: 3px solid #ff4b4b; background-color: white; margin-bottom: 25px; border-radius: 10px; }
    .title-text { color: #1e272e; font-size: 45px; font-weight: bold; margin-top: 10px; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# ------------------ LOGO & TITLE ------------------
st.markdown("""
    <div class="title-container">
        <img src="https://m.media-amazon.com/images/I/41mS7N29yDL.jpg" width="160">
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
# Sidebar Logo
st.sidebar.image("https://m.media-amazon.com/images/I/41mS7N29yDL.jpg", width=120)
st.sidebar.title("📌 Menu")
feature = st.sidebar.selectbox("Go to Analysis", ["Overall Stats", "Season Wise Analysis", "Team Performance", "Player Profile"])

# 🏠 FEATURE 1: OVERALL STATS
if feature == "Overall Stats":
    st.header("📊 All-Time IPL Statistics")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Matches", matches.shape[0])
    col2.metric("Teams Participated", matches['team1'].nunique())
    col3.metric("Total Runs Scored", f"{deliveries['total_runs'].sum():,}")

    c1, c2 = st.columns(2)
    with c1:
        runs = deliveries.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        fig1 = px.bar(runs, x='total_runs', y='batter', orientation='h', title="Top 10 Batsmen (All Time)", 
                     color='total_runs', color_continuous_scale='Reds', labels={'total_runs':'Runs', 'batter':'Batsman'})
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        wickets = deliveries[deliveries['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10).reset_index()
        wickets.columns = ['bowler', 'wickets']
        fig2 = px.bar(wickets, x='wickets', y='bowler', orientation='h', title="Top 10 Bowlers (All Time)", 
                     color='wickets', color_continuous_scale='Purples', labels={'wickets':'Wickets', 'bowler':'Bowler'})
        st.plotly_chart(fig2, use_container_width=True)

# 📅 FEATURE 2: SEASON WISE ANALYSIS (Orange & Purple Cap)
if feature == "Season Wise Analysis":
    selected_year = st.sidebar.selectbox("Select Season", sorted(matches['season'].unique(), reverse=True))
    st.header(f"🏆 Season {selected_year} - Detailed Analysis")

    m_year = matches[matches['season'] == selected_year]
    d_year = deliveries[deliveries['match_id'].isin(m_year['id'])]

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🟠 Orange Cap Race")
        oc = d_year.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_oc = px.bar(oc, x='total_runs', y='batter', orientation='h', color='total_runs', color_continuous_scale='Oranges')
        st.plotly_chart(fig_oc, use_container_width=True)

    with c2:
        st.subheader("🟣 Purple Cap Race")
        pc = d_year[d_year['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10).reset_index()
        pc.columns = ['bowler', 'wickets']
        fig_pc = px.bar(pc, x='wickets', y='bowler', orientation='h', color='wickets', color_continuous_scale='Purples')
        st.plotly_chart(fig_pc, use_container_width=True)

# 🚩 FEATURE 3: TEAM PERFORMANCE
if feature == "Team Performance":
    team = st.selectbox("Select Team", sorted(matches['team1'].unique()))
    st.header(f"Team Stats: {team}")
    
    team_data = matches[(matches['team1'] == team) | (matches['team2'] == team)]
    wins = team_data[team_data['winner'] == team].shape[0]
    losses = team_data.shape[0] - wins
    
    fig_pie = px.pie(values=[wins, losses], names=['Wins', 'Losses'], title=f"Win vs Loss for {team}", 
                    color_discrete_sequence=['#2ecc71', '#e74c3c'], hole=0.4)
    st.plotly_chart(fig_pie)

# 👤 FEATURE 4: PLAYER PROFILE
if feature == "Player Profile":
    player = st.selectbox("Select Player", sorted(deliveries['batter'].unique()))
    p_data = deliveries[deliveries['batter'] == player]
    total_runs = p_data['total_runs'].sum()
    
    st.metric(f"Total Career Runs for {player}", total_runs)
    
    p_runs_year = p_data.merge(matches[['id', 'season']], left_on='match_id', right_on='id')
    yearly_stats = p_runs_year.groupby('season')['total_runs'].sum().reset_index()
    fig_line = px.line(yearly_stats, x='season', y='total_runs', title=f"Yearly Runs Progression: {player}", markers=True)
    st.plotly_chart(fig_line)
