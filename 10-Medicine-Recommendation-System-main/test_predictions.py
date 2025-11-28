import pandas as pd
import os

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load datasets
symptoms_df = pd.read_csv(os.path.join(BASE_DIR, "dataset/symtoms_df.csv"))
description_df = pd.read_csv(os.path.join(BASE_DIR, "dataset/description.csv"))
precautions_df = pd.read_csv(os.path.join(BASE_DIR, "dataset/precautions_df.csv"))
medications_df = pd.read_csv(os.path.join(BASE_DIR, "dataset/medications.csv"))
diets_df = pd.read_csv(os.path.join(BASE_DIR, "dataset/diets.csv"))
workout_df = pd.read_csv(os.path.join(BASE_DIR, "dataset/workout_df.csv"))

def test_disease_prediction(disease_name):
    """Test the data for a specific disease"""
    print(f"\n=== Testing {disease_name} ===")
    
    # Get description
    desc_rows = description_df[description_df['Disease'] == disease_name]
    if len(desc_rows) > 0:
        description = desc_rows.iloc[0]['Description']
        print(f"Description: {description}")
    else:
        print("Description: Not found")
    
    # Get precautions
    prec_rows = precautions_df[precautions_df['Disease'] == disease_name]
    if len(prec_rows) > 0:
        prec_row = prec_rows.iloc[0]
        precautions = []
        for i in range(1, 5):
            prec_col = f'Precaution_{i}'
            if prec_col in prec_row and pd.notna(prec_row[prec_col]):
                precautions.append(prec_row[prec_col])
        print(f"Precautions: {precautions}")
    else:
        print("Precautions: Not found")
    
    # Get medications
    med_rows = medications_df[medications_df['Disease'] == disease_name]
    if len(med_rows) > 0:
        medication = med_rows.iloc[0]['Medication']
        print(f"Medications: {medication}")
    else:
        print("Medications: Not found")
    
    # Get diets
    diet_rows = diets_df[diets_df['Disease'] == disease_name]
    if len(diet_rows) > 0:
        diet = diet_rows.iloc[0]['Diet']
        print(f"Diets: {diet}")
    else:
        print("Diets: Not found")
    
    # Get workouts
    workout_rows = workout_df[workout_df['disease'] == disease_name]
    if len(workout_rows) > 0:
        workouts = workout_rows['workout'].tolist()
        print(f"Workouts: {workouts[:5]}...")  # Show first 5
    else:
        print("Workouts: Not found")
    
    # Get symptoms
    symptom_rows = symptoms_df[symptoms_df['Disease'] == disease_name]
    if len(symptom_rows) > 0:
        symptoms = []
        for col in symptom_rows.columns:
            if col.startswith('Symptom_'):
                symptom_vals = symptom_rows[col].dropna().tolist()
                symptoms.extend(symptom_vals)
        # Remove duplicates while preserving order
        unique_symptoms = []
        for s in symptoms:
            if s and s not in unique_symptoms:
                unique_symptoms.append(s)
        print(f"Symptoms: {unique_symptoms}")
    else:
        print("Symptoms: Not found")

# Test common diseases
test_disease_prediction("Common Cold")
test_disease_prediction("Malaria")
test_disease_prediction("Typhoid")
test_disease_prediction("Migraine")
test_disease_prediction("Bronchial Asthma")