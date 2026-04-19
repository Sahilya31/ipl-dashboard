import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="IPL Elite Dark Dashboard", layout="wide")

# 🌙 DARK MODE & STYLING
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    /* Title Container */
    .title-container {
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #1e1e2f 0%, #0e1117 100%);
        border-bottom: 3px solid #ff4b4b;
        border-radius: 15px;
        margin-bottom: 25px;
    }
    .title-text {
        color: #ff4b4b;
        font-size: 50px;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        color: #00d2ff;
        font-size: 35px;
    }
    div[data-testid="stMetricLabel"] {
        color: #ffffff;
    }
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------ LOGO & TITLE ------------------
# Guaranteed Working Logo Link
logo_url = "https://m.media-amazon.com/images/I/41mS7N29yDL.jpg"

st.markdown(f"""
    <div class="title-container">
        <img src="{logo_url}" width="150" style="border-radius: 15px; border: 2px solid #ff4b4b;">
        <div class="title-text">IPL ELITE DARK DASHBOARD</div>
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
    except:
        return pd.DataFrame(), pd.DataFrame()

matches, deliveries = load_data()

if matches.empty:
    st.error("⚠️ Data files (matches.csv) missing on GitHub! Please upload them.")
else:
    # ------------------ SIDEBAR ------------------
    st.sidebar.image(logo_url, width=150)
    st.sidebar.markdown("<h2 style='color: white;'>📌 Navigation</h2>", unsafe_allow_html=True)
    feature = st.sidebar.selectbox("Choose Analysis", 
        ["Overall Stats", "Season Wise Analysis", "Team Performance", "Player Profile", "Match Predictor (AI)", "Head-to-Head"])

    # 📊 FEATURE 1: OVERALL STATS
    if feature == "Overall Stats":
        st.header("🌌 All-Time League Statistics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Matches", matches.shape[0])
        col2.metric("Total Teams", matches['team1'].nunique())
        col3.metric("Total Runs Scored", f"{deliveries['total_runs'].sum():,}")
        
        c1, c2 = st.columns(2)
        with c1:
            runs = deliveries.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
            fig1 = px.bar(runs, x='total_runs', y='batter', orientation='h', title="Top 10 Batsmen", 
                         template="plotly_dark", color_discrete_sequence=['#00d2ff'])
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            wickets = deliveries[deliveries['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10).reset_index()
            wickets.columns = ['bowler', 'wickets']
            fig2 = px.bar(wickets, x='wickets', y='bowler', orientation='h', title="Top 10 Bowlers", 
                         template="plotly_dark", color_discrete_sequence=['#ff4b4b'])
            st.plotly_chart(fig2, use_container_width=True)

    # 📅 FEATURE 2: SEASON WISE ANALYSIS
    if feature == "Season Wise Analysis":
        year = st.sidebar.selectbox("Select Season", sorted(matches['season'].unique(), reverse=True))
        st.header(f"🏆 Season {year} Deep-Dive")
        m_year = matches[matches['season'] == year]
        d_year = deliveries[deliveries['match_id'].isin(m_year['id'])]
        
        col1, col2 = st.columns(2)
        with col1:
            oc = d_year.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
            st.plotly_chart(px.bar(oc, x='total_runs', y='batter', orientation='h', title="Orange Cap Race", 
                                   template="plotly_dark", color='total_runs', color_continuous_scale='Oranges'), use_container_width=True)
        with col2:
            pc = d_year[d_year['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10).reset_index()
            pc.columns = ['bowler', 'wickets']
            st.plotly_chart(px.bar(pc, x='wickets', y='bowler', orientation='h', title="Purple Cap Race", 
                                   template="plotly_dark", color='wickets', color_continuous_scale='Purples'), use_container_width=True)

    # 🚩 FEATURE 3: TEAM PERFORMANCE
    if feature == "Team Performance":
        team = st.selectbox("Select Team", sorted(matches['team1'].unique()))
        team_data = matches[(matches['team1'] == team) | (matches['team2'] == team)]
        wins = team_data[team_data['winner'] == team].shape[0]
        losses = team_data.shape[0] - wins
        fig_pie = px.pie(values=[wins, losses], names=['Wins', 'Losses'], title=f"{team} Win/Loss Ratio", 
                        hole=0.4, template="plotly_dark", color_discrete_sequence=['#00d2ff', '#ff4b4b'])
        st.plotly_chart(fig_pie, use_container_width=True)

    # 👤 FEATURE 4: PLAYER PROFILE
    if feature == "Player Profile":
        player = st.selectbox("Select Player", sorted(deliveries['batter'].unique()))
        p_runs = deliveries[deliveries['batter'] == player].merge(matches[['id', 'season']], left_on='match_id', right_on='id')
        yearly = p_runs.groupby('season')['total_runs'].sum().reset_index()
        fig_line = px.line(yearly, x='season', y='total_runs', title=f"{player} Career Progression", 
                          markers=True, template="plotly_dark")
        fig_line.update_traces(line_color='#00d2ff')
        st.plotly_chart(fig_line, use_container_width=True)

    # 🔮 FEATURE 5: MATCH PREDICTOR
    if feature == "Match Predictor (AI)":
        st.header("🔮 Victory Probability Engine")
        t1 = st.selectbox("Team 1", sorted(matches['team1'].unique()))
        t2 = st.selectbox("Team 2", sorted(matches['team1'].unique()))
        if t1 != t2:
            if st.button("Run Simulation"):
                h2h = matches[((matches['team1'] == t1) & (matches['team2'] == t2)) | ((matches['team1'] == t2) & (matches['team2'] == t1))]
                if not h2h.empty:
                    p1 = (h2h[h2h['winner'] == t1].shape[0] / h2h.shape[0]) * 100
                    st.subheader(f"{t1}: {p1:.1f}% | {t2}: {100-p1:.1f}%")
                    st.progress(p1 / 100)
                else: st.info("No Head-to-Head data available.")

    # ⚔️ FEATURE 6: HEAD-TO-HEAD
    if feature == "Head-to-Head":
        st.header("⚔️ Rivalry Statistics")
        ta = st.selectbox("Team A", sorted(matches['team1'].unique()))
        tb = st.selectbox("Team B", sorted(matches['team1'].unique()))
        h2h_df = matches[((matches['team1'] == ta) & (matches['team2'] == tb)) | ((matches['team1'] == tb) & (matches['team2'] == ta))]
        if not h2h_df.empty:
            st.plotly_chart(px.bar(h2h_df['winner'].value_counts().reset_index(), x='winner', y='count', 
                                   template="plotly_dark", color='winner', title="Historic Wins"), use_container_width=True)
        else: st.write("No matches found between these two teams.")
