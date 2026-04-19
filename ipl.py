import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="IPL Elite Analytics Pro", layout="wide")

# 🌙 PREMIUM DARK THEME STYLING
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e0e0e0; }
    .title-container { 
        text-align: center; padding: 30px; 
        background: linear-gradient(90deg, #1c1c2b 0%, #0b0e14 50%, #1c1c2b 100%);
        border-bottom: 2px solid #00d2ff; border-radius: 0 0 30px 30px; margin-bottom: 30px;
    }
    .title-text { color: #00d2ff; font-size: 45px; font-weight: 900; text-transform: uppercase; letter-spacing: 2px; }
    .stMetric { background-color: #161b22; padding: 20px; border-radius: 15px; border-top: 3px solid #00d2ff; }
    </style>
    """, unsafe_allow_html=True)

# ------------------ LOGO & TITLE ------------------
logo_url = "https://m.media-amazon.com/images/I/41mS7N29yDL.jpg"
st.markdown(f"""
    <div class="title-container">
        <img src="{logo_url}" width="120" style="border-radius: 50%; box-shadow: 0 0 15px #00d2ff;">
        <div class="title-text">IPL Data Intelligence Pro</div>
    </div>
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

# ------------------ SIDEBAR ------------------
st.sidebar.image(logo_url, width=150)
st.sidebar.markdown("### 📊 Dashboard Menu")
feature = st.sidebar.radio("Select Module", 
    ["📈 Overall Statistics", "🏆 Season Mastery", "⚡ Death Overs Analysis", "🔥 Team Rivalry (H2H)", "👤 Player Deep-Dive", "🔮 Match Predictor AI"])

# 📈 1. OVERALL STATISTICS (Wapas Add Kiya)
if feature == "Overall Statistics":
    st.header("🌌 League Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Matches", matches.shape[0])
    c2.metric("Total Teams", matches['team1'].nunique())
    c3.metric("Total Runs", f"{deliveries['total_runs'].sum():,}")
    
    col1, col2 = st.columns(2)
    with col1:
        runs = deliveries.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        st.plotly_chart(px.bar(runs, x='total_runs', y='batter', orientation='h', title="Top 10 Batsmen", template="plotly_dark", color_discrete_sequence=['#00d2ff']), use_container_width=True)
    with col2:
        wickets = deliveries[deliveries['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10).reset_index()
        wickets.columns = ['bowler', 'wickets']
        st.plotly_chart(px.bar(wickets, x='wickets', y='bowler', orientation='h', title="Top 10 Bowlers", template="plotly_dark", color_discrete_sequence=['#ff4b4b']), use_container_width=True)

# 🏆 2. SEASON MASTERY (Wapas Add Kiya)
if feature == "Season Mastery":
    year = st.sidebar.selectbox("Select Year", sorted(matches['season'].unique(), reverse=True))
    st.header(f"🎖️ Season {year} Analysis")
    m_yr = matches[matches['season'] == year]
    d_yr = deliveries[deliveries['match_id'].isin(m_yr['id'])]
    
    c1, c2 = st.columns(2)
    with c1:
        oc = d_yr.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        st.plotly_chart(px.bar(oc, x='total_runs', y='batter', orientation='h', title="Orange Cap Race", template="plotly_dark", color='total_runs', color_continuous_scale='Oranges'), use_container_width=True)
    with c2:
        pc = d_yr[d_yr['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10).reset_index()
        pc.columns = ['bowler', 'wickets']
        st.plotly_chart(px.bar(pc, x='wickets', y='bowler', orientation='h', title="Purple Cap Race", template="plotly_dark", color='wickets', color_continuous_scale='Purples'), use_container_width=True)

# ⚡ 3. DEATH OVERS ANALYSIS (Unique Feature)
if feature == "Death Overs Analysis":
    st.header("⚡ Death Overs Specialist (16-20 Over)")
    death_overs = deliveries[deliveries['over'] >= 16]
    col1, col2 = st.columns(2)
    with col1:
        do_runs = death_overs.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        st.plotly_chart(px.bar(do_runs, x='total_runs', y='batter', orientation='h', title="Death Over Hitters", template="plotly_dark", color_continuous_scale='Turbo'), use_container_width=True)
    with col2:
        # Phase Breakdown
        deliveries['phase'] = deliveries['over'].apply(lambda x: 'Powerplay' if x <= 6 else ('Middle' if x <= 15 else 'Death'))
        phase_stats = deliveries.groupby('phase')['total_runs'].sum().reset_index()
        st.plotly_chart(px.pie(phase_stats, values='total_runs', names='phase', hole=0.5, title="Run Distribution by Phase"), use_container_width=True)

# 🔥 4. TEAM RIVALRY (H2H)
if feature == "Team Rivalry (H2H)":
    st.header("⚔️ Team vs Team Dominance")
    t1 = st.selectbox("Team 1", sorted(matches['team1'].unique()), index=0)
    t2 = st.selectbox("Team 2", sorted(matches['team1'].unique()), index=1)
    h2h = matches[((matches['team1'] == t1) & (matches['team2'] == t2)) | ((matches['team1'] == t2) & (matches['team2'] == t1))]
    if not h2h.empty:
        st.plotly_chart(px.bar(h2h['winner'].value_counts().reset_index(), x='winner', y='count', title=f"{t1} vs {t2} Historical Wins", template="plotly_dark", color='winner'), use_container_width=True)
    else: st.info("No matches found between these teams.")

# 👤 5. PLAYER DEEP-DIVE
if feature == "Player Deep-Dive":
    player = st.selectbox("Select Player", sorted(deliveries['batter'].unique()))
    p_data = deliveries[deliveries['batter'] == player]
    p_prog = p_data.merge(matches[['id', 'season']], left_on='match_id', right_on='id')
    yearly = p_prog.groupby('season')['total_runs'].sum().reset_index()
    st.plotly_chart(px.line(yearly, x='season', y='total_runs', title=f"{player} Career Graph", markers=True, template="plotly_dark"), use_container_width=True)

# 🔮 6. MATCH PREDICTOR AI
if feature == "Match Predictor AI":
    st.header("🔮 Win Probability Simulation")
    ta = st.selectbox("Select Team A", sorted(matches['team1'].unique()))
    tb = st.selectbox("Select Team B", sorted(matches['team1'].unique()))
    if ta != tb and st.button("Predict Winner"):
        h2h_p = matches[((matches['team1'] == ta) & (matches['team2'] == tb)) | ((matches['team1'] == tb) & (matches['team2'] == ta))]
        if not h2h_p.empty:
            win_p = (h2h_p[h2h_p['winner'] == ta].shape[0] / h2h_p.shape[0]) * 100
            st.subheader(f"Historical Chance: {ta} ({win_p:.1f}%) vs {tb} ({100-win_p:.1f}%)")
            st.progress(win_p / 100)
        else: st.write("Insufficient history for prediction.")
