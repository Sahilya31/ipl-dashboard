import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="IPL Elite Analytics Dashboard", layout="wide")

# Elite UI Styling
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .title-container { text-align: center; padding: 25px; border-bottom: 4px solid #ff4b4b; background: linear-gradient(to right, #ffffff, #fce4e4, #ffffff); margin-bottom: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .title-text { color: #2d3436; font-size: 48px; font-weight: 900; letter-spacing: 1px; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; border-left: 5px solid #ff4b4b; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# ------------------ LOGO & TITLE ------------------
logo_url = "https://m.media-amazon.com/images/I/41mS7N29yDL.jpg"
st.markdown(f"""
    <div class="title-container">
        <img src="{logo_url}" width="140" style="border-radius: 15px;">
        <div class="title-text">IPL ELITE ANALYTICS</div>
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
st.sidebar.markdown("---")
feature = st.sidebar.radio("🔍 SELECT ANALYTICS", 
    ["📈 Global Insights", "🏆 Season Mastery", "⚔️ Head-to-Head", "👤 Player Deep-Dive", "🏟️ Venue & Toss Expert", "🔮 Win Predictor AI"])

# 📈 GLOBAL INSIGHTS
if feature == "Global Insights":
    st.header("🌍 IPL Historical Panorama")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Matches", matches.shape[0])
    c2.metric("Total Seasons", matches['season'].nunique())
    c3.metric("Boundary Count", f"{deliveries[deliveries['total_runs'] >= 4].shape[0]:,}")
    c4.metric("Total Runs", f"{deliveries['total_runs'].sum():,}")

    col1, col2 = st.columns(2)
    with col1:
        # Runs over seasons trend
        season_runs = matches.merge(deliveries, left_on='id', right_on='match_id').groupby('season')['total_runs'].sum().reset_index()
        fig = px.line(season_runs, x='season', y='total_runs', title="Total Runs Trend (Season-wise)", markers=True, line_shape="spline")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        # Wicket types distribution
        w_types = deliveries['dismissal_kind'].value_counts().reset_index()
        fig2 = px.pie(w_types, values='count', names='dismissal_kind', title="Wicket Type Distribution", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

# 🏆 SEASON MASTERY
if feature == "Season Mastery":
    year = st.sidebar.selectbox("Select Season", sorted(matches['season'].unique(), reverse=True))
    st.header(f"🎖️ IPL Season {year} - Core Analysis")
    m_yr = matches[matches['season'] == year]
    d_yr = deliveries[deliveries['match_id'].isin(m_yr['id'])]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🟠 Orange Cap Leaderboard")
        oc = d_yr.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        st.plotly_chart(px.bar(oc, x='total_runs', y='batter', orientation='h', color='total_runs', color_continuous_scale='YlOrBr'), use_container_width=True)
    with col2:
        st.subheader("🟣 Purple Cap Leaderboard")
        pc = d_yr[d_yr['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10).reset_index()
        pc.columns = ['bowler', 'wickets']
        st.plotly_chart(px.bar(pc, x='wickets', y='bowler', orientation='h', color='wickets', color_continuous_scale='Purp'), use_container_width=True)

# 🏟️ VENUE & TOSS EXPERT
if feature == "Venue & Toss Expert":
    st.header("🏟️ Stadium & Toss Impact Study")
    venue = st.selectbox("Select Venue", sorted(matches['venue'].unique()))
    v_data = matches[matches['venue'] == venue]
    
    c1, c2 = st.columns(2)
    with c1:
        # Toss Decision at Venue
        toss_dec = v_data['toss_decision'].value_counts().reset_index()
        st.plotly_chart(px.pie(toss_dec, values='count', names='toss_decision', title=f"Toss Decisions at {venue}"), use_container_width=True)
    with c2:
        # Team success at Venue
        v_winners = v_data['winner'].value_counts().reset_index()
        st.plotly_chart(px.bar(v_winners, x='winner', y='count', title=f"Team Dominance at {venue}", color='winner'), use_container_width=True)

# 👤 PLAYER DEEP-DIVE
if feature == "Player Deep-Dive":
    st.header("👤 Player Performance Profile")
    player = st.selectbox("Select Player", sorted(deliveries['batter'].unique()))
    p_data = deliveries[deliveries['batter'] == player]
    
    # Calculate Strike Rate
    balls = p_data.shape[0]
    runs = p_data['total_runs'].sum()
    sr = (runs/balls)*100 if balls > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Runs", runs)
    col2.metric("Strike Rate", f"{sr:.2f}")
    col3.metric("Balls Faced", balls)
    
    # Season by season progress
    p_prog = p_data.merge(matches[['id', 'season']], left_on='match_id', right_on='id')
    yearly = p_prog.groupby('season')['total_runs'].sum().reset_index()
    st.plotly_chart(px.area(yearly, x='season', y='total_runs', title=f"{player}'s Career Growth"), use_container_width=True)

# 🔮 WIN PREDICTOR AI
if feature == "Win Predictor AI":
    st.header("🔮 Historical Probability Predictor")
    t1 = st.selectbox("Team 1", sorted(matches['team1'].unique()))
    t2 = st.selectbox("Team 2", sorted(matches['team1'].unique()))
    
    if t1 != t2:
        if st.button("Analyze Probabilities"):
            h2h = matches[((matches['team1'] == t1) & (matches['team2'] == t2)) | ((matches['team1'] == t2) & (matches['team2'] == t1))]
            if h2h.shape[0] > 0:
                t1_w = (h2h[h2h['winner'] == t1].shape[0] / h2h.shape[0]) * 100
                st.subheader(f"Historical Advantage: {t1_w:.1f}% for {t1}")
                st.progress(t1_w / 100)
                st.write(f"Based on {h2h.shape[0]} head-to-head matches.")
            else:
                st.info("No direct history found. Predicting based on overall win-rates...")
    else:
        st.warning("Please pick two different teams.")

# ⚔️ HEAD-TO-HEAD
if feature == "Head-to-Head":
    st.header("⚔️ Rivalry Analysis")
    ta = st.selectbox("Team A", sorted(matches['team1'].unique()))
    tb = st.selectbox("Team B", sorted(matches['team2'].unique()))
    if ta != tb:
        h2h_df = matches[((matches['team1'] == ta) & (matches['team2'] == tb)) | ((matches['team1'] == tb) & (matches['team2'] == ta))]
        st.plotly_chart(px.bar(h2h_df['winner'].value_counts().reset_index(), x='winner', y='count', color='winner', title=f"{ta} vs {tb} Results"), use_container_width=True)
