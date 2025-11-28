"""
Test script to verify the new disease mappings work correctly
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_single_symptom_mappings():
    """Test the new single symptom mappings"""
    print("Testing single symptom mappings...")
    print("=" * 50)
    
    # Import the functions from main.py
    from main import find_matching_symptoms, predict_disease_from_symptoms
    
    test_cases = [
        ('fever', 'Viral Infection'),
        ('cold', 'Common Cold'),
        ('cough', 'Viral Respiratory Infection'),
        ('headache', 'Sinusitis')
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

def test_cluster_symptom_mappings():
    """Test the cluster symptom mappings"""
    print("Testing cluster symptom mappings...")
    print("=" * 50)
    
    # Import the functions from main.py
    from main import find_matching_symptoms, predict_disease_from_symptoms
    
    # Test cases with combinations of 2, 3, and 4 symptoms
    test_cases = [
        (['fever', 'cold'], 'Viral Infection'),
        (['cough', 'headache'], 'Viral Infection'),
        (['fever', 'cold', 'cough'], 'Viral Infection'),
        (['fever', 'cold', 'cough', 'headache'], 'Viral Infection'),
        (['headache', 'cold'], 'Viral Infection'),
    ]
    
    all_passed = True
    
    for symptoms, expected_disease in test_cases:
        # For each symptom, find matching symptoms
        matched_symptoms = []
        for symptom in symptoms:
            symptom_matches = find_matching_symptoms(symptom, threshold=0.6)
            matched_symptoms.extend(symptom_matches)
        
        # Remove duplicates
        matched_symptoms = list(set(matched_symptoms))
        
        predicted_disease = predict_disease_from_symptoms(matched_symptoms)
        
        print(f"Symptoms: {symptoms}")
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

def test_helper_function():
    """Test the helper function with new disease mappings"""
    print("Testing helper function with new disease mappings...")
    print("=" * 50)
    
    # Import the helper function from main.py
    from main import helper
    
    test_diseases = [
        'Viral Infection',
        'Common Cold',
        'Viral Respiratory Infection',
        'Sinusitis'
    ]
    
    all_passed = True
    
    for disease in test_diseases:
        desc, precautions, medications, diets, workout = helper(disease)
        
        print(f"Disease: {disease}")
        print(f"  Description: {desc[:50]}...")
        print(f"  Precautions: {len(precautions)} items")
        print(f"  Medications: {len(medications)} items")
        print(f"  Diets: {len(diets)} items")
        print(f"  Workouts: {len(workout)} items")
        
        # Check that we got meaningful data
        if desc and desc != "Description not available" and len(precautions) > 0:
            print("  ✅ PASS")
        else:
            print("  ❌ FAIL")
            all_passed = False
        print()
    
    return all_passed

def main():
    """Main test function"""
    print("Disease Prediction System - New Mappings Testing")
    print("=" * 60)
    
    # Test single symptom mappings
    single_test_passed = test_single_symptom_mappings()
    
    # Test cluster symptom mappings
    cluster_test_passed = test_cluster_symptom_mappings()
    
    # Test helper function
    helper_test_passed = test_helper_function()
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY:")
    print(f"Single symptom mappings test: {'PASS' if single_test_passed else 'FAIL'}")
    print(f"Cluster symptom mappings test: {'PASS' if cluster_test_passed else 'FAIL'}")
    print(f"Helper function test: {'PASS' if helper_test_passed else 'FAIL'}")
    
    if single_test_passed and cluster_test_passed and helper_test_passed:
        print("\n🎉 ALL TESTS PASSED! The new mappings work correctly.")
        return True
    else:
        print("\n❌ SOME TESTS FAILED! Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)