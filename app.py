import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pickle

# 1. Load the ML Model
try:
    with open('drug_model.pkl', 'rb') as f:
        ml_model = pickle.load(f)
except:
    st.error("Please run 'python train_model.py' first!")

st.title("🧪 Multi-Patient BioClear Simulator")

# 2. Initialize Session State (This stores our patients)
if 'patients' not in st.session_state:
    st.session_state.patients = []

# 3. Sidebar for adding new patients
st.sidebar.header("Add New Patient Profile")
new_bmi = st.sidebar.slider("BMI", 15.0, 45.0, 22.0)
new_age = st.sidebar.slider("Age", 18, 80, 25)
new_name = st.sidebar.text_input("Patient Name", f"Patient {len(st.session_state.patients) + 1}")

if st.sidebar.button("Add Patient to Study"):
    # Predict half-life immediately using the ML model
    hl = ml_model.predict([[new_bmi, new_age, 1.0]])[0]
    st.session_state.patients.append({
        "name": new_name,
        "bmi": new_bmi,
        "age": new_age,
        "hl": hl
    })

if st.sidebar.button("Clear All Patients"):
    st.session_state.patients = []

# 4. Display and Plot
if st.session_state.patients:
    dose = st.number_input("Shared Dose (mg)", value=100)
    fig, ax = plt.subplots(figsize=(10, 6))
    time = np.linspace(0, 100, 500)
    
    # Loop through all patients in the list
    for p in st.session_state.patients:
        k = np.log(2) / p['hl']
        conc = dose * np.exp(-k * time)
        ax.plot(time, conc, label=f"{p['name']} (BMI: {p['bmi']})")

    ax.axhline(y=10, color='r', linestyle='--', label="Detection Limit")
    ax.set_xlabel("Hours")
    ax.set_ylabel("Concentration (ng/mL)")
    ax.legend()
    st.pyplot(fig)

    # Display a summary table
    st.write("### Patient Comparison Table")
    st.table(st.session_state.patients)
    import pandas as pd

if st.session_state.patients:
    # 1. Create a DataFrame from our patient list
    export_df = pd.DataFrame(st.session_state.patients)
    
    # 2. Add a calculated column for "Estimated Clear Time"
    # Formula: t = -ln(cutoff/dose) / k
    export_df['clear_time_hrs'] = -np.log(10/dose) / (np.log(2)/export_df['hl'])
    
    # 3. Convert DataFrame to CSV
    csv = export_df.to_csv(index=False).encode('utf-8')

    # 4. Create the Download Button
    st.download_button(
        label="📥 Download Study Data as CSV",
        data=csv,
        file_name='bioclear_study_results.csv',
        mime='text/csv',
    )
else:
    st.info("Add patients from the sidebar to start the simulation.")
