import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="IPL Master Intelligence Dashboard", layout="wide")

# ✨ PRO-GRADE BROADCAST UI
st.markdown("""
    <style>
    .stApp { background: #0b0e14; color: #ffffff; }
    .title-container { 
        text-align: center; padding: 30px; 
        background: linear-gradient(135deg, #1e1e2f, #0b0e14);
        border-bottom: 4px solid #00d2ff; border-radius: 0 0 25px 25px; margin-bottom: 30px;
    }
    .title-text { font-size: 50px; font-weight: 900; color: #00d2ff; letter-spacing: 2px; }
    .stMetric { background: #161b22; padding: 20px; border-radius: 15px; border-left: 5px solid #00d2ff; }
    /* Plotly Chart Glowing Border */
    .js-plotly-plot { border: 1px solid rgba(0, 210, 255, 0.1); border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    try:
        m = pd.read_csv("matches.csv")
        d = pd.read_csv("deliveries_small.csv")
        m = m.dropna(subset=['winner'])
        return m, d
    except: return pd.DataFrame(), pd.DataFrame()

matches, deliveries = load_data()

# ------------------ LOGO & TITLE ------------------
logo_url = "https://m.media-amazon.com/images/I/41mS7N29yDL.jpg"
st.markdown(f"""
    <div class="title-container">
        <img src="{logo_url}" width="110" style="border-radius: 50%; box-shadow: 0 0 20px #00d2ff;">
        <div class="title-text">IPL MASTER INTELLIGENCE</div>
    </div>
    """, unsafe_allow_html=True)

if matches.empty:
    st.error("Bhai, data files (CSV) missing hain! Please GitHub par upload karo.")
    st.stop()

# ------------------ SIDEBAR NAVIGATION ------------------
st.sidebar.image(logo_url, width=150)
st.sidebar.markdown("---")
menu = st.sidebar.radio("📊 MASTER MENU", 
    ["📈 Overall Stats", "🏆 Season Mastery", "🚩 Team Dominance", "👤 Player Deep-Dive", "⚡ Advanced Analytics", "🔮 Win Predictor"])

# --- 1. OVERALL STATS ---
if menu == "📈 Overall Stats":
    st.header("🌍 All-Time League Panorama")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Matches", matches.shape[0])
    c2.metric("Total Teams", matches['team1'].nunique())
    c3.metric("Total 4s/6s", f"{deliveries[deliveries['total_runs'] >= 4].shape[0]:,}")
    c4.metric("Total Runs", f"{deliveries['total_runs'].sum():,}")

    col1, col2 = st.columns(2)
    with col1:
        runs = deliveries.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(runs, x='total_runs', y='batter', orientation='h', title="Top 10 Batsmen", template="plotly_dark", color='total_runs', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        wickets = deliveries[deliveries['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10).reset_index()
        wickets.columns = ['bowler', 'wickets']
        fig2 = px.bar(wickets, x='wickets', y='bowler', orientation='h', title="Top 10 Bowlers", template="plotly_dark", color='wickets', color_continuous_scale='Reds')
        st.plotly_chart(fig2, use_container_width=True)

# --- 2. SEASON MASTERY ---
elif menu == "🏆 Season Mastery":
    year = st.sidebar.selectbox("Select Season", sorted(matches['season'].unique(), reverse=True))
    st.header(f"🎖️ Season {year} - Caps & Highlights")
    m_yr = matches[matches['season'] == year]
    d_yr = deliveries[deliveries['match_id'].isin(m_yr['id'])]
    
    col1, col2 = st.columns(2)
    with col1:
        oc = d_yr.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        st.plotly_chart(px.bar(oc, x='total_runs', y='batter', orientation='h', title="🟠 Orange Cap Leaderboard", template="plotly_dark", color_discrete_sequence=['#ffa500']), use_container_width=True)
    with col2:
        pc = d_yr[d_yr['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10).reset_index()
        pc.columns = ['bowler', 'wickets']
        st.plotly_chart(px.bar(pc, x='wickets', y='bowler', orientation='h', title="🟣 Purple Cap Leaderboard", template="plotly_dark", color_discrete_sequence=['#800080']), use_container_width=True)

# --- 3. TEAM DOMINANCE ---
elif menu == "🚩 Team Dominance":
    team = st.selectbox("Select Team", sorted(matches['team1'].unique()))
    st.header(f"🚩 {team} Performance Analysis")
    team_data = matches[(matches['team1'] == team) | (matches['team2'] == team)]
    wins = team_data[team_data['winner'] == team].shape[0]
    losses = team_data.shape[0] - wins
    
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.pie(values=[wins, losses], names=['Wins', 'Losses'], hole=0.5, title="Win/Loss Ratio", color_discrete_sequence=['#00d2ff', '#ff4b4b']), use_container_width=True)
    with c2:
        opp_wins = team_data[team_data['winner'] != team]['winner'].value_counts().reset_index()
        st.plotly_chart(px.bar(opp_wins, x='winner', y='count', title="Toughest Opponents (Wins Against You)", template="plotly_dark"), use_container_width=True)

# --- 4. PLAYER DEEP-DIVE ---
elif menu == "👤 Player Deep-Dive":
    player = st.selectbox("Select Player", sorted(deliveries['batter'].unique()))
    p_data = deliveries[deliveries['batter'] == player].merge(matches[['id', 'season']], left_on='match_id', right_on='id')
    
    st.header(f"👤 {player} Career Insights")
    yearly = p_data.groupby('season')['total_runs'].sum().reset_index()
    st.plotly_chart(px.area(yearly, x='season', y='total_runs', title="Runs Scored Over Seasons", template="plotly_dark", color_discrete_sequence=['#00d2ff']), use_container_width=True)

# --- 5. ADVANCED ANALYTICS ---
elif menu == "⚡ Advanced Analytics":
    st.header("⚡ Professional Phase & Death Over Study")
    deliveries['phase'] = deliveries['over'].apply(lambda x: 'Powerplay' if x <= 6 else ('Middle' if x <= 15 else 'Death'))
    
    col1, col2 = st.columns(2)
    with col1:
        phase_runs = deliveries.groupby('phase')['total_runs'].sum().reset_index()
        st.plotly_chart(px.pie(phase_runs, values='total_runs', names='phase', hole=0.5, title="Run Distribution by Phase"), use_container_width=True)
    with col2:
        death_overs = deliveries[deliveries['over'] >= 16]
        do_runs = death_overs.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        st.plotly_chart(px.bar(do_runs, x='total_runs', y='batter', orientation='h', title="Best Finishers (16-20 Overs)", color_discrete_sequence=['#39ff14']), use_container_width=True)

# --- 6. WIN PREDICTOR ---
elif menu == "🔮 Win Predictor":
    st.header("🔮 AI Historical Predictor")
    t1 = st.selectbox("Team 1", sorted(matches['team1'].unique()))
    t2 = st.selectbox("Team 2", sorted(matches['team1'].unique()))
    if t1 != t2 and st.button("Predict Winning Chance"):
        h2h = matches[((matches['team1'] == t1) & (matches['team2'] == t2)) | ((matches['team1'] == t2) & (matches['team2'] == t1))]
        if not h2h.empty:
            p1 = (h2h[h2h['winner'] == t1].shape[0] / h2h.shape[0]) * 100
            st.subheader(f"{t1}: {p1:.1f}% | {t2}: {100-p1:.1f}%")
            st.progress(p1 / 100)
        else: st.info("No Head-to-Head data found.")
