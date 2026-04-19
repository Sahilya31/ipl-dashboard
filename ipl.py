import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="IPL Pro Data Scientist Dashboard", layout="wide")

# 🌙 DARK MODE & ELITE STYLING
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e0e0e0; }
    .title-container { 
        text-align: center; padding: 40px; 
        background: linear-gradient(90deg, #1c1c2b 0%, #0b0e14 50%, #1c1c2b 100%);
        border-bottom: 2px solid #00d2ff; border-radius: 0 0 30px 30px; margin-bottom: 30px;
    }
    .title-text { color: #00d2ff; font-size: 55px; font-weight: 900; text-transform: uppercase; letter-spacing: 3px; }
    .stMetric { background-color: #161b22; padding: 25px; border-radius: 15px; border-top: 4px solid #00d2ff; }
    </style>
    """, unsafe_allow_html=True)

# ------------------ LOGO & TITLE ------------------
logo_url = "https://m.media-amazon.com/images/I/41mS7N29yDL.jpg"
st.markdown(f"""
    <div class="title-container">
        <img src="{logo_url}" width="130" style="border-radius: 50%; box-shadow: 0 0 20px #00d2ff;">
        <div class="title-text">IPL Data Intelligence</div>
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
st.sidebar.markdown("### 🛠️ Advanced Analytics")
feature = st.sidebar.radio("Insights Module", 
    ["Death Overs King", "Phase-wise Analysis", "Team Dominance Heatmap", "Player Comparison Pro"])

# 🚀 1. DEATH OVERS KING (UNIQUE)
if feature == "Death Overs King":
    st.header("⚡ Death Overs Specialist (16-20 Over)")
    death_overs = deliveries[deliveries['over'] >= 16]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top Batters (Most Runs in Death)")
        do_runs = death_overs.groupby('batter')['total_runs'].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(do_runs, x='total_runs', y='batter', orientation='h', template="plotly_dark", color='total_runs', color_continuous_scale='Turbo')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Death Over Bowlers (Economy Rate)")
        do_bowls = death_overs.groupby('bowler').size().reset_index(name='balls')
        do_runs_conced = death_overs.groupby('bowler')['total_runs'].sum().reset_index()
        eco_df = do_bowls.merge(do_runs_conced, on='bowler')
        eco_df = eco_df[eco_df['balls'] > 60] # Min 10 overs in death
        eco_df['economy'] = (eco_df['total_runs'] / eco_df['balls']) * 6
        eco_df = eco_df.sort_values('economy').head(10)
        st.plotly_chart(px.bar(eco_df, x='economy', y='bowler', orientation='h', template="plotly_dark", color='economy'), use_container_width=True)

# 📊 2. PHASE-WISE ANALYSIS
if feature == "Phase-wise Analysis":
    st.header("⏱️ Match Phase Breakdown")
    deliveries['phase'] = deliveries['over'].apply(lambda x: 'Powerplay' if x <= 6 else ('Middle' if x <= 15 else 'Death'))
    
    phase_stats = deliveries.groupby('phase')['total_runs'].sum().reset_index()
    fig_phase = px.pie(phase_stats, values='total_runs', names='phase', hole=0.6, title="Where are the runs coming from?", color_discrete_sequence=px.colors.sequential.Electric)
    st.plotly_chart(fig_phase, use_container_width=True)

# 🔥 3. TEAM DOMINANCE HEATMAP
if feature == "Team Dominance Heatmap":
    st.header("🔥 Team Win-Rate Correlation")
    pivot_table = matches.pivot_table(index='team1', columns='winner', aggfunc='size', fill_value=0)
    fig_heat = px.imshow(pivot_table, text_auto=True, aspect="auto", title="Who beats whom? (Historical Wins)", color_continuous_scale='Viridis')
    st.plotly_chart(fig_heat, use_container_width=True)

# 👤 4. PLAYER COMPARISON PRO
if feature == "Player Comparison Pro":
    st.header("👤 Head-to-Head Player Comparison")
    p1 = st.selectbox("Select Player 1", sorted(deliveries['batter'].unique()), index=0)
    p2 = st.selectbox("Select Player 2", sorted(deliveries['batter'].unique()), index=1)
    
    def get_stats(p):
        d = deliveries[deliveries['batter'] == p]
        return {'Runs': d['total_runs'].sum(), 'Balls': d.shape[0], 'SR': (d['total_runs'].sum()/d.shape[0])*100 if d.shape[0]>0 else 0}
    
    s1, s2 = get_stats(p1), get_stats(p2)
    
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Scatterpolar(r=[s1['Runs'], s1['SR']], theta=['Total Runs', 'Strike Rate'], fill='toself', name=p1))
    fig_comp.add_trace(go.Scatterpolar(r=[s2['Runs'], s2['SR']], theta=['Total Runs', 'Strike Rate'], fill='toself', name=p2))
    fig_comp.update_layout(polar=dict(radialaxis=dict(visible=True)), template="plotly_dark")
    st.plotly_chart(fig_comp, use_container_width=True)
