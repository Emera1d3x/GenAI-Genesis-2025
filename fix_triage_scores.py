import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

def update_triage_scores():
    # Get all patients
    patients_ref = db.collection("patients")
    patients = patients_ref.stream()
    
    for patient in patients:
        data = patient.to_dict()
        symptoms = [s.lower().strip() for s in data.get('symptoms', [])]
        print(f"\nPatient {data.get('patient_id')}:")
        print(f"Symptoms: {symptoms}")
        print(f"Current triage score: {data.get('triage_score')}")
        
        # Check for chest pain
        has_chest_pain = any(s in ['chest pain', 'chest-pain', 'chestpain'] for s in symptoms)
        
        # Update triage score if needed
        new_triage_score = 0.9 if has_chest_pain else 0.5
        if new_triage_score != data.get('triage_score'):
            print(f"Updating triage score to: {new_triage_score}")
            patients_ref.document(patient.id).update({
                'triage_score': new_triage_score
            })
        else:
            print("Triage score is correct")

if __name__ == "__main__":
    update_triage_scores()
    print("\nTriage scores have been updated.")
