import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pickle
import pandas as pd

# --- STEP 1: INITIALIZE SESSION STATE ---
# This must be at the very top to prevent errors
if 'study_data' not in st.session_state:
    st.session_state.study_data = []

# --- STEP 2: LOAD ML MODEL ---
try:
    with open('drug_model.pkl', 'rb') as f:
        ml_model = pickle.load(f)
except:
    st.error("Model file 'drug_model.pkl' not found. Please run your training script first.")

# --- STEP 3: DATABASE ---
DRUG_DB = {
    "Nicotine": {"hl": 2.0, "desc": "Rapid renal clearance."},
    "Caffeine": {"hl": 5.0, "desc": "Hepatic metabolism (CYP1A2)."},
    "THC": {"hl": 30.0, "desc": "Lipophilic; stored in fat cells."},
    "Alcohol": {"hl": 1.5, "desc": "Fast metabolism."}
}

# --- STEP 4: SIDEBAR UI ---
st.sidebar.title("🩺 Patient Inputs")

# BMI Calculator Section
with st.sidebar.expander("1. BMI Calculator", expanded=True):
    weight = st.number_input("Weight (kg)", 10.0, 200.0, 70.0)
    height_cm = st.number_input("Height (cm)", 50.0, 250.0, 170.0)
    height_m = height_cm / 100
    calc_bmi = round(weight / (height_m ** 2), 1)
    st.info(f"Calculated BMI: {calc_bmi}")

# Simulation Parameters
st.sidebar.markdown("---")
st.sidebar.subheader("2. Parameters")
drug_choice = st.sidebar.selectbox("Select Drug", list(DRUG_DB.keys()))
bmi_val = st.sidebar.slider("Use BMI Value", 15.0, 45.0, float(calc_bmi))
age_val = st.sidebar.slider("Age", 18, 80, 25)
dose_val = st.sidebar.number_input("Dose (mg)", value=100)

# THE ADD BUTTON (Placed in sidebar for visibility)
if st.sidebar.button("➕ Add Patient to Analysis"):
    # Use ML to predict multiplier (normalizing around 24h)
    multiplier = ml_model.predict([[bmi_val, age_val, 1.0]])[0] / 24.0
    final_hl = DRUG_DB[drug_choice]["hl"] * multiplier
    
    # Save to memory
    st.session_state.study_data.append({
        "Drug": drug_choice,
        "BMI": bmi_val,
        "Age": age_val,
        "HL_Hours": round(final_hl, 2),
        "Dose": dose_val
    })
    st.sidebar.success("Patient added!")

if st.sidebar.button("🗑️ Clear All Data"):
    st.session_state.study_data = []
    st.rerun()

# --- STEP 5: MAIN DASHBOARD ---
st.title("🧪 BioClear ML: Drug Elimination Dashboard")

tab1, tab2 = st.tabs(["📈 Visualization", "📋 Data Table"])

with tab1:
    if st.session_state.study_data:
        fig, ax = plt.subplots(figsize=(10, 5))
        time = np.linspace(0, 72, 500)
        
        for p in st.session_state.study_data:
            k = np.log(2) / p["HL_Hours"]
            conc = p["Dose"] * np.exp(-k * time)
            ax.plot(time, conc, label=f"{p['Drug']} (BMI: {p['BMI']})")
        
        ax.axhline(y=10, color='r', linestyle='--', label="Detection Limit")
        ax.set_xlabel("Hours")
        ax.set_ylabel("Concentration (ng/mL)")
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("Add a patient from the sidebar to see the graph.")

with tab2:
    if st.session_state.study_data:
        df = pd.DataFrame(st.session_state.study_data)
        st.dataframe(df, use_container_width=True)
        
        # Download CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results", data=csv, file_name="bioclear_results.csv", mime="text/csv")
    else:
        st.write("No data available yet.")
