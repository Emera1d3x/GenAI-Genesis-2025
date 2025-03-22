from google.cloud import firestore

class DataIngestionNode:
    def __init__(self):
        self.db = firestore.Client()

    def process(self, input_data):
        # Save patient data to Firestore
        doc_ref = self.db.collection("patients").document(input_data["patient_id"])
        doc_ref.set(input_data)
        return input_data