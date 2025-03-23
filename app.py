import streamlit as st
from dotenv import load_dotenv
import os
import logging
from backend import TriageFlow, db  # Import db from backend

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

# Initialize TriageFlow
flow = TriageFlow()

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

# Add new patient form
st.header("📝 Add New Patient")
with st.form("new_patient_form"):
    patient_id = st.text_input("Patient ID")
    symptoms = st.text_input("Symptoms (comma-separated)")
    
    # Vitals inputs
    st.subheader("Vitals")
    col1, col2 = st.columns(2)
    with col1:
        blood_pressure = st.text_input("Blood Pressure (e.g., 120/80)")
        heart_rate = st.number_input("Heart Rate (bpm)", min_value=0, max_value=300)
    with col2:
        temperature = st.number_input("Temperature (°C)", min_value=30.0, max_value=45.0, value=37.0)
        oxygen_saturation = st.number_input("Oxygen Saturation (%)", min_value=0, max_value=100, value=98)

    submitted = st.form_submit_button("Submit Patient Data")
    
    if submitted:
        try:
            # Prepare input data
            input_data = {
                "patient_id": patient_id,
                "symptoms": [s.strip() for s in symptoms.split(",")],
                "vitals": {
                    "blood_pressure": blood_pressure,
                    "heart_rate": heart_rate,
                    "temperature": temperature,
                    "oxygen_saturation": oxygen_saturation
                }
            }
            
            # Process through TriageFlow
            result = flow.run(input_data)
            st.success(f"Patient {patient_id} added successfully!")
            logger.info(f"New patient processed: {result}")
        except Exception as e:
            st.error(f"Error processing patient data: {str(e)}")
            logger.error(f"Error processing patient data: {e}")

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
    # Sort patients by triage score (highest first)
    patients.sort(key=lambda x: x.get('triage_score', 0), reverse=True)
    
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

# Key metrics
st.header("📊 Key Metrics")
if patients:
    # Count patients by priority level
    high_priority = sum(1 for p in patients if p.get('triage_score', 0) >= 0.9)
    medium_priority = sum(1 for p in patients if 0.5 < p.get('triage_score', 0) < 0.9)
    low_priority = sum(1 for p in patients if p.get('triage_score', 0) <= 0.5)
    
    st.write(f"**👥 Total Patients:** {len(patients)}")
    st.write(f"**🔴 High Priority Patients:** {high_priority}")
    st.write(f"**🟠 Medium Priority Patients:** {medium_priority}")
    st.write(f"**🟢 Low Priority Patients:** {low_priority}")
else:
    st.warning("No metrics available.")

# Footer
st.markdown("---")
st.markdown("**SwiftCareAI** - Built with ❤️ for better healthcare.")