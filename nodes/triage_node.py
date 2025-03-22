class TriageNode:
    def process(self, input_data):
        # Assign a triage score based on symptoms and vitals
        symptoms = input_data.get("symptoms", [])
        if "chest pain" in symptoms:
            return {"triage_score": 0.9}  # High priority
        return {"triage_score": 0.5}  # Medium priority