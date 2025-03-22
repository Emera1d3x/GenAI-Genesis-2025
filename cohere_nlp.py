import cohere
from dotenv import load_dotenv
import os
from nodes.triage_node import TriageNode

# Load environment variables from .env file
load_dotenv()

YOUR_API_KEY = os.getenv("YOUR_API_KEY")

class CohereTriageNode(TriageNode):
    def __init__(self):
        super().__init__()
        self.client = cohere.Client(YOUR_API_KEY)
    
    def process(self, input_data):
        # First use the base TriageNode logic for critical cases
        base_result = super().process(input_data)
        if base_result["triage_score"] > 0.5:  # If base triage considers it high priority
            return base_result
            
        # For other cases, use Cohere API
        symptoms = input_data.get("symptoms", [])
        symptoms_text = ", ".join(symptoms)
        response = self.client.generate(
            model="command",
            prompt=f"""You are a medical symptom analyzer. Given the symptoms, return ONLY a single number between 0 and 1 representing the urgency (1 = critical, 0 = non-urgent).
Do not include any other text, explanation, or punctuation in your response.

Symptoms: {symptoms_text}""",
            max_tokens=100,
            temperature=0.3
        )
        
        score = float(response.generations[0].text.strip())
        return {"triage_score": score}
 

if __name__ == "__main__":
    # Test the triage node
    triage = CohereTriageNode()
    test_cases = [
        {"symptoms": ["chest pain", "shortness of breath"]},
        {"symptoms": ["headache", "fever"]},
        {"symptoms": ["nausea", "dizziness"]}
    ]
    
    for case in test_cases:
        result = triage.process(case)
        print(f"Symptoms: {case['symptoms']}")
        print(f"Triage Score: {result['triage_score']}\n")
