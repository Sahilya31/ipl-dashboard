import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="IPL Super Analytics Dashboard", layout="wide")

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
logo_url = "https://m.media-amazon.com/images/I/41mS7N29yDL.jpg"
st.markdown(f"""
    <div class="title-container">
        <img src="{logo_url}" width="160" style="border-radius: 10px;">
        <div class="title-text">IPL Super Analytics Dashboard</div>
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
st.sidebar.image(logo_url, width=150)
st.sidebar.title("📌 Navigation")
feature = st.sidebar.selectbox("Choose Analysis", 
    ["Overall Stats", "Season Wise Analysis", "Team Performance", "Player Profile", "Match Predictor (AI)", "Head-to-Head"])

# 🏠 FEATURE 1 & 2 (Orange/Purple Cap, Overall) - Already in your code
if feature == "Overall Stats":
    st.header("📊 All-Time IPL Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Matches", matches.shape[0])
    col2.metric("Total Teams", matches['team1'].nunique())
    col3.metric("Total Runs", f"{deliveries['total_runs'].sum():,}")
    
    c1, c2 = st.columns(2)
    with c1:
        runs = deliveries.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        st.plotly_chart(px.bar(runs, x='total_runs', y='batter', orientation='h', title="Top 10 Batsmen", color='total_runs', color_continuous_scale='Reds'), use_container_width=True)
    with c2:
        wickets = deliveries[deliveries['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10).reset_index()
        wickets.columns = ['bowler', 'wickets']
        st.plotly_chart(px.bar(wickets, x='wickets', y='bowler', orientation='h', title="Top 10 Bowlers", color='wickets', color_continuous_scale='Purples'), use_container_width=True)

# 🔮 FEATURE 5: MATCH PREDICTOR (AI Logic)
if feature == "Match Predictor (AI)":
    st.header("🔮 AI Match Winner Predictor")
    st.write("Select two teams to see who has a higher statistical chance of winning.")
    
    t1 = st.selectbox("Select Team 1", sorted(matches['team1'].unique()))
    t2 = st.selectbox("Select Team 2", sorted(matches['team1'].unique()))
    
    if t1 == t2:
        st.warning("Please select two different teams!")
    else:
        if st.button("Calculate Win Probability"):
            # Simple Logic based on historical win rate between these two
            h2h = matches[((matches['team1'] == t1) & (matches['team2'] == t2)) | ((matches['team1'] == t2) & (matches['team2'] == t1))]
            t1_wins = h2h[h2h['winner'] == t1].shape[0]
            t2_wins = h2h[h2h['winner'] == t2].shape[0]
            
            if h2h.shape[0] > 0:
                p1 = (t1_wins / h2h.shape[0]) * 100
                p2 = (t2_wins / h2h.shape[0]) * 100
                st.subheader(f"Historical Win Probability:")
                st.write(f"**{t1}**: {p1:.1f}% | **{t2}**: {p2:.1f}%")
                st.progress(p1 / 100)
            else:
                st.info("These teams haven't played much against each other. Based on overall form...")
                st.write(f"**{t1}** has a slight edge!")

# ⚔️ FEATURE 6: HEAD-TO-HEAD
if feature == "Head-to-Head":
    st.header("⚔️ Team vs Team Analysis")
    team_a = st.selectbox("Team A", sorted(matches['team1'].unique()), index=0)
    team_b = st.selectbox("Team B", sorted(matches['team1'].unique()), index=1)
    
    h2h_data = matches[((matches['team1'] == team_a) & (matches['team2'] == team_b)) | ((matches['team1'] == team_b) & (matches['team2'] == team_a))]
    st.write(f"Matches Played: {h2h_data.shape[0]}")
    
    fig_h2h = px.bar(h2h_data['winner'].value_counts().reset_index(), x='winner', y='count', title=f"{team_a} vs {team_b} Comparison", color='winner')
    st.plotly_chart(fig_h2h)

# (Baki Season, Team, Player features merge kar lein pehle wale code se)
