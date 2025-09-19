import streamlit as st
import pandas as pd
from database_setup import create_table, fetch_all, insert_train
from csv_to_db import insert_from_csv

st.title("🚆 Train Database Manager")

# Ensure table exists
create_table()

# --- Section 1: Upload CSV ---
st.header("📂 Upload CSV to Insert Data")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Preview of uploaded file:", df.head())

    if st.button("Insert CSV into Database"):
        insert_from_csv(uploaded_file)
        st.success("CSV data inserted successfully!")

# --- Section 2: Add Record Manually ---
st.header("✍️ Insert a New Train Record")

with st.form("insert_form"):
    fitness_certificate = st.text_input("Fitness Certificate")
    job_card = st.text_input("Job Card")
    branding_priority = st.selectbox("Branding Priority", ["High", "Medium", "Low"])
    mileage_balancing = st.number_input("Mileage Balancing", min_value=0.0, step=100.0)
    cleaning_slot = st.text_input("Cleaning Slot")
    depot_positioning = st.text_input("Depot Positioning")

    submitted = st.form_submit_button("Insert Record")

    if submitted:
        insert_train(fitness_certificate, job_card, branding_priority,
                     mileage_balancing, cleaning_slot, depot_positioning)
        st.success("Record inserted successfully!")

# --- Section 3: Show All Records ---
st.header("📊 Train Records in Database")
data = fetch_all()
if data:
    df = pd.DataFrame(data, columns=[
        "ID", "Fitness Certificate", "Job Card", "Branding Priority",
        "Mileage Balancing", "Cleaning Slot", "Depot Positioning"
    ])
    st.dataframe(df)
else:
    st.info("No records found yet.")
