import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Drone Operations Coordinator",
    layout="wide"
)

# ---------- GOOGLE SHEETS CONNECTION (CLOUD SAFE) ----------

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from Streamlit Secrets
creds_dict = st.secrets["gcp_service_account"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    creds_dict, scope
)

client = gspread.authorize(creds)

# 🔥 Replace with your Spreadsheet ID
SPREADSHEET_ID = "YOUR_SPREADSHEET_ID_HERE"

sheet = client.open_by_key(SPREADSHEET_ID)

pilot_sheet = sheet.worksheet("pilot_roster")
drone_sheet = sheet.worksheet("drone_fleet")
mission_sheet = sheet.worksheet("missions")

pilots = pd.DataFrame(pilot_sheet.get_all_records())
drones = pd.DataFrame(drone_sheet.get_all_records())
missions = pd.DataFrame(mission_sheet.get_all_records())

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

st.sidebar.title("Drone Operations System")

section = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Pilot Management", "Drone Inventory",
     "Mission Assignment", "Urgent Reassignment"]
)

# =====================================================
# DASHBOARD
# =====================================================

if section == "Dashboard":

    st.title("Drone Operations Coordinator")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Pilots", len(pilots))
    col2.metric("Total Drones", len(drones))
    col3.metric("Active Missions", len(missions))

# =====================================================
# PILOT MANAGEMENT
# =====================================================

elif section == "Pilot Management":

    st.title("Pilot Management")

    st.subheader("Pilot Roster")
    st.dataframe(pilots)

    st.subheader("Search Available Pilots")

    col1, col2 = st.columns(2)
    skill = col1.text_input("Required Skill")
    location = col2.text_input("Location")

    if st.button("Search Pilots"):

        with st.spinner("Processing request..."):
            time.sleep(1)

            filtered = pilots[pilots["status"] == "Available"]

            if skill:
                filtered = filtered[
                    filtered["skills"].str.contains(skill, case=False)
                ]

            if location:
                filtered = filtered[
                    filtered["location"].str.contains(location, case=False)
                ]

            st.dataframe(filtered)

    st.subheader("Update Pilot Status")

    name = st.text_input("Pilot Name")
    status = st.selectbox(
        "New Status",
        ["Available", "Assigned", "On Leave", "Unavailable"]
    )

    if st.button("Update Status"):

        with st.spinner("Updating status..."):
            time.sleep(1)

            try:
                cell = pilot_sheet.find(name)
                pilot_sheet.update_cell(cell.row, 6, status)
                st.success("Status updated successfully.")
            except:
                st.error("Pilot not found.")

# =====================================================
# DRONE INVENTORY
# =====================================================

elif section == "Drone Inventory":

    st.title("Drone Inventory")

    st.dataframe(drones)

    st.subheader("Available Drones")

    available = drones[drones["status"] == "Available"]
    st.dataframe(available)

    st.subheader("Maintenance Alerts")

    maintenance = drones[drones["status"] == "Maintenance"]

    if maintenance.empty:
        st.success("No drones currently in maintenance.")
    else:
        st.warning("Maintenance issues detected.")
        st.dataframe(maintenance)

# =====================================================
# MISSION ASSIGNMENT
# =====================================================

elif section == "Mission Assignment":

    st.title("Mission Assignment")

    mission_id = st.text_input("Mission ID")

    if st.button("Recommend Assignment"):

        with st.spinner("Analyzing mission requirements..."):
            time.sleep(1)

            mission = missions[missions["project_id"] == mission_id]

            if not mission.empty:

                mission = mission.iloc[0]

                available_pilots = pilots[pilots["status"] == "Available"]

                matched_pilots = available_pilots[
                    available_pilots["skills"].str.contains(
                        mission["required_skills"], case=False)
                ]

                available_drones = drones[drones["status"] == "Available"]

                st.subheader("Recommended Pilots")
                st.dataframe(matched_pilots)

                st.subheader("Available Drones")
                st.dataframe(available_drones)

            else:
                st.warning("Mission not found.")

# =====================================================
# URGENT REASSIGNMENT
# =====================================================

elif section == "Urgent Reassignment":

    st.title("Urgent Reassignment")

    project = st.text_input("Project ID")

    if st.button("Find Replacement"):

        with st.spinner("Searching for available resources..."):
            time.sleep(1)

            available_pilots = pilots[pilots["status"] == "Available"]
            available_drones = drones[drones["status"] == "Available"]

            if available_pilots.empty:
                st.error("No pilots available.")

            elif available_drones.empty:
                st.error("No drones available.")

            else:
                st.subheader("Replacement Pilot")
                st.dataframe(available_pilots.head(1))

                st.subheader("Replacement Drone")
                st.dataframe(available_drones.head(1))