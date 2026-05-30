import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from db_utils import (
    init_db, log_weight, get_weight_history, 
    log_calories, get_calorie_history, 
    log_workout, get_workout_history,
    log_water, get_water_history,
    set_setting, get_setting
)

# Initialize Database
init_db()

st.set_page_config(page_title="Fitness & Weight Loss Tracker", layout="wide")

st.title("💪 Fitness & Weight Loss Tracker")
st.markdown("Track your journey, stay consistent, and reach your goals!")

# Sidebar for navigation
menu = ["Dashboard", "Weight Tracker", "Calorie Counter", "Workout Log", "Hydration", "Settings"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Dashboard":
    st.header("📊 Overview")
    
    # Get current data
    weight_df = get_weight_history()
    calorie_df = get_calorie_history()
    workout_df = get_workout_history()
    water_df = get_water_history()
    goal_weight = get_setting("goal_weight")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    if not weight_df.empty:
        current_weight = weight_df.iloc[-1]['weight']
        start_weight = weight_df.iloc[0]['weight']
        weight_diff = start_weight - current_weight
        col1.metric("Current Weight", f"{current_weight} kg", delta=f"-{weight_diff:.2f} kg" if weight_diff > 0 else f"+{weight_diff:.2f} kg")
        
        if goal_weight:
            remaining = float(goal_weight) - current_weight
            if remaining < 0:
                col1.success(f"Goal reached! You are {abs(remaining):.2f}kg under goal!")
            else:
                col1.info(f"Goal: {goal_weight}kg ({remaining:.2f}kg to go)")
    else:
        col1.write("No weight data yet.")
        
    if not calorie_df.empty:
        latest_calories = calorie_df.iloc[-1]['calories']
        col2.metric("Last Calorie Log", f"{latest_calories} kcal")
    else:
        col2.write("No calorie data yet.")

    if not workout_df.empty:
        total_workouts = len(workout_df)
        col3.metric("Total Workouts", f"{total_workouts} sessions")
    else:
        col3.write("No workout data yet.")
        
    if not water_df.empty:
        latest_water = water_df.iloc[0]['amount']
        col4.metric("Today's Water", f"{latest_water} ml")
    else:
        col4.write("No water data yet.")

    # Weight Loss Graph
    st.subheader("📈 Weight Progress")
    if not weight_df.empty:
        st.line_chart(weight_df.set_index('date')['weight'])
    else:
        st.info("Log your weight to see the progress chart!")

elif choice == "Weight Tracker":
    st.header("⚖️ Weight Tracker")
    
    with st.form("weight_form"):
        weight_input = st.number_input("Enter your weight (kg)", min_value=0.0, step=0.1)
        submit_weight = st.form_submit_button("Save Weight")
        
        if submit_weight:
            log_weight(weight_input)
            st.success("Weight saved successfully!")

    st.subheader("History")
    st.table(get_weight_history())

elif choice == "Calorie Counter":
    st.header("🍎 Calorie Counter")
    
    with st.form("calorie_form"):
        cal_input = st.number_input("Enter daily calories (kcal)", min_value=0, step=1)
        submit_cal = st.form_submit_button("Save Calories")
        
        if submit_cal:
            log_calories(cal_input)
            st.success("Calories saved successfully!")

    st.subheader("History")
    st.table(get_calorie_history())

elif choice == "Workout Log":
    st.header("🏋️ Workout Log")
    
    with st.form("workout_form"):
        exercise = st.text_input("Exercise Name")
        duration = st.number_input("Duration (minutes)", min_value=0, step=1)
        intensity = st.selectbox("Intensity", ["Low", "Medium", "High"])
        submit_workout = st.form_submit_button("Save Workout")
        
        if submit_workout:
            log_workout(exercise, duration, intensity)
            st.success("Workout saved successfully!")

    st.subheader("Recent Workouts")
    st.table(get_workout_history())

elif choice == "Hydration":
    st.header("💧 Hydration Tracker")
    
    with st.form("water_form"):
        water_input = st.number_input("Add water (ml)", min_value=0, step=100)
        submit_water = st.form_submit_button("Add Water")
        
        if submit_water:
            log_water(water_input)
            st.success(f"Added {water_input}ml of water!")

    st.subheader("Water History")
    st.table(get_water_history())

elif choice == "Settings":
    st.header("⚙️ Settings")
    
    current_goal = get_setting("goal_weight")
    
    with st.form("settings_form"):
        goal_weight_input = st.number_input("Set your Goal Weight (kg)", value=float(current_goal) if current_goal else 70.0, step=0.1)
        submit_settings = st.form_submit_button("Save Settings")
        
        if submit_settings:
            set_setting("goal_weight", goal_weight_input)
            st.success("Settings saved!")
