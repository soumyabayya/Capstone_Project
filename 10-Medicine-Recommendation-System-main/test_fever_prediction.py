"""
Test script to specifically verify that single symptom 'fever' returns 'Common Cold'
as required in the specifications.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fever_prediction():
    """Test that single symptom 'fever' returns 'Common Cold'"""
    print("Testing single symptom 'fever' prediction...")
    print("=" * 50)
    
    # Import the functions from main.py
    from main import find_matching_symptoms, predict_disease_from_symptoms
    
    # Test the find_matching_symptoms function
    matched_symptoms = find_matching_symptoms('fever', threshold=0.6)
    print(f"Matched symptoms for 'fever': {matched_symptoms}")
    
    # Test the predict_disease_from_symptoms function
    predicted_disease = predict_disease_from_symptoms(matched_symptoms)
    print(f"Predicted disease: {predicted_disease}")
    
    # Verify the result
    if predicted_disease == 'Common Cold':
        print("✅ SUCCESS: Single symptom 'fever' correctly returns 'Common Cold'")
        return True
    else:
        print(f"❌ FAILURE: Expected 'Common Cold', but got '{predicted_disease}'")
        return False

def test_other_common_symptoms():
    """Test other common symptoms that were previously misclassified"""
    print("\nTesting other common symptoms...")
    print("=" * 50)
    
    # Import the functions from main.py
    from main import find_matching_symptoms, predict_disease_from_symptoms
    
    test_cases = [
        ('cold', 'Common Cold'),
        ('cough', 'Common Cold'),
        ('headache', 'Migraine'),
        ('chills', 'Common Cold')
    ]
    
    all_passed = True
    
    for symptom, expected_disease in test_cases:
        matched_symptoms = find_matching_symptoms(symptom, threshold=0.6)
        predicted_disease = predict_disease_from_symptoms(matched_symptoms)
        
        print(f"Symptom: {symptom}")
        print(f"  Matched symptoms: {matched_symptoms}")
        print(f"  Predicted disease: {predicted_disease}")
        print(f"  Expected disease: {expected_disease}")
        
        if predicted_disease == expected_disease:
            print("  ✅ PASS")
        else:
            print("  ❌ FAIL")
            all_passed = False
        print()
    
    return all_passed

def main():
    """Main test function"""
    print("Disease Prediction System - Special Case Testing")
    print("=" * 60)
    
    # Test fever prediction
    fever_test_passed = test_fever_prediction()
    
    # Test other common symptoms
    other_test_passed = test_other_common_symptoms()
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY:")
    print(f"Single symptom 'fever' test: {'PASS' if fever_test_passed else 'FAIL'}")
    print(f"Other common symptoms test: {'PASS' if other_test_passed else 'FAIL'}")
    
    if fever_test_passed and other_test_passed:
        print("\n🎉 ALL TESTS PASSED! The system meets all requirements.")
        return True
    else:
        print("\n❌ SOME TESTS FAILED! Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)