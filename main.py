from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the path to the Google key file
google_key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
print("Google Key Path:", google_key_path)

from google.cloud import firestore

# Initialize Firestore client
db = firestore.Client()

# Example: Add a document to Firestore
doc_ref = db.collection("patients").document("patient-123")
doc_ref.set({
    "name": "John Doe",
    "age": 30,
    "symptoms": ["chest pain", "shortness of breath"]
})

print("Document added successfully!")

#scr/main.py code
from flows.triage_flow import TriageFlow

if __name__ == "__main__":
    flow = TriageFlow()
    input_data = {
        "patient_id": "123",
        "symptoms": ["chest pain", "shortness of breath"],
        "vitals": {"blood_pressure": 120, "heart_rate": 90}
    }
    result = flow.run(input_data)
    print(result)