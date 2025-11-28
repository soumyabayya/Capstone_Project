import pandas as pd
import os

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load all datasets
symptoms_df = pd.read_csv(os.path.join(BASE_DIR, "dataset/symtoms_df.csv"))
description_df = pd.read_csv(os.path.join(BASE_DIR, "dataset/description.csv"))
precautions_df = pd.read_csv(os.path.join(BASE_DIR, "dataset/precautions_df.csv"))
medications_df = pd.read_csv(os.path.join(BASE_DIR, "dataset/medications.csv"))
diets_df = pd.read_csv(os.path.join(BASE_DIR, "dataset/diets.csv"))
workout_df = pd.read_csv(os.path.join(BASE_DIR, "dataset/workout_df.csv"))

def verify_disease_data(disease_name):
    """Verify that all data for a disease is consistent and available"""
    print(f"\n=== Verifying {disease_name} ===")
    
    # Check if disease exists in all datasets
    datasets = {
        "Symptoms": symptoms_df,
        "Description": description_df,
        "Precautions": precautions_df,
        "Medications": medications_df,
        "Diets": diets_df,
        "Workouts": workout_df
    }
    
    all_good = True
    
    for dataset_name, df in datasets.items():
        if dataset_name == "Symptoms":
            exists = disease_name in df['Disease'].values
        elif dataset_name == "Workouts":
            exists = disease_name in df['disease'].values
        else:
            exists = disease_name in df['Disease'].values
            
        if exists:
            print(f"✓ {dataset_name}: Found")
        else:
            print(f"✗ {dataset_name}: Missing")
            all_good = False
    
    return all_good

def verify_common_diseases():
    """Verify data for common diseases"""
    common_diseases = [
        "Common Cold",
        "Malaria",
        "Typhoid",
        "Migraine",
        "Bronchial Asthma",
        "Fungal infection",
        "Allergy",
        "GERD"
    ]
    
    print("=== Verifying Common Diseases ===")
    all_passed = True
    
    for disease in common_diseases:
        if not verify_disease_data(disease):
            all_passed = False
    
    if all_passed:
        print("\n✓ All common diseases have complete data")
    else:
        print("\n✗ Some diseases are missing data")
    
    return all_passed

def verify_symptom_disease_mapping():
    """Verify that symptoms map to appropriate diseases"""
    print("\n=== Verifying Symptom-Disease Mapping ===")
    
    # Check common symptoms (note the leading spaces in the dataset)
    common_symptoms = {
        " high_fever": ["Common Cold", "Malaria", "Typhoid"],
        " cough": ["Common Cold", "Bronchial Asthma"],
        " headache": ["Migraine", "Malaria", "Typhoid"],
        " chills": ["Common Cold", "Malaria", "Typhoid"]
    }
    
    for symptom, expected_diseases in common_symptoms.items():
        # Find diseases that have this symptom
        diseases_with_symptom = []
        for index, row in symptoms_df.iterrows():
            for col in row.index:
                if isinstance(col, str) and col.startswith('Symptom_') and row[col] == symptom:
                    diseases_with_symptom.append(row['Disease'])
                    break
        
        # Remove duplicates
        diseases_with_symptom = list(set(diseases_with_symptom))
        
        print(f"Symptom '{symptom}' found in diseases: {diseases_with_symptom}")
        
        # Check if expected diseases are present
        for expected in expected_diseases:
            if expected in diseases_with_symptom:
                print(f"  ✓ Expected disease '{expected}' found")
            else:
                print(f"  ⚠ Expected disease '{expected}' not found for '{symptom}'")

def verify_data_consistency():
    """Verify that data across datasets is consistent"""
    print("\n=== Verifying Data Consistency ===")
    
    # Get all unique diseases from symptoms dataset
    symptom_diseases = set(symptoms_df['Disease'].unique())
    description_diseases = set(description_df['Disease'].unique())
    precaution_diseases = set(precautions_df['Disease'].unique())
    medication_diseases = set(medications_df['Disease'].unique())
    diet_diseases = set(diets_df['Disease'].unique())
    workout_diseases = set(workout_df['disease'].unique())
    
    # Check for consistency
    all_diseases = symptom_diseases
    datasets = {
        "Description": description_diseases,
        "Precautions": precaution_diseases,
        "Medications": medication_diseases,
        "Diets": diet_diseases,
        "Workouts": workout_diseases
    }
    
    consistent = True
    for name, diseases in datasets.items():
        missing_in_dataset = all_diseases - diseases
        missing_in_symptoms = diseases - all_diseases
        
        if missing_in_dataset:
            print(f"⚠ Diseases in Symptoms but missing in {name}: {missing_in_dataset}")
            consistent = False
        if missing_in_symptoms:
            print(f"⚠ Diseases in {name} but missing in Symptoms: {missing_in_symptoms}")
            consistent = False
    
    if consistent:
        print("✓ All datasets are consistent")
    else:
        print("✗ Some inconsistencies found")
    
    return consistent

if __name__ == "__main__":
    print("Medicine Recommendation System - Data Verification")
    print("=" * 50)
    
    # Run all verification checks
    test1 = verify_common_diseases()
    verify_symptom_disease_mapping()
    test2 = verify_data_consistency()
    
    print("\n" + "=" * 50)
    if test1 and test2:
        print("✓ All verification tests passed!")
        print("The system has accurate and consistent data.")
    else:
        print("⚠ Some verification tests failed.")
        print("Please check the data consistency.")