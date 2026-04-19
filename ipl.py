import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="IPL Elite Neon Dashboard", layout="wide")

# ✨ ADVANCED GLASS UI & NEON STYLING
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #1a1c2c, #0b0e14); color: #ffffff; }
    .title-container { 
        text-align: center; padding: 40px; 
        background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 210, 255, 0.3); border-radius: 20px;
        box-shadow: 0 0 30px rgba(0, 210, 255, 0.1); margin-bottom: 35px;
    }
    .title-text { 
        background: linear-gradient(90deg, #00d2ff, #3a7bd5, #ff4b4b);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 55px; font-weight: 900; letter-spacing: 2px;
    }
    /* Chart Container Styling */
    .plot-container { border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.1); padding: 10px; background: rgba(0,0,0,0.2); }
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
        <img src="{logo_url}" width="130" style="border-radius: 50%; box-shadow: 0 0 25px #00d2ff;">
        <div class="title-text">IPL ELITE NEON INTELLIGENCE</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------
feature = st.sidebar.radio("Navigate Analysis", ["📈 Global Insights", "🏆 Season Mastery", "👤 Player Profiles"])

# 📈 GLOBAL INSIGHTS (With Enhanced Graphs)
if feature == "📈 Global Insights":
    st.header("🌍 League Performance Intelligence")
    
    col1, col2 = st.columns(2)
    with col1:
        # Top Batsmen with Neon Gradient
        runs = deliveries.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        fig1 = px.bar(runs, x='total_runs', y='batter', orientation='h', 
                     title="All-Time Leading Scorers", template="plotly_dark",
                     color='total_runs', color_continuous_scale='Blues')
        
        # PRO GRAPHICS SETTINGS
        fig1.update_traces(marker_line_color='rgb(0, 210, 255)', marker_line_width=1.5, opacity=0.8)
        fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig1, use_container_width=True)
            
    with col2:
        # Top Bowlers with Neon Red
        wickets = deliveries[deliveries['dismissal_kind'].notna()].groupby('bowler').size().sort_values(ascending=False).head(10).reset_index()
        wickets.columns = ['bowler', 'wickets']
        fig2 = px.bar(wickets, x='wickets', y='bowler', orientation='h', 
                     title="Leading Wicket Takers", template="plotly_dark",
                     color='wickets', color_continuous_scale='Reds')
        
        fig2.update_traces(marker_line_color='rgb(255, 75, 75)', marker_line_width=1.5, opacity=0.8)
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig2, use_container_width=True)

# 👤 PLAYER PROFILES (With Area Curves)
if feature == "👤 Player Profiles":
    player = st.selectbox("Search Player", sorted(deliveries['batter'].unique()))
    p_data = deliveries[deliveries['batter'] == player].merge(matches[['id', 'season']], left_on='match_id', right_on='id')
    yearly = p_data.groupby('season')['total_runs'].sum().reset_index()
    
    # Smooth Area Chart
    fig_line = px.area(yearly, x='season', y='total_runs', title=f"{player} Career Progression", 
                      template="plotly_dark")
    
    fig_line.update_traces(line_color='#00d2ff', fillcolor='rgba(0, 210, 255, 0.2)', marker=dict(size=8))
    fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    st.plotly_chart(fig_line, use_container_width=True)
