"""
Debug script to test the exact input: cold,cough,headache,fever
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_cluster():
    """Debug the cluster symptom processing"""
    from main import find_matching_symptoms, predict_disease_from_symptoms
    
    # Simulate the exact input from the user
    user_input = "cold,cough,headache,fever"
    
    print(f"User input: {user_input}")
    
    # Split the user's input into a list of symptoms (assuming they are comma-separated)
    user_symptoms = [s.strip() for s in user_input.split(',')]
    print(f"User symptoms: {user_symptoms}")
    
    # Try to find matches for each symptom
    matched_symptoms = []
    for symptom in user_symptoms:
        symptom_matches = find_matching_symptoms(symptom, threshold=0.6)
        matched_symptoms.extend(symptom_matches)
        print(f"Symptom '{symptom}' matched to: {symptom_matches}")
    
    # Remove duplicates while preserving order
    seen = set()
    matched_symptoms = [x for x in matched_symptoms if not (x in seen or seen.add(x))]
    print(f"Final matched symptoms: {matched_symptoms}")
    
    # Predict disease based on matched symptoms
    predicted_disease = predict_disease_from_symptoms(matched_symptoms)
    print(f"Predicted disease: {predicted_disease}")

if __name__ == "__main__":
    debug_cluster()