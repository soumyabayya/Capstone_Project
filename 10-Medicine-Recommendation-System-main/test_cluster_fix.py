"""
Test script to verify that cluster symptom detection always returns 'Viral Infection'
for any combination of 2 or more symptoms from fever, cold, cough, and headache
"""

def test_cluster_symptoms():
    """Test cluster symptom detection"""
    import sys
    import os
    
    # Add the current directory to Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Import the function from main.py
    from main import predict_disease_from_symptoms
    
    # Test cases for cluster symptoms - all should return 'Viral Infection'
    cluster_test_cases = [
        (['high_fever', 'chills'], 'Viral Infection'),  # fever + cold
        (['cough', 'headache'], 'Viral Infection'),  # cough + headache
        (['high_fever', 'cough'], 'Viral Infection'),  # fever + cough
        (['chills', 'headache'], 'Viral Infection'),  # cold + headache
        (['high_fever', 'chills', 'cough'], 'Viral Infection'),  # fever + cold + cough
        (['high_fever', 'cough', 'headache'], 'Viral Infection'),  # fever + cough + headache
        (['chills', 'cough', 'headache'], 'Viral Infection'),  # cold + cough + headache
        (['high_fever', 'chills', 'cough', 'headache'], 'Viral Infection'),  # all four
    ]
    
    print("Testing cluster symptom detection...")
    print("=" * 60)
    
    all_passed = True
    
    for symptoms, expected in cluster_test_cases:
        result = predict_disease_from_symptoms(symptoms)
        print(f"Symptoms: {symptoms}")
        print(f"Expected: {expected}")
        print(f"Got: {result}")
        
        if result == expected:
            print("✅ PASS\n")
        else:
            print("❌ FAIL\n")
            all_passed = False
    
    # Test cases that should NOT return 'Viral Infection'
    non_cluster_test_cases = [
        (['high_fever'], 'Viral Infection'),  # single fever
        (['chills'], 'Common Cold'),  # single cold
        (['cough'], 'Viral Respiratory Infection'),  # single cough
        (['headache'], 'Sinusitis'),  # single headache
        (['itching', 'skin_rash'], None),  # unrelated symptoms
    ]
    
    print("Testing non-cluster symptoms...")
    print("=" * 60)
    
    for symptoms, expected in non_cluster_test_cases:
        result = predict_disease_from_symptoms(symptoms)
        print(f"Symptoms: {symptoms}")
        print(f"Expected: {expected}")
        print(f"Got: {result}")
        
        # For the unrelated symptoms, we just check that it's not 'Viral Infection'
        if symptoms == ['itching', 'skin_rash']:
            if result != 'Viral Infection':
                print("✅ PASS (correctly not Viral Infection)\n")
            else:
                print("❌ FAIL (incorrectly returned Viral Infection)\n")
                all_passed = False
        else:
            # For single symptoms, check exact match
            if result == expected:
                print("✅ PASS\n")
            else:
                print("❌ FAIL\n")
                all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! Cluster symptom detection works correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    success = test_cluster_symptoms()
    exit(0 if success else 1)