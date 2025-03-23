import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import cohere
import googlemaps

# Load environment variables
load_dotenv()

# Initialize Firebase
cred = credentials.Certificate("C:/Users/POLSTORE/GenAI-Genesis-2025/firebase-key.json")  # Download this from Firebase Console
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

# Initialize Cohere client
co = cohere.Client(os.getenv("COHERE_API_KEY"))

# Initialize Google Maps client
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

class DataIngestionNode:
    def process(self, input_data):
        # Save patient data to Firestore
        doc_ref = db.collection("patients").document(input_data["patient_id"])
        doc_ref.set(input_data)
        return input_data

class TriageNode:
    def process(self, input_data):
        # Use Cohere to analyze symptoms
        symptoms = input_data.get("symptoms", [])
        response = co.generate(
            prompt=f"Summarize and prioritize these symptoms: {', '.join(symptoms)}.",
            max_tokens=50
        )
        summary = response.generations[0].text

        # Assign a triage score (mock logic)
        if "chest pain" in symptoms:
            triage_score = 0.9  # High priority
        else:
            triage_score = 0.5  # Medium priority

        return {"triage_score": triage_score, "symptom_summary": summary}

class ResourceAllocationNode:
    def process(self, input_data):
        # Mock patient location (latitude, longitude)
        patient_location = (37.7749, -122.4194)  # San Francisco

        # Find the nearest hospital using Google Maps API
        hospitals = gmaps.places_nearby(
            location=patient_location,
            radius=5000,  # 5 km radius
            type="hospital"
        )

        # Recommend the nearest hospital
        if hospitals.get("results"):
            recommended_hospital = hospitals["results"][0]["name"]
        else:
            recommended_hospital = "No hospital found"

        return {"recommended_hospital": recommended_hospital}

class TriageFlow:
    def __init__(self):
        self.data_ingestion_node = DataIngestionNode()
        self.triage_node = TriageNode()
        self.resource_allocation_node = ResourceAllocationNode()

    def run(self, input_data):
        # Step 1: Ingest data
        processed_data = self.data_ingestion_node.process(input_data)
        # Step 2: Assign triage score
        triage_result = self.triage_node.process(processed_data)
        # Step 3: Allocate resources
        allocation_result = self.resource_allocation_node.process(triage_result)
        return {**processed_data, **triage_result, **allocation_result}

# Example usage
if __name__ == "__main__":
    flow = TriageFlow()
    input_data = {
        "patient_id": "123",
        "symptoms": ["chest pain", "shortness of breath"],
        "vitals": {"blood_pressure": 120, "heart_rate": 90}
    }
    result = flow.run(input_data)
    print(result)