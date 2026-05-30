import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_lottie import st_lottie
import requests
from db_utils import (
    init_db, log_weight, get_weight_history, 
    log_calories, get_calorie_history, 
    log_workout, get_workout_history,
    log_water, get_water_history,
    set_setting, get_setting
)

# --- CONFIG & VERSION CHECK ---
init_db()
st.set_page_config(page_title="ULTRA Fitness", page_icon="⚡", layout="wide")

# GitHub Version check
VERSION = "1.3" 
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/nkar123412-hub/Hermess-repository/main/version.txt"

def check_for_updates():
    try:
        response = requests.get(GITHUB_VERSION_URL, timeout=2)
        if response.status_code == 200:
            remote_version = response.text.strip()
            if remote_version != VERSION:
                return True
    except:
        pass
    return False

if check_for_updates():
    st.warning("🔄 Доступно обновление! Пожалуйста, обновите страницу, чтобы получить новые функции")

# --- CUSTOM CSS FOR NEON DARK THEME ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    :root { --neon-blue: #00D4FF; --neon-green: #39FF14; --dark-card: #1A1C24; }
    div[data-testid="stMetric"] {
        background: rgba(26, 28, 36, 0.6);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
    div.stForm { background: rgba(26, 28, 36, 0.8); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); padding: 30px; }
    .stButton>button {
        background: linear-gradient(45deg, #00D4FF, #0055FF);
        color: white; border: none; border-radius: 10px; font-weight: bold; width: 100%;
    }
    .stButton>button:hover { box-shadow: 0 0 15px #00D4FF; transform: translateY(-2px); }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #FFFFFF; text-shadow: 0 0 10px rgba(0, 212, 255, 0.5); }
    .stTable { background-color: #1A1C24; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

lottie_workout = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_tivbc6vo.json")
lottie_weight = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_5njp8vtp.json")
lottie_water = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_h8sc6oia.json")
lottie_calories = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_7z2xv9be.json")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>⚡ ULTRA Fitness</h1>", unsafe_allow_html=True)
    st.markdown("---")
    menu = ["Dashboard", "Weight", "Calories", "Workout", "Hydration", "Settings"]
    choice = st.sidebar.selectbox("Main Menu", menu)
    st.markdown("---")
    st.markdown(f"**Version:** {VERSION}")
    st.markdown("✨ *Stay Consistent. Stay Strong.*")

# --- MAIN CONTENT ---

if choice == "Dashboard":
    st.markdown("<h2 style='text-align: center;'>🚀 YOUR PROGRESS</h2>", unsafe_allow_html=True)
    
    weight_df = get_weight_history()
    calorie_df = get_calorie_history()
    workout_df = get_workout_history()
    water_df = get_water_history()
    goal_weight = get_setting("goal_weight")
    
    # 1. Top Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if not weight_df.empty:
            cur_w = weight_df.iloc[-1]['weight']
            start_w = weight_df.iloc[0]['weight']
            diff = start_w - cur_w
            st.metric("Current Weight", f"{cur_w} kg", delta=f"-{diff:.2f} kg")
        else: st.info("No weight data")
    with col2:
        if not calorie_df.empty: st.metric("Daily Calories", f"{calorie_df.iloc[-1]['calories']} kcal")
        else: st.info("No calorie data")
    with col3:
        if not workout_df.empty: st.metric("Total Workouts", f"{len(workout_df)} sessions")
        else: st.info("No workout data")
    with col4:
        if not water_df.empty: st.metric("Today's Water", f"{water_df.iloc[0]['amount']} ml")
        else: st.info("No water data")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Goal Progress Bar
    if not weight_df.empty and goal_weight:
        cur_w = weight_df.iloc[-1]['weight']
        goal_w = float(goal_weight)
        start_w = weight_df.iloc[0]['weight']
        total_to_lose = start_w - goal_w
        already_lost = start_w - cur_w
        progress = max(0, min(100, (already_lost / total_to_lose) * 100 if total_to_lose != 0 else 0))
        st.markdown(f"### 🎯 Goal Progress: {cur_w}kg $\rightarrow$ {goal_w}kg")
        st.progress(progress / 100)
        st.write(f"**{progress:.1f}%** of your target achieved!")

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Quick Log Buttons (UX Improvement)
    st.markdown("### ⚡ Quick Log")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
    if qcol1.button("⚖️ Log Weight"): st.session_state.choice = "Weight"
    if qcol2.button("🍎 Log Calories"): st.session_state.choice = "Calories"
    if qcol3.button("🏋️ Log Workout"): st.session_state.choice = "Workout"
    if qcol4.button("💧 Log Water"): st.session_state.choice = "Hydration"

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Main Charts
    row1_col1, row1_col2 = st.columns([2, 1])
    with row1_col1:
        st.markdown("### 📈 Weight Trend")
        if not weight_df.empty: st.line_chart(weight_df.set_index('date')['weight'])
        else: st.info("Start logging weight to see the trend!")
    with row1_col2:
        st.markdown("### ⚡ Energy")
        if lottie_workout: st_lottie(lottie_workout, height=200, key="dash_anim")

elif choice == "Weight":
    st.markdown("## ⚖️ Weight Management")
    if st.button("⬅️ Back to Dashboard"): st.session_state.choice = "Dashboard"
    col1, col2 = st.columns([1, 1])
    with col1:
        if lottie_weight: st_lottie(lottie_weight, height=250)
        with st.form("weight_form"):
            weight_input = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
            if st.form_submit_button("Update Weight"):
                log_weight(weight_input)
                st.success("Saved!")
    with col2:
        st.table(get_weight_history().tail(10))

elif choice == "Calories":
    st.markdown("## 🍎 Calorie Tracker")
    if st.button("⬅️ Back to Dashboard"): st.session_state.choice = "Dashboard"
    col1, col2 = st.columns([1, 1])
    with col1:
        if lottie_calories: st_lottie(lottie_calories, height=250)
        with st.form("calorie_form"):
            cal_input = st.number_input("Calories (kcal)", min_value=0, step=1)
            if st.form_submit_button("Save Calories"):
                log_calories(cal_input)
                st.success("Saved!")
    with col2:
        st.table(get_calorie_history().tail(10))

elif choice == "Workout":
    st.markdown("## 🏋️ Training Log")
    if st.button("⬅️ Back to Dashboard"): st.session_state.choice = "Dashboard"
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.form("workout_form"):
            exercise = st.text_input("Exercise Name")
            duration = st.number_input("Duration (min)", min_value=0, step=1)
            intensity = st.selectbox("Intensity", ["Low", "Medium", "High"])
            if st.form_submit_button("Add Workout"):
                log_workout(exercise, duration, intensity)
                st.success("Logged!")
    with col2:
        st.table(get_workout_history().tail(10))

elif choice == "Hydration":
    st.markdown("## 💧 Water Intake")
    if st.button("⬅️ Back to Dashboard"): st.session_state.choice = "Dashboard"
    col1, col2 = st.columns([1, 1])
    with col1:
        if lottie_water: st_lottie(lottie_water, height=250)
        with st.form("water_form"):
            water_input = st.number_input("Amount (ml)", min_value=0, step=100)
            if st.form_submit_button("Add Water"):
                log_water(water_input)
                st.success("Stay hydrated!")
    with col2:
        st.table(get_water_history().tail(10))

elif choice == "Settings":
    st.markdown("## ⚙️ App Settings")
    current_goal = get_setting("goal_weight")
    with st.form("settings_form"):
        goal_weight_input = st.number_input("Set Goal Weight (kg)", 
                                            value=float(current_goal) if current_goal else 70.0, 
                                            step=0.1)
        if st.form_submit_button("Save Profile"):
            set_setting("goal_weight", goal_weight_input)
            st.success("Profile Updated!")
