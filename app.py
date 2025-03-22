import streamlit as st
from google.cloud import firestore
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Firestore client
db = firestore.Client.from_service_account_json(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

# Streamlit app
st.title("Healthcare AI Dashboard")
st.write("Real-time decision support tool for doctors and medical staff.")

# Fetch patient data from Firestore
def fetch_patients():
    patients_ref = db.collection("patients")
    patients = patients_ref.stream()
    return [patient.to_dict() for patient in patients]

# Display prioritized patient list
st.header("Prioritized Patient List")
patients = fetch_patients()
for patient in patients:
    st.subheader(f"Patient ID: {patient['patient_id']}")
    st.write(f"**Triage Score:** {patient.get('triage_score', 'N/A')}")
    st.write(f"**Symptoms:** {', '.join(patient.get('symptoms', []))}")
    st.write(f"**Symptom Summary:** {patient.get('symptom_summary', 'N/A')}")
    st.write(f"**Vitals:** {patient.get('vitals', {})}")
    st.write(f"**Recommended Treatment:** {patient.get('recommended_treatment', 'N/A')}")
    st.write(f"**Recommended Hospital:** {patient.get('recommended_hospital', 'N/A')}")
    st.write("---")

# Real-time alerts
st.header("Real-Time Alerts")
alerts = [
    {"patient_id": "123", "message": "Heart rate increased to 130 bpm"},
    {"patient_id": "456", "message": "Blood pressure dropped to 90/60"},
]
for alert in alerts:
    st.warning(f"**Alert for Patient {alert['patient_id']}:** {alert['message']}")

# Key metrics
st.header("Key Metrics")
st.write("**Total Patients:**", len(patients))
st.write("**High Priority Patients:**", len([p for p in patients if p.get("triage_score", 0) > 0.8]))
st.write("**Medium Priority Patients:**", len([p for p in patients if 0.5 < p.get("triage_score", 0) <= 0.8]))
st.write("**Low Priority Patients:**", len([p for p in patients if p.get("triage_score", 0) <= 0.5]))