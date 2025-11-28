"""
Simple verification script to confirm cluster symptom fix
"""

def verify_fix():
    """Verify the cluster symptom fix"""
    import sys
    import os
    
    # Add the current directory to Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Import the function from main.py
    from main import predict_disease_from_symptoms
    
    # Test the most critical case - cluster of all four symptoms
    symptoms = ['high_fever', 'chills', 'cough', 'headache']
    result = predict_disease_from_symptoms(symptoms)
    
    print("Cluster Symptom Fix Verification")
    print("=" * 40)
    print(f"Input symptoms: {symptoms}")
    print(f"Predicted disease: {result}")
    
    if result == 'Viral Infection':
        print("✅ SUCCESS: Cluster symptoms correctly return 'Viral Infection'")
        return True
    else:
        print(f"❌ FAILURE: Expected 'Viral Infection', but got '{result}'")
        return False

if __name__ == "__main__":
    success = verify_fix()
    exit(0 if success else 1)