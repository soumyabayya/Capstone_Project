"""
Final verification script to confirm the cluster symptom fix works correctly
"""

import requests
import re

def test_cluster_fix():
    """Test that the cluster symptom fix works correctly"""
    url = "http://127.0.0.1:5000/predict"
    
    # Test data matching the user's exact input
    data = {
        'symptoms': 'cold,cough,headache,fever'
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Extract predicted disease from response
            # Look for the predicted disease in the response
            disease_match = re.search(r'<h4[^>]*class="text-center mb-4"[^>]*>([^<]+)</h4>', content)
            if not disease_match:
                disease_match = re.search(r'<h4[^>]*>([^<]+)</h4>', content)
            
            if disease_match:
                predicted_disease = disease_match.group(1).strip()
                print(f"Predicted Disease: {predicted_disease}")
                
                if predicted_disease == "Viral Infection":
                    print("✅ SUCCESS: Cluster symptoms correctly return 'Viral Infection'")
                    return True
                else:
                    print(f"❌ FAILURE: Expected 'Viral Infection', but got '{predicted_disease}'")
                    return False
            else:
                print("❌ FAILURE: Could not extract predicted disease from response")
                # Print a snippet of the response for debugging
                print(f"Response snippet: {content[:1000]}")
                return False
        else:
            print(f"❌ FAILURE: HTTP request failed with status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_cluster_fix()
    exit(0 if success else 1)