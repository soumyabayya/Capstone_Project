import pandas as pd
import os

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load symptoms dataset
symptoms_df = pd.read_csv(os.path.join(BASE_DIR, "dataset/symtoms_df.csv"))

# Get all unique symptoms
symptoms = set()
for col in ['Symptom_1', 'Symptom_2', 'Symptom_3', 'Symptom_4']:
    symptoms.update(symptoms_df[col].dropna().unique())

print("Available symptoms:")
for symptom in sorted(list(symptoms)):
    print(f"  {symptom}")

# Check for specific symptoms
common_symptoms = ['high_fever', 'cough', 'headache', 'chills', 'fever']
print("\nChecking for common symptoms:")
for symptom in common_symptoms:
    if symptom in symptoms:
        print(f"✓ {symptom} found")
    else:
        print(f"✗ {symptom} not found")

# Check what diseases have high_fever
print("\nDiseases with ' high_fever' (note the space):")
diseases_with_high_fever = symptoms_df[symptoms_df.isin([' high_fever']).any(axis=1)]
for disease in diseases_with_high_fever['Disease'].unique():
    print(f"  {disease}")

print("\nDiseases with ' cough' (note the space):")
diseases_with_cough = symptoms_df[symptoms_df.isin([' cough']).any(axis=1)]
for disease in diseases_with_cough['Disease'].unique():
    print(f"  {disease}")

print("\nDiseases with ' headache' (note the space):")
diseases_with_headache = symptoms_df[symptoms_df.isin([' headache']).any(axis=1)]
for disease in diseases_with_headache['Disease'].unique():
    print(f"  {disease}")