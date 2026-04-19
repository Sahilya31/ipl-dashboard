import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="IPL Elite Neon Dashboard", layout="wide")

# ✨ NEON GLOW & GLASSMORPHISM UI
st.markdown("""
    <style>
    /* Main Background with subtle gradient */
    .stApp {
        background: radial-gradient(circle at top left, #1e1e2f, #0b0e14);
        color: #ffffff;
    }
    
    /* Neon Title Container */
    .title-container {
        text-align: center;
        padding: 40px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        box-shadow: 0 0 30px rgba(0, 210, 255, 0.2);
        margin-bottom: 35px;
    }
    
    .title-text {
        background: linear-gradient(to right, #00d2ff, #3a7bd5, #ff4b4b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 60px;
        font-weight: 900;
        letter-spacing: -1px;
    }

    /* Glass Cards for Metrics */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px !important;
        border-radius: 15px;
        transition: transform 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #00d2ff;
        box-shadow: 0 10px 20px rgba(0, 210, 255, 0.1);
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 15, 25, 0.8);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------ LOGO & TITLE ------------------
logo_url = "https://m.media-amazon.com/images/I/41mS7N29yDL.jpg"

st.markdown(f"""
    <div class="title-container">
        <img src="{logo_url}" width="140" style="border-radius: 50%; box-shadow: 0 0 20px #00d2ff;">
        <div class="title-text">IPL ELITE NEON DASHBOARD</div>
        <p style="color: #888; letter-spacing: 5px;">ADVANCED DATA INTELLIGENCE</p>
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
    st.warning("⚠️ Data load nahi ho raha. Check karein ki files upload hain?")
else:
    # ------------------ SIDEBAR ------------------
    st.sidebar.image(logo_url, width=150)
    feature = st.sidebar.radio("🔭 EXPLORE ANALYTICS", 
        ["📈 Global Insights", "🏆 Season Mastery", "⚡ Death Overs Analysis", "⚔️ Team Rivalry", "👤 Player Profiles"])

    # 📈 GLOBAL INSIGHTS
    if feature == "Global Insights":
        st.header("🌍 Historical Dominance")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Matches", matches.shape[0])
        c2.metric("Teams", matches['team1'].nunique())
        c3.metric("Avg Runs/Match", int(deliveries['total_runs'].sum()/matches.shape[0]))
        c4.metric("Total 4s/6s", f"{deliveries[deliveries['total_runs'] >= 4].shape[0]:,}")

        col1, col2 = st.columns(2)
        with col1:
            runs = deliveries.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
            fig1 = px.bar(runs, x='total_runs', y='batter', orientation='h', 
                         title="All-Time Leading Scorers", template="plotly_dark",
                         color='total_runs', color_continuous_scale='Blues')
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)
            
        with col2:
            wickets = deliveries[deliveries['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10).reset_index()
            wickets.columns = ['bowler', 'wickets']
            fig2 = px.bar(wickets, x='wickets', y='bowler', orientation='h', 
                         title="Leading Wicket Takers", template="plotly_dark",
                         color='wickets', color_continuous_scale='Reds')
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

    # ⚡ DEATH OVERS ANALYSIS (Unique Graphic)
    if feature == "Death Overs Analysis":
        st.header("⚡ The Death Over Specialists (16-20 Over)")
        death = deliveries[deliveries['over'] >= 16]
        
        c1, c2 = st.columns(2)
        with c1:
            do_runs = death.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
            fig_do = px.scatter(do_runs, x='total_runs', y='batter', size='total_runs', 
                               color='total_runs', title="Most Dangerous Finishers", template="plotly_dark")
            st.plotly_chart(fig_do, use_container_width=True)
            
        with c2:
            phase = deliveries.groupby('over')['total_runs'].sum().reset_index()
            fig_area = px.area(phase, x='over', y='total_runs', title="Run Aggression by Over", 
                              template="plotly_dark", color_discrete_sequence=['#00d2ff'])
            st.plotly_chart(fig_area, use_container_width=True)

    # (Season Mastery, Rivalry etc. features merge ho jayenge)
