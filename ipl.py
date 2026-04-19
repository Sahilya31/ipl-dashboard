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
        # Looking for files in the root folder
        m = pd.read_csv("matches.csv")
        d = pd.read_csv("deliveries_small.csv")
        m = m.dropna(subset=['winner'])
        return m, d
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

matches, deliveries = load_data()

# ------------------ DATA VALIDATION ------------------
if matches.empty or deliveries.empty:
    st.error("### ⚠️ Data Files Missing!")
    st.write("Bhai, `matches.csv` aur `deliveries_small.csv` files aapki GitHub repository mein nahi mil rahi hain.")
    st.info("💡 **Steps to Fix:**")
    st.markdown("""
    1. Go to your GitHub Repo: [Sahilya31/ipl-dashboard](https://github.com/Sahilya31/ipl-dashboard)
    2. Click on **'Add file'** -> **'Upload files'**
    3. Upload `matches.csv` and `deliveries_small.csv`
    4. Commit changes and Refresh your dashboard!
    """)
    st.stop()

# ------------------ SIDEBAR & MODULES ------------------
st.sidebar.image(logo_url, width=150)
st.sidebar.markdown("### 📊 Dashboard Menu")
feature = st.sidebar.radio("Select Module", 
    ["📈 Overall Statistics", "🏆 Season Mastery", "⚡ Death Overs Analysis", "🔥 Team Rivalry (H2H)", "👤 Player Deep-Dive", "🔮 Match Predictor AI"])

# 📈 1. OVERALL STATISTICS
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

# 🏆 2. SEASON MASTERY
elif feature == "Season Mastery":
    year = st.sidebar.selectbox("Select Year", sorted(matches['season'].unique(), reverse=True))
    st.header(f"🎖️ Season {year} Analysis")
    m_yr = matches[matches['season'] == year]
    d_yr = deliveries[deliveries['match_id'].isin(m_yr['id'])]
    
    c1, c2 = st.columns(2)
    with c1:
        oc = d_yr.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        st.plotly_chart(px.bar(oc, x='total_runs', y='batter', orientation='h', title="Orange Cap Race", template="plotly_dark", color='total_runs', color_continuous_scale='Oranges'), use_container_width=True)
    with col2:
        pc = d_yr[d_yr['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10).reset_index()
        pc.columns = ['bowler', 'wickets']
        st.plotly_chart(px.bar(pc, x='wickets', y='bowler', orientation='h', title="Purple Cap Race", template="plotly_dark", color='wickets', color_continuous_scale='Purples'), use_container_width=True)

# (Additional features: Death Overs, H2H, Player Profile, and Predictor follow the same pattern)
