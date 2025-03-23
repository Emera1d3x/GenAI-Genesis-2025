import streamlit as st
from google.cloud import firestore
from dotenv import load_dotenv
import os
import logging
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

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
    st.error("Failed to initialize Firestore. Please check the logs.")
    raise

# Streamlit app configuration
st.set_page_config(
    page_title="SwiftCareAI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stButton button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #2980b9;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .patient-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .high-priority {
        border-left: 5px solid #e74c3c;
    }
    .medium-priority {
        border-left: 5px solid #f39c12;
    }
    .low-priority {
        border-left: 5px solid #2ecc71;
    }
    .metric-container {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
    }
    .alert-card {
        background-color: #ffebee;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 4px solid #e74c3c;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.image("https://i.imgur.com/zzGhxJf.png", width=100)  # Placeholder for logo
    st.title("SwiftCareAI")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["Dashboard", "Patient Details", "Analytics", "Settings"],
        index=0
    )
    
    st.markdown("---")
    
    # User info
    st.markdown("**Logged in as:**")
    st.markdown("Dr. Sarah Johnson")
    st.markdown("Field Hospital #42")
    
    st.markdown("---")
    # Quick filters
    st.subheader("Quick Filters")
    priority_filter = st.multiselect(
        "Priority Level",
        ["High", "Medium", "Low"],
        default=["High", "Medium", "Low"]
    )
    
    st.markdown("---")
    st.markdown("v1.0.0 - SwiftCareAI")
    st.markdown("[Documentation](https://github.com/yourusername/SwiftCareAI)")
    
    # Auto refresh toggle
    auto_refresh = st.checkbox("Auto-refresh data", value=True)
    if auto_refresh:
        refresh_interval = st.slider("Refresh interval (seconds)", 30, 300, 60)

# Fetch patient data from Firestore
def fetch_patients():
    try:
        patients_ref = db.collection("patients")
        patients = patients_ref.stream()
        patient_list = [patient.to_dict() for patient in patients]
        
        # Sort by triage score
        patient_list.sort(key=lambda x: x.get('triage_score', 0), reverse=True)
        
        logger.info(f"Successfully fetched {len(patient_list)} patients")
        return patient_list
    except Exception as e:
        logger.error(f"Failed to fetch patients: {e}")
        st.error("Failed to fetch patient data. Please check the logs.")
        return []

# Fetch hospital data from Firestore
def fetch_hospitals():
    try:
        hospitals_ref = db.collection("hospitals")
        hospitals = hospitals_ref.stream()
        return [hospital.to_dict() for hospital in hospitals]
    except Exception as e:
        logger.error(f"Failed to fetch hospitals: {e}")
        st.error("Failed to fetch hospital data. Please check the logs.")
        return []

# Fetch alert data from Firestore
def fetch_alerts():
    try:
        alerts_ref = db.collection("alerts").order_by("timestamp", direction="DESCENDING").limit(5)
        alerts = alerts_ref.stream()
        return [alert.to_dict() for alert in alerts]
    except Exception as e:
        logger.error(f"Failed to fetch alerts: {e}")
        st.error("Failed to fetch alert data. Please check the logs.")
        return []

# Convert triage score to priority level
def get_priority_level(score):
    if score > 0.8:
        return "High"
    elif score > 0.5:
        return "Medium"
    else:
        return "Low"

# Main Dashboard Page
if page == "Dashboard":
    # Header
    st.title("📊 SwiftCareAI Dashboard")
    st.markdown("Real-time decision support for medical professionals in high-pressure environments")
    
    # Auto-refresh functionality
    if auto_refresh:
        placeholder = st.empty()
        with placeholder.container():
            st.info(f"Data auto-refreshes every {refresh_interval} seconds. Last updated: {datetime.now().strftime('%H:%M:%S')}")
    
    # Key metrics row
    patients = fetch_patients()
    hospitals = fetch_hospitals()
    alerts = fetch_alerts()
    
    if patients:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-container">
                <p>Total Patients</p>
                <p class="metric-value">%d</p>
            </div>
            """ % len(patients), unsafe_allow_html=True)
        
        high_priority = len([p for p in patients if p.get('triage_score', 0) > 0.8])
        with col2:
            st.markdown("""
            <div class="metric-container" style="border-left: 4px solid #e74c3c;">
                <p>High Priority</p>
                <p class="metric-value" style="color: #e74c3c;">%d</p>
            </div>
            """ % high_priority, unsafe_allow_html=True)
        
        medium_priority = len([p for p in patients if 0.5 < p.get('triage_score', 0) <= 0.8])
        with col3:
            st.markdown("""
            <div class="metric-container" style="border-left: 4px solid #f39c12;">
                <p>Medium Priority</p>
                <p class="metric-value" style="color: #f39c12;">%d</p>
            </div>
            """ % medium_priority, unsafe_allow_html=True)
        
        low_priority = len([p for p in patients if p.get('triage_score', 0) <= 0.5])
        with col4:
            st.markdown("""
            <div class="metric-container" style="border-left: 4px solid #2ecc71;">
                <p>Low Priority</p>
                <p class="metric-value" style="color: #2ecc71;">%d</p>
            </div>
            """ % low_priority, unsafe_allow_html=True)
    
    # Split screen - Left: Patient List, Right: Alerts & Hospital Status
    col_left, col_right = st.columns([2, 1])
    
    # Left Column - Patient List
    with col_left:
        st.markdown("### 🚑 Prioritized Patient List")
        
        if patients:
            # Filter patients based on sidebar selection
            filtered_patients = [
                p for p in patients if get_priority_level(p.get('triage_score', 0)) in priority_filter
            ]
            
            for patient in filtered_patients:
                triage_score = patient.get('triage_score', 0)
                priority_level = get_priority_level(triage_score)
                priority_class = ""
                
                if priority_level == "High":
                    priority_class = "high-priority"
                elif priority_level == "Medium":
                    priority_class = "medium-priority"
                else:
                    priority_class = "low-priority"
                
                st.markdown(f"""
                <div class="patient-card {priority_class}">
                    <h3>🆔 Patient ID: {patient.get('patient_id', 'Unknown')}</h3>
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <p><strong>Triage Score:</strong> {triage_score:.2f} ({priority_level} Priority)</p>
                            <p><strong>🩺 Symptoms:</strong> {', '.join(patient.get('symptoms', []))}</p>
                            <p><strong>Summary:</strong> {patient.get('symptom_summary', 'N/A')}</p>
                        </div>
                        <div>
                            <p><strong>Vitals:</strong> {', '.join([f"{k}: {v}" for k, v in patient.get('vitals', {}).items()])}</p>
                            <p><strong>🏥 Recommended:</strong> {patient.get('recommended_hospital', 'N/A')}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No patient data found.")
    
    # Right Column - Alerts & Hospital Status
    with col_right:
        # Alerts Section
        st.markdown("### ⚠️ Real-Time Alerts")
        
        if alerts:
            for alert in alerts:
                st.markdown(f"""
                <div class="alert-card">
                    <p><strong>Patient {alert.get('patient_id', 'Unknown')}</strong></p>
                    <p>{alert.get('message', 'No message')}</p>
                    <small>{alert.get('timestamp', 'Unknown time')}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No active alerts at this time.")
        
        # Hospital Status
        st.markdown("### 🏥 Hospital Status")
        
        if hospitals:
            for hospital in hospitals:
                capacity = hospital.get('capacity', 0)
                capacity_color = "#2ecc71"  # Green for good capacity
                
                if capacity > 80:
                    capacity_color = "#e74c3c"  # Red for almost full
                elif capacity > 60:
                    capacity_color = "#f39c12"  # Orange for getting full
                
                st.markdown(f"""
                <div style="background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <h4>{hospital.get('name', 'Unknown Hospital')}</h4>
                    <p>Capacity: <span style="color: {capacity_color};">{capacity}%</span></p>
                    <p>Distance: {hospital.get('distance', 'Unknown')} km</p>
                    <p>Specialty: {hospital.get('specialty', 'General')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hospital data available.")
    
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(refresh_interval)
        st.experimental_rerun()

# Patient Details Page
elif page == "Patient Details":
    st.title("👤 Patient Details")
    
    # Patient search
    patient_id = st.text_input("Enter Patient ID to view details:")
    
    if patient_id:
        try:
            patient_doc = db.collection("patients").document(patient_id).get()
            
            if patient_doc.exists:
                patient = patient_doc.to_dict()
                
                # Tabs for different sections of patient info
                tabs = st.tabs(["Overview", "Medical History", "Treatment Plan", "Notes"])
                
                with tabs[0]:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Patient Information")
                        st.write(f"**Patient ID:** {patient.get('patient_id', 'Unknown')}")
                        st.write(f"**Age:** {patient.get('age', 'Unknown')}")
                        st.write(f"**Gender:** {patient.get('gender', 'Unknown')}")
                        
                        st.subheader("Current Symptoms")
                        st.write(", ".join(patient.get('symptoms', [])))
                        st.write(f"**Symptom Summary:** {patient.get('symptom_summary', 'N/A')}")
                    
                    with col2:
                        st.subheader("Vital Signs")
                        vitals = patient.get('vitals', {})
                        for key, value in vitals.items():
                            st.write(f"**{key}:** {value}")
                        
                        st.subheader("Triage Information")
                        triage_score = patient.get('triage_score', 0)
                        st.write(f"**Triage Score:** {triage_score:.2f}")
                        st.write(f"**Priority Level:** {get_priority_level(triage_score)}")
                        st.write(f"**Recommended Hospital:** {patient.get('recommended_hospital', 'N/A')}")
                
                with tabs[1]:
                    st.subheader("Medical History")
                    # Placeholder for medical history
                    st.info("Medical history would be displayed here in a real application.")
                    
                    # Sample medical history chart
                    history_data = {
                        'Date': ['2023-01', '2023-04', '2023-07', '2023-10', '2024-01'],
                        'Blood Pressure': [120, 125, 130, 128, 122]
                    }
                    history_df = pd.DataFrame(history_data)
                    st.line_chart(history_df.set_index('Date'))
                
                with tabs[2]:
                    st.subheader("Treatment Plan")
                    st.info("Treatment plan would be displayed here in a real application.")
                    
                    # Sample treatment steps
                    st.write("1. Initial assessment and stabilization")
                    st.write("2. Diagnostic tests (blood work, imaging)")
                    st.write("3. Treatment administration")
                    st.write("4. Monitoring and reassessment")
                    st.write("5. Transfer to specialized care facility if needed")
                
                with tabs[3]:
                    st.subheader("Notes")
                    notes = st.text_area("Add notes about this patient:", height=200)
                    if st.button("Save Notes"):
                        st.success("Notes saved successfully (simulated)")
                
            else:
                st.error(f"No patient found with ID: {patient_id}")
                
        except Exception as e:
            logger.error(f"Error retrieving patient details: {e}")
            st.error("Error retrieving patient details. Please check the logs.")

# Analytics Page
elif page == "Analytics":
    st.title("📈 Analytics Dashboard")
    
    patients = fetch_patients()
    
    if patients:
        # Priority Distribution
        st.subheader("Patient Priority Distribution")
        priority_counts = {
            "High": len([p for p in patients if p.get('triage_score', 0) > 0.8]),
            "Medium": len([p for p in patients if 0.5 < p.get('triage_score', 0) <= 0.8]),
            "Low": len([p for p in patients if p.get('triage_score', 0) <= 0.5])
        }
        
        priority_df = pd.DataFrame({
            'Priority': list(priority_counts.keys()),
            'Count': list(priority_counts.values())
        })
        
        fig = px.pie(priority_df, values='Count', names='Priority', 
                    color='Priority',
                    color_discrete_map={'High': '#e74c3c', 'Medium': '#f39c12', 'Low': '#2ecc71'},
                    title='Patient Distribution by Priority')
        st.plotly_chart(fig)
        
        # Symptom Distribution
        st.subheader("Common Symptoms")
        all_symptoms = []
        for patient in patients:
            all_symptoms.extend(patient.get('symptoms', []))
        
        symptom_counts = {}
        for symptom in all_symptoms:
            if symptom in symptom_counts:
                symptom_counts[symptom] += 1
            else:
                symptom_counts[symptom] = 1
        
        symptom_df = pd.DataFrame({
            'Symptom': list(symptom_counts.keys()),
            'Count': list(symptom_counts.values())
        }).sort_values('Count', ascending=False).head(10)
        
        fig = px.bar(symptom_df, x='Symptom', y='Count', title='Top 10 Common Symptoms')
        st.plotly_chart(fig)
        
        # Hospital Recommendations
        st.subheader("Hospital Recommendations")
        hospital_counts = {}
        for patient in patients:
            hospital = patient.get('recommended_hospital', 'Unknown')
            if hospital in hospital_counts:
                hospital_counts[hospital] += 1
            else:
                hospital_counts[hospital] = 1
        
        hospital_df = pd.DataFrame({
            'Hospital': list(hospital_counts.keys()),
            'Count': list(hospital_counts.values())
        }).sort_values('Count', ascending=False)
        
        fig = px.bar(hospital_df, x='Hospital', y='Count', title='Patient Distribution by Hospital')
        st.plotly_chart(fig)
    else:
        st.warning("No patient data available for analytics.")

# Settings Page
elif page == "Settings":
    st.title("⚙️ Settings")
    
    st.subheader("Application Settings")
    
    # Display Preferences
    st.markdown("### Display Preferences")
    st.checkbox("Dark Mode", value=False)
    st.checkbox("Enable Notifications", value=True)
    
    # Data Refresh Settings
    st.markdown("### Data Refresh Settings")
    st.slider("Data Refresh Interval (seconds)", 10, 300, 60)
    
    # Triage Settings
    st.markdown("### Triage Settings")
    st.slider("High Priority Threshold", 0.7, 0.95, 0.8)
    st.slider("Medium Priority Threshold", 0.3, 0.7, 0.5)
    
    # Hospital Settings
    st.markdown("### Hospital Settings")
    hospital_search_radius = st.slider("Hospital Search Radius (km)", 5, 50, 20)
    
    # Save Settings
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")
        
    # System Information
    st.markdown("### System Information")
    st.info("SwiftCareAI Version: 1.0.0")
    st.info("Last Updated: March 23, 2025")
    st.info("Backend Status: Online")
    st.info("Database Status: Connected")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #7f8c8d; font-size: 0.8em;">
        <p>SwiftCareAI - Built with ❤️ for better healthcare. © 2025</p>
    </div>
    """,
    unsafe_allow_html=True
)