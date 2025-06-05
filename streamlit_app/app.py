import streamlit as st

st.title("Neural Query Tool (Demo)")

patient_id = st.text_input("Patient ID")
task_type = st.selectbox("Task Type", ["Go/No-Go", "Memory", "Visual"])
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

if st.button("Run Query"):
    st.success(f"Querying data for patient '{patient_id}', task '{task_type}' between {start_date} and {end_date}")
    st.write({
        "patient_id": patient_id,
        "task_type": task_type,
        "start": str(start_date),
        "end": str(end_date),
    })
