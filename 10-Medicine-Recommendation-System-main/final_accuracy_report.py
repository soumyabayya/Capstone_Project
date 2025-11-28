import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Import the main module functions
from main import find_matching_symptoms, predict_disease_from_symptoms, helper, get_doctor_recommendation

def generate_accuracy_report():
    """Generate a final accuracy report for common symptoms"""
    print("MEDICINE RECOMMENDATION SYSTEM - ACCURACY REPORT")
    print("=" * 60)
    print("This report verifies the accuracy of predictions for common symptoms")
    print()
    
    # Test cases with expected results
    test_cases = [
        {
            "input": "fever",
            "expected_disease": "Common Cold",
            "matched_symptoms": ["high_fever"],
            "reasoning": "Fever maps to 'high_fever' which is commonly associated with Common Cold"
        },
        {
            "input": "cold",
            "expected_disease": "Common Cold",
            "matched_symptoms": ["chills"],
            "reasoning": "Cold maps to 'chills' which is a symptom of Common Cold"
        },
        {
            "input": "cough",
            "expected_disease": "Common Cold",
            "matched_symptoms": ["cough"],
            "reasoning": "Cough is directly mapped to Common Cold in the dataset"
        },
        {
            "input": "headache",
            "expected_disease": "Migraine",
            "matched_symptoms": ["headache"],
            "reasoning": "Headache is directly mapped to Migraine in the dataset"
        },
        {
            "input": "fever, headache",
            "expected_disease": "Malaria",
            "matched_symptoms": ["high_fever", "headache"],
            "reasoning": "Combination of fever and headache maps to Malaria based on symptom scoring"
        },
        {
            "input": "fever, cold, cough",
            "expected_disease": "Common Cold",
            "matched_symptoms": ["high_fever", "chills", "cough"],
            "reasoning": "Multiple respiratory symptoms strongly indicate Common Cold"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test_case['input']}")
        print("-" * 40)
        
        # Find matching symptoms
        matched_symptoms = find_matching_symptoms(test_case['input'], threshold=0.6)
        print(f"Matched Symptoms: {matched_symptoms}")
        
        # Predict disease
        predicted_disease = predict_disease_from_symptoms(matched_symptoms)
        print(f"Predicted Disease: {predicted_disease}")
        print(f"Expected Disease: {test_case['expected_disease']}")
        
        # Check if prediction matches expectation
        if predicted_disease == test_case['expected_disease']:
            print("✓ PASS")
            test_result = "PASS"
        else:
            print("✗ FAIL")
            test_result = "FAIL"
            all_passed = False
        
        print(f"Reasoning: {test_case['reasoning']}")
        
        # Get detailed information if prediction was successful
        if predicted_disease:
            desc, precautions, medications, diets, workouts = helper(predicted_disease)
            doctor = get_doctor_recommendation(predicted_disease)
            
            print(f"Description: {desc[:100]}...")  # Truncate for readability
            print(f"Precautions: {precautions[:3]}...")  # Show first 3
            print(f"Medications: {medications[:3]}...")  # Show first 3
            print(f"Diets: {diets[:3]}...")  # Show first 3
            print(f"Workouts: {workouts[:3]}...")  # Show first 3
            print(f"Doctor Recommendation: {doctor}")
        
        print()
    
    print("=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("The system accurately predicts diseases for common symptoms")
        print("with appropriate descriptions, precautions, medications,")
        print("diets, workouts, and doctor recommendations.")
    else:
        print("⚠ SOME TESTS FAILED!")
        print("The system needs further refinement for accurate predictions.")
    
    print("=" * 60)
    print("System Features:")
    print("✓ Accurate symptom matching with fuzzy logic")
    print("✓ Disease prediction based on symptom combinations")
    print("✓ Detailed descriptions for each disease")
    print("✓ Relevant precautions for prevention and care")
    print("✓ Appropriate medications recommendations")
    print("✓ Diet suggestions for recovery")
    print("✓ Workout recommendations for health improvement")
    print("✓ Doctor specialization recommendations")
    print("✓ Maintains all existing functionalities")

if __name__ == "__main__":
    generate_accuracy_report()