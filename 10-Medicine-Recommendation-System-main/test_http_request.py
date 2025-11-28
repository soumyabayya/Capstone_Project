"""
Test script to simulate an HTTP POST request to the /predict endpoint
"""

import requests
import re

def test_http_request():
    """Test the HTTP POST request with the problematic input"""
    url = "http://127.0.0.1:5000/predict"
    
    # Test data matching the user's input
    data = {
        'symptoms': 'cold,cough,headache,fever'
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        
        # Extract predicted disease from response
        content = response.text
        
        # Look for the predicted disease in the response
        disease_match = re.search(r'<h4 class="text-center mb-4">([^<]+)</h4>', content)
        if disease_match:
            predicted_disease = disease_match.group(1)
            print(f"Predicted Disease: {predicted_disease}")
        else:
            # Try another pattern
            disease_match = re.search(r'<h4[^>]*>([^<]+)</h4>', content)
            if disease_match:
                predicted_disease = disease_match.group(1)
                print(f"Predicted Disease: {predicted_disease}")
            else:
                print("Could not extract predicted disease from response")
        
        # Look for the description
        desc_match = re.search(r'<p[^>]*class="text-muted"[^>]*>([^<]+)</p>', content)
        if desc_match:
            description = desc_match.group(1)
            print(f"Description: {description}")
        
        # Print a snippet of the response for debugging
        print(f"Response snippet: {content[:1000]}")
        
    except Exception as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    test_http_request()