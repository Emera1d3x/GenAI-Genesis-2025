import os
import logging
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import cohere
import requests

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,  # Log level (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    filename="backend.log",  # Log file
    filemode="a",  # Append mode
)
logger = logging.getLogger(__name__)

# Initialize Firebase
try:
    cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    firebase_admin.initialize_app(cred)
    logger.info("Firebase initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {e}")
    raise

# Initialize Firestore client
db = firestore.client()

# Initialize Cohere client
try:
    co = cohere.Client(os.getenv("COHERE_API_KEY"))
    logger.info("Cohere client initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Cohere client: {e}")
    raise

# Function to find hospitals using OpenStreetMap Overpass API
def find_hospitals(latitude, longitude, radius=5000):
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node["amenity"="hospital"](around:{radius},{latitude},{longitude});
    out body;
    >;
    out skel qt;
    """
    try:
        response = requests.get(overpass_url, params={"data": query})
        response.raise_for_status()  # Raise an exception for HTTP errors
        logger.info("Successfully fetched hospitals from OpenStreetMap.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch hospitals from OpenStreetMap: {e}")
        return None

class DataIngestionNode:
    def process(self, input_data):
        try:
            # Save patient data to Firestore
            doc_ref = db.collection("patients").document(input_data["patient_id"])
            doc_ref.set(input_data)
            logger.info(f"Patient data saved successfully: {input_data}")
            return input_data
        except Exception as e:
            logger.error(f"Failed to save patient data: {e}")
            raise

class TriageNode:
    def process(self, input_data):
        try:
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

            logger.info(f"Triage score assigned: {triage_score}")
            return {"triage_score": triage_score, "symptom_summary": summary}
        except Exception as e:
            logger.error(f"Failed to assign triage score: {e}")
            raise

class ResourceAllocationNode:
    def process(self, input_data):
        try:
            # Mock patient location (latitude, longitude)
            patient_location = (37.7749, -122.4194)  # San Francisco

            # Find the nearest hospital using OpenStreetMap
            hospitals = find_hospitals(*patient_location)
            if hospitals and "elements" in hospitals:
                recommended_hospital = hospitals["elements"][0]["tags"].get("name", "No hospital found")
            else:
                recommended_hospital = "No hospital found"

            logger.info(f"Recommended hospital: {recommended_hospital}")
            return {"recommended_hospital": recommended_hospital}
        except Exception as e:
            logger.error(f"Failed to allocate resources: {e}")
            raise

class TriageFlow:
    def __init__(self):
        self.data_ingestion_node = DataIngestionNode()
        self.triage_node = TriageNode()
        self.resource_allocation_node = ResourceAllocationNode()

    def run(self, input_data):
        try:
            # Step 1: Ingest data
            processed_data = self.data_ingestion_node.process(input_data)
            # Step 2: Assign triage score
            triage_result = self.triage_node.process(processed_data)
            # Step 3: Allocate resources
            allocation_result = self.resource_allocation_node.process(triage_result)
            logger.info("Triage flow completed successfully.")
            return {**processed_data, **triage_result, **allocation_result}
        except Exception as e:
            logger.error(f"Triage flow failed: {e}")
            raise

# Example usage
if __name__ == "__main__":
    try:
        flow = TriageFlow()
        input_data = {
            "patient_id": "123",
            "symptoms": ["chest pain", "shortness of breath"],
            "vitals": {"blood_pressure": 120, "heart_rate": 90}
        }
        result = flow.run(input_data)
        print(result)
    except Exception as e:
        logger.critical(f"Application failed: {e}")