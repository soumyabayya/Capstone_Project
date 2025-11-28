import pickle
import numpy as np

# Load the trained model
with open('models/disease_prediction_model.pkl', 'rb') as f:
    model_data = pickle.load(f)
    model = model_data['model']
    symptom_to_index = model_data['symptom_to_index']
    index_to_symptom = model_data['index_to_symptom']
    diseases = model_data['diseases']

print("Model loaded successfully!")
print(f"Number of symptoms: {len(symptom_to_index)}")
print(f"Number of diseases: {len(diseases)}")

# Test with some common symptoms
test_symptoms = ['fever', 'cough', 'headache']
print(f"\nTesting with symptoms: {test_symptoms}")

# Convert symptoms to feature vector
input_vector = np.zeros(len(symptom_to_index))
for symptom in test_symptoms:
    if symptom in symptom_to_index:
        input_vector[symptom_to_index[symptom]] = 1

# Predict
prediction = model.predict([input_vector])[0]
probabilities = model.predict_proba([input_vector])[0]
max_prob = np.max(probabilities)

print(f"Predicted disease: {prediction}")
print(f"Confidence: {max_prob:.2f}")

# Test single symptom 'fever'
print("\n" + "="*50)
test_symptoms = ['fever']
print(f"Testing single symptom: {test_symptoms}")

# Convert symptoms to feature vector
input_vector = np.zeros(len(symptom_to_index))
for symptom in test_symptoms:
    if symptom in symptom_to_index:
        input_vector[symptom_to_index[symptom]] = 1

# Predict
prediction = model.predict([input_vector])[0]
probabilities = model.predict_proba([input_vector])[0]
max_prob = np.max(probabilities)

print(f"Predicted disease: {prediction}")
print(f"Confidence: {max_prob:.2f}")