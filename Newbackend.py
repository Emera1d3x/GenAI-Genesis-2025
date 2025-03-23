import os
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import cohere
import requests
import numpy as np
from geopy.distance import geodesic

# Load environment variables
load_dotenv()

# Set up logging with more detailed configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("backend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SwiftCareAI")

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

# Initialize Cohere client with error handling and retries
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

def initialize_cohere_client() -> cohere.Client:
    """Initialize Cohere client with retry logic."""
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        logger.error("COHERE_API_KEY not found in environment variables.")
        raise ValueError("COHERE_API_KEY not found in environment variables.")
    
    for attempt in range(MAX_RETRIES):
        try:
            client = cohere.Client(api_key)
            logger.info("Cohere client initialized successfully.")
            return client
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"Attempt {attempt+1} failed to initialize Cohere client: {e}. Retrying...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"Failed to initialize Cohere client after {MAX_RETRIES} attempts: {e}")
                raise

co = initialize_cohere_client()

# Function to find hospitals using OpenStreetMap Overpass API
def find_hospitals(latitude: float, longitude: float, radius: int = 5000) -> Optional[List[Dict[str, Any]]]:
    """
    Find hospitals near a given location using OpenStreetMap Overpass API.
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        radius: Search radius in meters
        
    Returns:
        List of hospitals or None if the request fails
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node["amenity"="hospital"](around:{radius},{latitude},{longitude});
    out body;
    >;
    out skel qt;
    """
    
    try:
        response = requests.get(overpass_url, params={"data": query}, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        data = response.json()
        logger.info(f"Successfully fetched {len(data.get('elements', []))} hospitals from OpenStreetMap.")
        
        # Process the raw data into a more usable format
        hospitals = []
        for element in data.get("elements", []):
            if "tags" in element:
                hospital = {
                    "id": element.get("id"),
                    "name": element["tags"].get("name", "Unknown Hospital"),
                    "latitude": element.get("lat"),
                    "longitude": element.get("lon"),
                    "specialty": element["tags"].get("healthcare:speciality", "General"),
                    "emergency": element["tags"].get("emergency", "no"),
                    "capacity": np.random.randint(30, 95)  # Simulated capacity for demo
                }
                
                # Calculate distance from patient
                if hospital["latitude"] and hospital["longitude"]:
                    hospital_coords = (hospital["latitude"], hospital["longitude"])
                    patient_coords = (latitude, longitude)
                    distance = geodesic(patient_coords, hospital_coords).kilometers
                    hospital["distance"] = round(distance, 2)
                
                hospitals.append(hospital)
        
        # Sort hospitals by distance
        hospitals.sort(key=lambda x: x.get("distance", float("inf")))
        
        return hospitals
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch hospitals from OpenStreetMap: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse hospital data: {e}")
        return None

class BaseNode:
    """Base class for all processing nodes."""
    
    def __init__(self, name: str):
        self.name = name
        logger.info(f"Initialized {name} node")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return the result."""
        raise NotImplementedError("Subclasses must implement the process method")
    
    def log_processing(self, input_data: Dict[str, Any], output_data: Dict[str, Any]):
        """Log the processing step with input and output data."""
        logger.info(f"{self.name} processed data: patient_id={input_data.get('patient_id', 'unknown')}")

class DataIngestionNode(BaseNode):
    """Node for ingesting and validating patient data."""
    
    def __init__(self):
        super().__init__("DataIngestion")
    
    def validate_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate the input data."""
        required_fields = ["patient_id", "symptoms"]
        
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        return True, "Data is valid"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and store patient data."""
        try:
            # Validate data
            valid, message = self.validate_data(input_data)
            if not valid:
                logger.error(f"Data validation failed: {message}")
                raise ValueError(message)
            
            # Add timestamp
            input_data["timestamp"] = firestore.SERVER_TIMESTAMP
            
            # Save patient data to Firestore
            doc_ref = db.collection("patients").document(input_data["patient_id"])
            doc_ref.set(input_data, merge=True)
            
            logger.info(f"Patient data saved successfully: patient_id={input_data['patient_id']}")
            self.log_processing(input_data, input_data)
            
            return input_data
        except Exception as e:
            logger.error(f"Failed to save patient data: {e}")
            raise

class PreprocessingNode(BaseNode):
    """Node for cleaning and preprocessing patient data."""
    
    def __init__(self):
        super().__init__("Preprocessing")
    
    def normalize_vitals(self, vitals: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize vital signs to standard units."""
        normalized = {}
        
        for key, value in vitals.items():
            if key == "blood_pressure" and isinstance(value, str):
                # Convert string BP (e.g., "120/80") to systolic and diastolic values
                try:
                    systolic, diastolic = map(int, value.split("/"))
                    normalized["systolic_bp"] = systolic
                    normalized["diastolic_bp"] = diastolic
                except ValueError:
                    normalized[key] = value
            elif key == "temperature" and isinstance(value, (int, float)):
                # Ensure temperature is in Celsius
                if value > 50:  # Likely Fahrenheit
                    normalized[key] = round((value - 32) * 5/9, 1)
                else:
                    normalized[key] = value
            else:
                normalized[key] = value
        
        return normalized
    
    def categorize_symptoms(self, symptoms: List[str]) -> Dict[str, List[str]]:
        """Categorize symptoms by severity."""
        severe_symptoms = [
            "chest pain", "difficulty breathing", "shortness of breath", 
            "severe bleeding", "unconscious", "unresponsive", "seizure"
        ]
        
        moderate_symptoms = [
            "fever", "vomiting", "dizziness", "moderate pain", 
            "headache", "abdominal pain", "dehydration"
        ]
        
        categorized = {
            "severe": [s for s in symptoms if any(severe in s.lower() for severe in severe_symptoms)],
            "moderate": [s for s in symptoms if any(moderate in s.lower() for moderate in moderate_symptoms)],
            "mild": [s for s in symptoms if not any(severe in s.lower() for severe in severe_symptoms) and 
                                          not any(moderate in s.lower() for moderate in moderate_symptoms)]
        }
        
        return categorized
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess the patient data."""
        try:
            output_data = input_data.copy()
            
            # Normalize vital signs if present
            if "vitals" in output_data:
                output_data["vitals"] = self.normalize_vitals(output_data["vitals"])
            
            # Categorize symptoms by severity
            if "symptoms" in output_data:
                output_data["symptom_categories"] = self