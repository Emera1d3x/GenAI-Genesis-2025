import streamlit as st
from google.cloud import firestore
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="frontend.log",
    filemode="a",
)
logger = logging.getLogger(__name__)

# Initialize Firestore client
try:
    db = firestore.Client.from_service_account_json(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    logger.info("Firestore client initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Firestore client: {e}")
    raise

# Streamlit app
st.set_page_config(page_title="SwiftCareAI", page_icon="🏥", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f2f6;
    }
    h1 {
        color: #2e86c1;
    }
    h2 {
        color: #1a5276;
    }
    .stButton button {
        background-color: #2e86c1;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton button:hover {
        background-color: #1a5276;
    }
    .stAlert {
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# App title and description
st.title("🏥 SwiftCareAI")
st.markdown("**Real-time decision support tool for doctors and medical staff.**")

# Fetch patient data from Firestore
def fetch_patients():
    try:
        patients_ref = db.collection("patients")
        patients = patients_ref.stream()
        return [patient.to_dict() for patient in patients]
    except Exception as e:
        logger.error(f"Failed to fetch patients: {e}")
        st.error("Failed to fetch patient data. Please check the logs.")
        return []

# Display prioritized patient list
st.header("📋 Prioritized Patient List")
patients = fetch_patients()

if patients:
    for patient in patients:
        with st.container():
            st.subheader(f"🆔 Patient ID: {patient['patient_id']}")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**🚨 Triage Score:** {patient.get('triage_score', 'N/A')}")
                st.write(f"**🩺 Symptoms:** {', '.join(patient.get('symptoms', []))}")
                st.write(f"**📝 Symptom Summary:** {patient.get('symptom_summary', 'N/A')}")
            with col2:
                st.write(f"**💓 Vitals:** {patient.get('vitals', {})}")
                st.write(f"**🏨 Recommended Hospital:** {patient.get('recommended_hospital', 'N/A')}")
            st.markdown("---")
else:
    st.warning("No patient data found.")

# Real-time alerts
st.header("🚨 Real-Time Alerts")
alerts = [
    {"patient_id": "123", "message": "Heart rate increased to 130 bpm"},
    {"patient_id": "456", "message": "Blood pressure dropped to 90/60"},
]

for alert in alerts:
    st.warning(f"**Alert for Patient {alert['patient_id']}:** {alert['message']}")

# Key metrics
st.header("📊 Key Metrics")
if patients:
    st.write(f"**👥 Total Patients:** {len(patients)}")
    st.write(f"**🔴 High Priority Patients:** {len([p for p in patients if p.get('triage_score', 0) > 0.8])}")
    st.write(f"**🟠 Medium Priority Patients:** {len([p for p in patients if 0.5 < p.get('triage_score', 0) <= 0.8])}")
    st.write(f"**🟢 Low Priority Patients:** {len([p for p in patients if p.get('triage_score', 0) <= 0.5])}")
else:
    st.warning("No metrics available.")

# Footer
st.markdown("---")
st.markdown("**SwiftCareAI** - Built with ❤️ for better healthcare.")