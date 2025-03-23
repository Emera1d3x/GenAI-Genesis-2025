from google.cloud import firestore
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firestore client
db = firestore.Client.from_service_account_json(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

# Sample patient data
sample_patients = [
    {
        "patient_id": "P001",
        "triage_score": 0.9,
        "symptoms": ["Chest Pain", "Shortness of Breath", "Sweating"],
        "symptom_summary": "Severe chest pain with breathing difficulty",
        "vitals": {
            "heart_rate": 110,
            "blood_pressure": "140/90",
            "temperature": 37.8,
            "oxygen_saturation": 94
        },
        "recommended_hospital": "City General Hospital"
    },
    {
        "patient_id": "P002",
        "triage_score": 0.6,
        "symptoms": ["Headache", "Dizziness", "Nausea"],
        "symptom_summary": "Moderate headache with vertigo",
        "vitals": {
            "heart_rate": 85,
            "blood_pressure": "125/82",
            "temperature": 37.2,
            "oxygen_saturation": 98
        },
        "recommended_hospital": "Community Medical Center"
    }
]

# Add sample data to Firestore
for patient in sample_patients:
    doc_ref = db.collection("patients").document(patient["patient_id"])
    doc_ref.set(patient)
    print(f"Added patient {patient['patient_id']} to Firestore")
