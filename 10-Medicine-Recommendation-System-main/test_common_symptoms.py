import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Import the main module functions
from main import find_matching_symptoms, predict_disease_from_symptoms, helper, get_doctor_recommendation

def test_common_symptoms():
    """Test the system with common symptoms"""
    print("=== Testing Common Symptoms Prediction ===\n")
    
    # Test cases for common symptoms
    test_cases = [
        "fever",
        "cold",
        "cough",
        "headache",
        "fever, cough",
        "fever, headache",
        "cold, cough",
        "fever, cold, cough",
        "headache, fever",
        "high fever"
    ]
    
    for symptoms_input in test_cases:
        print(f"Input Symptoms: {symptoms_input}")
        
        # Find matching symptoms
        matched_symptoms = find_matching_symptoms(symptoms_input, threshold=0.6)
        print(f"Matched Symptoms: {matched_symptoms}")
        
        # Predict disease
        predicted_disease = predict_disease_from_symptoms(matched_symptoms)
        print(f"Predicted Disease: {predicted_disease}")
        
        if predicted_disease:
            # Get detailed information
            desc, precautions, medications, diets, workouts = helper(predicted_disease)
            doctor = get_doctor_recommendation(predicted_disease)
            
            print(f"Description: {desc}")
            print(f"Precautions: {precautions}")
            print(f"Medications: {medications}")
            print(f"Diets: {diets}")
            print(f"Workouts: {workouts[:3]}...")  # Show first 3
            print(f"Doctor Recommendation: {doctor}")
        else:
            print("No disease predicted")
        
        print("-" * 50)

if __name__ == "__main__":
    test_common_symptoms()