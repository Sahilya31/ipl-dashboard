import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="IPL Dashboard", layout="wide")

# ------------------ CUSTOM CSS (UI MAGIC) ------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
.card {
    background: rgba(255,255,255,0.1);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 30px rgba(0,0,0,0.3);
    text-align: center;
    transition: 0.3s;
}
.card:hover {
    transform: scale(1.05);
}
.title {
    text-align: center;
    font-size: 40px;
    font-weight: bold;
}
div.stButton > button {
    background: linear-gradient(90deg, #ff512f, #dd2476);
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.markdown('<div class="title">🏏 IPL Premium Dashboard</div>', unsafe_allow_html=True)

# ------------------ LOAD DATA ------------------
matches = pd.read_csv("matches.csv")
deliveries = pd.read_csv("deliveries_small.csv")

# ------------------ CLEAN DATA ------------------
matches = matches.dropna(subset=['team1','team2','toss_winner','toss_decision','winner'])

deliveries['match_id'] = deliveries['match_id'].astype(int)
deliveries['over'] = deliveries['over'].astype(int)
deliveries['ball'] = deliveries['ball'].astype(int)

# ------------------ SIDEBAR ------------------
st.sidebar.title("⚙ Controls")

view_type = st.sidebar.radio("View Type", ["Overall", "Year-wise"])

season = None
if view_type == "Year-wise":
    season = st.sidebar.selectbox("Season", sorted(matches['season'].unique()))

feature = st.sidebar.selectbox("Feature", [
    "Dashboard Home",
    "Match Prediction",
    "Ball-by-Ball",
    "Orange Cap",
    "Purple Cap",
    "Man of the Match",
    "Hat-trick"
])

# ------------------ FILTER DATA ------------------
if view_type == "Overall":
    data = deliveries
    match_data = matches
else:
    match_ids = matches[matches['season']==season]['id']
    data = deliveries[deliveries['match_id'].isin(match_ids)]
    match_data = matches[matches['season']==season]

# =====================================================
# 🏠 DASHBOARD HOME
# =====================================================
if feature == "Dashboard Home":

    runs = data.groupby('batter')['batsman_runs'].sum()
    wickets = data[data['dismissal_kind'].notna()].groupby('bowler').size()
    mom = match_data['player_of_match'].value_counts()

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(f"""<div class="card"><h3>🟠 Orange Cap</h3><h2>{runs.idxmax()}</h2></div>""", unsafe_allow_html=True)
    c2.markdown(f"""<div class="card"><h3>🟣 Purple Cap</h3><h2>{wickets.idxmax()}</h2></div>""", unsafe_allow_html=True)
    c3.markdown(f"""<div class="card"><h3>🌟 Most MOM</h3><h2>{mom.idxmax()}</h2></div>""", unsafe_allow_html=True)
    c4.markdown(f"""<div class="card"><h3>🏏 Matches</h3><h2>{match_data.shape[0]}</h2></div>""", unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    col1.subheader("📈 Top Batsmen")
    col1.bar_chart(runs.sort_values(ascending=False).head(5))

    col2.subheader("🎯 Top Bowlers")
    col2.bar_chart(wickets.sort_values(ascending=False).head(5))

# =====================================================
# 🔮 MATCH PREDICTION
# =====================================================
if feature == "Match Prediction":

    df = match_data[['team1','team2','toss_winner','toss_decision','winner']].dropna()

    X = pd.get_dummies(df[['team1','team2','toss_winner','toss_decision']], drop_first=True)
    y = df['winner']

    X = X.fillna(0)

    model = RandomForestClassifier()
    model.fit(X, y)

    col1, col2 = st.columns(2)

    with col1:
        team1 = st.selectbox("Team 1", df['team1'].unique())
        team2 = st.selectbox("Team 2", df['team2'].unique())

    with col2:
        toss_winner = st.selectbox("Toss Winner", [team1, team2])
        toss_decision = st.selectbox("Decision", ['bat','field'])

    if st.button("Predict Winner"):
        if team1 == team2:
            st.error("❌ Same team not allowed")
        else:
            inp = pd.DataFrame({
                'team1':[team1],
                'team2':[team2],
                'toss_winner':[toss_winner],
                'toss_decision':[toss_decision]
            })

            inp = pd.get_dummies(inp)
            inp = inp.reindex(columns=X.columns, fill_value=0)

            pred = model.predict(inp)
            st.success(f"🏆 Winner: {pred[0]}")

# =====================================================
# 📊 BALL BY BALL
# =====================================================
if feature == "Ball-by-Ball":

    match_id = st.selectbox("Match", sorted(data['match_id'].unique()))
    mdata = data[data['match_id']==match_id]

    col1, col2 = st.columns(2)

    over = col1.selectbox("Over", sorted(mdata['over'].unique()))
    ball = col2.selectbox("Ball", sorted(mdata[mdata['over']==over]['ball'].unique()))

    ball_data = mdata[(mdata['over']==over) & (mdata['ball']==ball)]

    if st.button("Get Info"):
        if not ball_data.empty:
            row = ball_data.iloc[0]
            st.success(f"🏏 Runs: {row['total_runs']}")
            c1, c2 = st.columns(2)
            c1.metric("Batsman", row['batter'])
            c2.metric("Bowler", row['bowler'])

# =====================================================
# 🟠 ORANGE CAP
# =====================================================
if feature == "Orange Cap":

    if view_type == "Overall":
        runs = data.groupby('batter')['batsman_runs'].sum()
        st.success(f"{runs.idxmax()} - {runs.max()} runs")

    else:
        result = []
        for yr in sorted(matches['season'].unique()):
            match_ids = matches[matches['season']==yr]['id']
            d = deliveries[deliveries['match_id'].isin(match_ids)]

            r = d.groupby('batter')['batsman_runs'].sum()
            if not r.empty:
                result.append([yr, r.idxmax(), r.max()])

        st.dataframe(pd.DataFrame(result, columns=["Year","Player","Runs"]))

# =====================================================
# 🟣 PURPLE CAP
# =====================================================
if feature == "Purple Cap":

    if view_type == "Overall":
        wk = data[data['dismissal_kind'].notna()]
        wc = wk.groupby('bowler').size()
        st.success(f"{wc.idxmax()} - {wc.max()} wickets")

    else:
        result = []
        for yr in sorted(matches['season'].unique()):
            match_ids = matches[matches['season']==yr]['id']
            d = deliveries[deliveries['match_id'].isin(match_ids)]

            wk = d[d['dismissal_kind'].notna()]
            wc = wk.groupby('bowler').size()

            if not wc.empty:
                result.append([yr, wc.idxmax(), wc.max()])

        st.dataframe(pd.DataFrame(result, columns=["Year","Player","Wickets"]))

# =====================================================
# 🌟 MOM
# =====================================================
if feature == "Man of the Match":

    if view_type == "Overall":
        mom = match_data['player_of_match'].value_counts()
        st.success(f"{mom.idxmax()} - {mom.max()} awards")

    else:
        df = match_data.groupby(['season','player_of_match']).size().reset_index(name='count')
        idx = df.groupby('season')['count'].idxmax()
        st.dataframe(df.loc[idx])

# =====================================================
# 🎩 HAT-TRICK (WITH PLAYER NAMES)
# =====================================================
if feature == "Hat-trick":

    hattricks = []

    for match in data['match_id'].unique():
        mdata = data[data['match_id']==match].sort_values(['over','ball'])

        for bowler in mdata['bowler'].unique():
            bdata = mdata[mdata['bowler']==bowler].copy()
            bdata['w'] = bdata['dismissal_kind'].notna().astype(int)

            wl = bdata['w'].tolist()

            for i in range(len(wl)-2):
                if wl[i]==1 and wl[i+1]==1 and wl[i+2]==1:
                    hattricks.append([bowler, match, bdata.iloc[i]['over']])
                    break

    if hattricks:
        df = pd.DataFrame(hattricks, columns=["Bowler","Match ID","Over"])
        st.success(f"🎩 Total Hat-tricks: {len(df)}")
        st.dataframe(df)

        for _, row in df.iterrows():
            st.info(f"🎯 {row['Bowler']} → Match {row['Match ID']} (Over {row['Over']})")

    else:
        st.warning("No hat-tricks found")
