import streamlit as st
import pandas as pd
import datetime
from database_setup import create_tables, insert_train, insert_record, fetch_all
from csv_to_db import insert_from_df
from simulation import run_simulation

# Custom CSS for white UI
st.markdown("""
<style>
    body {
        background-color: white;
        color: black;
    }
    .main-header {
        font-size: 2.5em;
        color: black;
        text-align: center;
        margin-bottom: 20px;
        font-family: 'Helvetica, Arial, sans-serif';
    }
    .section-header {
        color: black;
        border-bottom: 2px solid black;
        padding-bottom: 5px;
        font-family: 'Helvetica, Arial, sans-serif';
    }
    .stButton>button {
        background-color: white;
        color: black;
        border-radius: 5px;
        border: 1px solid black;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #f0f0f0;
    }
    .dataframe {
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    .stTabs {
        background: white;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #ddd;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        color: black;
        border-radius: 6px;
        border: 1px solid #ddd;
        transition: all 0.3s ease;
        font-weight: 500;
        padding: 8px 12px;
        font-size: 14px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f0f0f0;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #e0e0e0;
        color: black;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="KMRL Train Induction Platform", layout="wide")
st.markdown('<h1 class="main-header">🚆 Kochi Metro Train Database Manager</h1>', unsafe_allow_html=True)

# Ensure tables exist
create_tables()

# Top navigation tabs
tabs = st.tabs([
    "📂 Upload CSV",
    "🚉 Trains",
    "📝 Fitness Certificates",
    "🛠 Job Cards",
    "🎨 Branding",
    "📏 Mileage",
    "🧹 Cleaning Slots",
    "🏠 Depot Positions",
    "📊 Dashboard",
    "🔮 Simulation"
])

# ------------------ CSV UPLOAD ------------------
with tabs[0]:
    st.markdown('<h2 class="section-header">📂 Upload CSV Data</h2>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state['uploaded_df'] = df
            valid = not (df.empty or len(df.columns) == 0)
            if not valid:
                st.error("Uploaded file has no data or columns.")
                st.session_state['uploaded_df'] = None
        except pd.errors.EmptyDataError:
            st.error("Uploaded file is empty or invalid.")
            st.session_state['uploaded_df'] = None
        except pd.errors.ParserError:
            st.error("Uploaded file is not a valid CSV.")
            st.session_state['uploaded_df'] = None
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            st.session_state['uploaded_df'] = None
    else:
        st.session_state['uploaded_df'] = None

    col1, col2 = st.columns([1, 2])

    with col1:
        with st.expander("Upload Form", expanded=True):
            table_choice = st.selectbox("Target Table", [
                "trains", "fitness_certificates", "job_cards",
                "branding_priorities", "mileage_records",
                "cleaning_slots", "depot_positions"
            ])

            if st.button("Insert into DB"):
                if table_choice and st.session_state.get('uploaded_df') is not None:
                    insert_from_df(st.session_state['uploaded_df'], table_choice)
                    st.success(f"✅ Inserted into {table_choice}!")
                else:
                    st.error("Please select a target table and upload a valid file.")

    with col2:
        if st.session_state.get('uploaded_df') is not None:
            st.subheader("Preview")
            st.dataframe(st.session_state['uploaded_df'].head(10))
        else:
            st.info("Upload a CSV file to see preview.")


# ------------------ TRAINS ------------------
with tabs[1]:
    st.markdown('<h2 class="section-header">🚉 Manage Trains</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        with st.expander("Add New Train", expanded=True):
            with st.form("train_form"):
                train_number = st.text_input("Train Number")
                description = st.text_input("Description")
                submitted = st.form_submit_button("Insert Train")
                if submitted:
                    if train_number:
                        insert_train(train_number, description)
                        st.success("✅ Train inserted!")
                    else:
                        st.error("Train Number is required.")

    with col2:
        data = fetch_all("trains")
        if data:
            df = pd.DataFrame(data)
            df.rename(columns={"id": "ID", "train_number": "Train Number", "description": "Description"}, inplace=True)
            search = st.text_input("Search Trains", key="train_search")
            if search:
                df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
            st.dataframe(df)
        else:
            st.info("No trains found.")


# ------------------ FITNESS ------------------
with tabs[2]:
    st.markdown('<h2 class="section-header">📝 Fitness Certificates</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        with st.expander("Add Fitness Certificate", expanded=True):
            with st.form("fitness_form"):
                train_id = st.number_input("Train ID", min_value=1)
                status = st.selectbox("Status", ["Valid", "Expired"])
                valid_till = st.date_input("Valid Till")
                issued_by = st.text_input("Issued By")
                submitted = st.form_submit_button("Insert Record")
                if submitted:
                    if train_id and issued_by:
                        insert_record("fitness_certificates", {
                            "train_id": train_id,
                            "certificate_status": status,
                            "valid_till": str(valid_till),
                            "issued_by": issued_by
                        })
                        st.success("✅ Inserted!")
                    else:
                        st.error("Train ID and Issued By are required.")

    with col2:
        data = fetch_all("fitness_certificates")
        if data:
            df = pd.DataFrame(data)
            df.rename(columns={"id": "ID", "train_id": "Train ID", "certificate_status": "Status", "valid_till": "Valid Till", "issued_by": "Issued By"}, inplace=True)
            search = st.text_input("Search Certificates", key="fitness_search")
            if search:
                df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
            st.dataframe(df)
        else:
            st.info("No fitness certificates found.")


# ------------------ JOB CARDS ------------------
with tabs[3]:
    st.markdown('<h2 class="section-header">🛠 Job Cards</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        with st.expander("Add Job Card", expanded=True):
            with st.form("job_form"):
                train_id = st.number_input("Train ID", min_value=1)
                job_card_no = st.text_input("Job Card No")
                status = st.selectbox("Status", ["Open", "Closed"])
                source = st.text_input("Source System", "Maximo")
                submitted = st.form_submit_button("Insert Record")
                if submitted:
                    if train_id and job_card_no:
                        insert_record("job_cards", {
                            "train_id": train_id,
                            "job_card_no": job_card_no,
                            "status": status,
                            "source_system": source
                        })
                        st.success("✅ Inserted!")
                    else:
                        st.error("Train ID and Job Card No are required.")

    with col2:
        data = fetch_all("job_cards")
        if data:
            df = pd.DataFrame(data)
            df.rename(columns={"id": "ID", "train_id": "Train ID", "job_card_no": "Job Card No", "status": "Status", "source_system": "Source"}, inplace=True)
            search = st.text_input("Search Job Cards", key="job_search")
            if search:
                df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
            st.dataframe(df)
        else:
            st.info("No job cards found.")


# ------------------ BRANDING ------------------
with tabs[4]:
    st.markdown('<h2 class="section-header">🎨 Branding Priorities</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        with st.expander("Add Branding Priority", expanded=True):
            with st.form("brand_form"):
                train_id = st.number_input("Train ID", min_value=1)
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                campaign = st.text_input("Campaign Name")
                exposure = st.number_input("Exposure Hours", min_value=0.0, step=1.0)
                submitted = st.form_submit_button("Insert Record")
                if submitted:
                    if train_id and campaign:
                        insert_record("branding_priorities", {
                            "train_id": train_id,
                            "priority_level": priority,
                            "campaign_name": campaign,
                            "exposure_hours": exposure
                        })
                        st.success("✅ Inserted!")
                    else:
                        st.error("Train ID and Campaign Name are required.")

    with col2:
        data = fetch_all("branding_priorities")
        if data:
            df = pd.DataFrame(data)
            df.rename(columns={"id": "ID", "train_id": "Train ID", "priority_level": "Priority", "campaign_name": "Campaign", "exposure_hours": "Exposure Hrs"}, inplace=True)
            search = st.text_input("Search Branding", key="brand_search")
            if search:
                df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
            st.dataframe(df)
        else:
            st.info("No branding priorities found.")


# ------------------ MILEAGE ------------------
with tabs[5]:
    st.markdown('<h2 class="section-header">📏 Mileage Records</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        with st.expander("Add Mileage Record", expanded=True):
            with st.form("mileage_form"):
                train_id = st.number_input("Train ID", min_value=1)
                km = st.number_input("Total KM", min_value=0.0, step=100.0)
                last_updated = st.date_input("Last Updated")
                submitted = st.form_submit_button("Insert Record")
                if submitted:
                    if train_id:
                        insert_record("mileage_records", {
                            "train_id": train_id,
                            "total_km": km,
                            "last_updated": str(last_updated)
                        })
                        st.success("✅ Inserted!")
                    else:
                        st.error("Train ID is required.")

    with col2:
        data = fetch_all("mileage_records")
        if data:
            df = pd.DataFrame(data)
            df.rename(columns={"id": "ID", "train_id": "Train ID", "total_km": "KM", "last_updated": "Last Updated"}, inplace=True)
            search = st.text_input("Search Mileage", key="mileage_search")
            if search:
                df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
            st.dataframe(df)
        else:
            st.info("No mileage records found.")


# ------------------ CLEANING ------------------
with tabs[6]:
    st.markdown('<h2 class="section-header">🧹 Cleaning Slots</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        with st.expander("Add Cleaning Slot", expanded=True):
            with st.form("cleaning_form"):
                train_id = st.number_input("Train ID", min_value=1)
                slot = st.text_input("Slot Name")
                time = st.text_input("Scheduled Time")
                status = st.selectbox("Status", ["Pending", "Done"])
                submitted = st.form_submit_button("Insert Record")
                if submitted:
                    if train_id and slot:
                        insert_record("cleaning_slots", {
                            "train_id": train_id,
                            "slot_name": slot,
                            "scheduled_time": time,
                            "status": status
                        })
                        st.success("✅ Inserted!")
                    else:
                        st.error("Train ID and Slot Name are required.")

    with col2:
        data = fetch_all("cleaning_slots")
        if data:
            df = pd.DataFrame(data)
            df.rename(columns={"id": "ID", "train_id": "Train ID", "slot_name": "Slot", "scheduled_time": "Time", "status": "Status"}, inplace=True)
            search = st.text_input("Search Cleaning Slots", key="cleaning_search")
            if search:
                df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
            st.dataframe(df)
        else:
            st.info("No cleaning slots found.")


# ------------------ DEPOT ------------------
with tabs[7]:
    st.markdown('<h2 class="section-header">🏠 Depot Positions</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        with st.expander("Add Depot Position", expanded=True):
            with st.form("depot_form"):
                train_id = st.number_input("Train ID", min_value=1)
                depot = st.text_input("Depot Name")
                position = st.text_input("Position Code")
                submitted = st.form_submit_button("Insert Record")
                if submitted:
                    if train_id and depot and position:
                        insert_record("depot_positions", {
                            "train_id": train_id,
                            "depot_name": depot,
                            "position_code": position
                        })
                        st.success("✅ Inserted!")
                    else:
                        st.error("Train ID, Depot Name, and Position Code are required.")

    with col2:
        data = fetch_all("depot_positions")
        if data:
            df = pd.DataFrame(data)
            df.rename(columns={"id": "ID", "train_id": "Train ID", "depot_name": "Depot", "position_code": "Position"}, inplace=True)
            search = st.text_input("Search Depot Positions", key="depot_search")
            if search:
                df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
            st.dataframe(df)
        else:
            st.info("No depot positions found.")


# ------------------ DASHBOARD ------------------
with tabs[8]:
    st.markdown('<h2 class="section-header">📊 System Dashboard</h2>', unsafe_allow_html=True)
    st.write("This dashboard provides a comprehensive overview of the Kochi Metro Train Database, including record counts, distributions, and status summaries across all modules.")

    # Key Metrics
    st.subheader("📈 Key Metrics")
    tables = ["trains", "fitness_certificates", "job_cards",
              "branding_priorities", "mileage_records",
              "cleaning_slots", "depot_positions"]
    counts = {}
    for table in tables:
        data = fetch_all(table)
        counts[table] = len(data) if data else 0

    total_records = sum(counts.values())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", total_records)
    with col2:
        st.metric("Trains", counts["trains"])
    with col3:
        st.metric("Fitness Certificates", counts["fitness_certificates"])
    with col4:
        st.metric("Job Cards", counts["job_cards"])

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("Branding Priorities", counts["branding_priorities"])
    with col6:
        st.metric("Mileage Records", counts["mileage_records"])
    with col7:
        st.metric("Cleaning Slots", counts["cleaning_slots"])
    with col8:
        st.metric("Depot Positions", counts["depot_positions"])

    # Data Visualizations
    st.subheader("📊 Data Visualizations")

    # Bar chart
    st.write("**Record Counts by Module**")
    chart_data = pd.DataFrame(list(counts.items()), columns=["Table", "Count"])
    st.bar_chart(chart_data.set_index("Table"))

    # Train Status Overview
    st.subheader("🚆 Train Status Overview")
    trains = fetch_all("trains")
    fitness = fetch_all("fitness_certificates")
    jobs = fetch_all("job_cards")
    cleaning = fetch_all("cleaning_slots")

    statuses = []
    for train in trains:
        train_id = train.get('id', 0)
        train_num = train.get('train_number', f"Train {train_id}")
        issues = []

        # Check fitness
        fit = [f for f in fitness if f['train_id'] == train_id]
        if not fit or any(f['certificate_status'] != 'Valid' or datetime.date.today() > datetime.datetime.strptime(f['valid_till'], '%Y-%m-%d').date() for f in fit):
            issues.append("Invalid/Expired Fitness")

        # Check jobs
        open_jobs = [j for j in jobs if j['train_id'] == train_id and j['status'] != 'Closed']
        if open_jobs:
            issues.append("Open Job Cards")

        # Check cleaning
        pending_clean = [c for c in cleaning if c['train_id'] == train_id and c['status'] != 'Done']
        if pending_clean:
            issues.append("Pending Cleaning")

        status = "Passed Checks" if not issues else "Needs Maintenance"
        statuses.append({"Train Number": train_num, "Status": status, "Issues": "; ".join(issues)})

    df_status = pd.DataFrame(statuses)
    st.dataframe(df_status)

    # Metrics
    passed = len([s for s in statuses if s['Status'] == 'Passed Checks'])
    needs = len(statuses) - passed
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Trains Passed Checks", passed)
    with col2:
        st.metric("Trains Needing Maintenance", needs)


# ------------------ SIMULATION ------------------
with tabs[9]:
    st.markdown('<h2 class="section-header">🔮 What-If Simulation</h2>', unsafe_allow_html=True)
    st.write("Test scenarios for nightly induction plans. Adjust variables to see trade-offs in punctuality, cost, safety, and advertiser obligations.")

    # Scenario Inputs
    st.subheader("Scenario Variables")
    col1, col2 = st.columns(2)
    with col1:
        min_induction_count = st.slider("Minimum Trains to Induct", min_value=1, max_value=50, value=10)
        allow_risky_trains = st.checkbox("Allow Risky Trains (with issues)")
        max_issues_allowed = st.slider("Max Issues Allowed per Train", min_value=0, max_value=5, value=1) if allow_risky_trains else 0
        prioritize_advertiser = st.checkbox("Prioritize Advertiser Campaigns")
    with col2:
        cost_penalty_per_issue = st.slider("Cost Penalty per Issue (₹)", min_value=0, max_value=2000, value=500)
        # Additional variables can be added here

    # Run Simulation
    if st.button("Run Simulation"):
        params = {
            'min_induction_count': min_induction_count,
            'allow_risky_trains': allow_risky_trains,
            'max_issues_allowed': max_issues_allowed,
            'prioritize_advertiser': prioritize_advertiser,
            'cost_penalty_per_issue': cost_penalty_per_issue
        }
        result = run_simulation(params)

        # Display Results
        st.subheader("Simulation Results")
        metrics = result['metrics']
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Punctuality (%)", metrics['punctuality'])
        with col2:
            st.metric("Total Cost (₹)", f"{metrics['cost']:,}")
        with col3:
            st.metric("Safety Score (Avg Issues)", metrics['safety_score'])
        with col4:
            st.metric("Advertiser Exposure (Hrs)", metrics['advertiser_exposure'])

        # Selected Trains
        st.subheader("Selected Trains for Induction")
        selected_df = pd.DataFrame(result['selected_trains'])
        if not selected_df.empty:
            selected_df = selected_df[['train_number', 'status', 'issues', 'issue_count']]
            selected_df.rename(columns={'train_number': 'Train Number', 'status': 'Status', 'issues': 'Issues', 'issue_count': 'Issue Count'}, inplace=True)
            st.dataframe(selected_df)
        else:
            st.info("No trains selected based on criteria.")

        # Metrics Chart
        st.subheader("Metrics Comparison")
        chart_data = pd.DataFrame({
            'Metric': ['Punctuality', 'Cost', 'Safety Score', 'Advertiser Exposure'],
            'Value': [metrics['punctuality'], metrics['cost'], metrics['safety_score'], metrics['advertiser_exposure']]
        })
        st.bar_chart(chart_data.set_index('Metric'))
    else:
        st.info("Adjust parameters and click 'Run Simulation' to see results.")
