import numpy as np
import pandas as pd
import pickle
import ast
import os
import re
from flask import Flask, request, render_template, jsonify
from sklearn.ensemble import RandomForestClassifier

# flask app
app = Flask(__name__)

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# load dataset===================================
sym_des = pd.read_csv(os.path.join(BASE_DIR, "dataset/symtoms_df.csv"))
precautions = pd.read_csv(os.path.join(BASE_DIR, "dataset/precautions_df.csv"))
workout = pd.read_csv(os.path.join(BASE_DIR, "dataset/workout_df.csv"))
description = pd.read_csv(os.path.join(BASE_DIR, "dataset/description.csv"))
medications = pd.read_csv(os.path.join(BASE_DIR, 'dataset/medications.csv'))
diets = pd.read_csv(os.path.join(BASE_DIR, "dataset/diets.csv"))

# Load the trained model
try:
    with open(os.path.join(BASE_DIR, 'models/disease_prediction_model.pkl'), 'rb') as f:
        model_data = pickle.load(f)
        model = model_data['model']
        symptom_to_index = model_data['symptom_to_index']
        index_to_symptom = model_data['index_to_symptom']
        diseases = model_data['diseases']
except FileNotFoundError:
    # Fallback to original model if new model is not available
    model = pickle.load(open(os.path.join(BASE_DIR, 'models/svc.pkl'), 'rb'))
    symptom_to_index = None

#============================================================
# custom and helping functions
#==========================helper functions================

# Global variables to store dataset symptoms and disease mappings
DATASET_SYMPTOMS = set()  # For fast symptom lookup
SYMPTOM_TO_DISEASES = {}  # Map symptoms to diseases
DISEASE_SYMPTOMS = {}     # Map diseases to their symptoms

# Function to initialize dataset symptoms and mappings
def initialize_dataset_mappings():
    """Load symptoms directly from dataset and create mappings for fast lookup"""
    global DATASET_SYMPTOMS, SYMPTOM_TO_DISEASES, DISEASE_SYMPTOMS
    
    # Clear existing data
    DATASET_SYMPTOMS.clear()
    SYMPTOM_TO_DISEASES.clear()
    DISEASE_SYMPTOMS.clear()
    
    # Process the symptoms dataset
    for index, row in sym_des.iterrows():
        disease = row['Disease']
        
        # Collect all symptoms for this disease
        disease_symptoms = []
        
        # Check all symptom columns (Symptom_1, Symptom_2, etc.)
        for col in row.index:
            col_name = str(col)  # Convert to string to ensure startswith works
            if col_name.startswith('Symptom_'):
                symptom_value = row[col]
                # Handle pandas Series by converting to string representation
                if hasattr(symptom_value, 'iloc') or hasattr(symptom_value, 'values'):
                    # It's a pandas object, convert to string and extract value
                    symptom_str = str(symptom_value)
                    # If it's a Series representation, extract the actual value
                    if symptom_str.startswith('0') and '    ' in symptom_str:
                        # Extract the actual value from Series string representation
                        try:
                            symptom_value = symptom_str.split()[1]  # Get the value part
                        except:
                            symptom_value = symptom_str
                    else:
                        symptom_value = symptom_str
                
                # Check if not null/NaN
                if symptom_value is not None and str(symptom_value).lower() != 'nan' and str(symptom_value).strip() != '':
                    symptom = str(symptom_value).strip().lower()
                    if symptom:  # Only add non-empty symptoms
                        # Add to dataset symptoms set
                        DATASET_SYMPTOMS.add(symptom)
                        
                        # Map symptom to disease
                        if symptom not in SYMPTOM_TO_DISEASES:
                            SYMPTOM_TO_DISEASES[symptom] = set()
                        SYMPTOM_TO_DISEASES[symptom].add(disease)
                        
                        # Add to disease symptoms list
                        disease_symptoms.append(symptom)
        
        # Map disease to its symptoms
        if disease not in DISEASE_SYMPTOMS:
            DISEASE_SYMPTOMS[disease] = set()
        DISEASE_SYMPTOMS[disease].update(disease_symptoms)

# Function to normalize input text
def normalize_input(text):
    """Normalize input by removing punctuation, converting to lowercase, trimming spaces"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation (commas, periods, etc.)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # Replace multiple spaces with single space and trim
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# Disease name mapping to handle mismatches between model predictions and CSV data
def normalize_disease_name(disease_name):
    """Normalize disease names to match CSV file format"""
    disease_name = disease_name.strip()  # Remove leading/trailing spaces
    
    # Map model disease names to CSV disease names
    disease_mapping = {
        'Peptic ulcer diseae': 'Peptic ulcer disease',  # Fix typo
        'Diabetes': 'Diabetes ',  # Add trailing space to match CSV
        'Hypertension': 'Hypertension ',  # Add trailing space to match CSV
        'Viral Infection': 'Common Cold',  # Map Viral Infection to Common Cold for data lookup
        'Viral Respiratory Infection': 'Common Cold',  # Map to Common Cold for data lookup
        'Sinusitis': 'Common Cold',  # Map to Common Cold for data lookup
    }
    
    return disease_mapping.get(disease_name, disease_name)

def get_custom_disease_info(disease_name):
    """Get custom disease information for newly mapped diseases"""
    # Custom information for our special disease mappings
    custom_disease_info = {
        'Viral Infection': {
            'description': 'A viral infection is a illness caused by a virus. Common symptoms include fever, fatigue, and body aches. Most viral infections resolve on their own with rest and supportive care.',
            'precautions': ['Get plenty of rest', 'Stay hydrated', 'Use over-the-counter pain relievers', 'Avoid contact with others to prevent spreading'],
            'medications': ['Acetaminophen', 'Ibuprofen', 'Antiviral medications (if prescribed)'],
            'diets': ['Drink plenty of fluids', 'Eat light, nutritious meals', 'Include vitamin C rich foods'],
            'workout': ['Rest completely until symptoms improve', 'Gradual return to normal activities'],
        },
        'Common Cold': {
            'description': 'The common cold is a viral infection of your nose and throat (upper respiratory tract). It\'s usually harmless, although it might not feel that way.',
            'precautions': ['Wash hands frequently', 'Avoid close contact with sick individuals', 'Disinfect surfaces', 'Stay hydrated'],
            'medications': ['Decongestants', 'Antihistamines', 'Pain relievers', 'Cough suppressants'],
            'diets': ['Warm fluids like tea or soup', 'Honey', 'Vitamin C rich foods', 'Chicken soup'],
            'workout': ['Light activities if feeling well', 'Rest if experiencing severe symptoms'],
        },
        'Viral Respiratory Infection': {
            'description': 'A viral respiratory infection affects the nose, throat, or lungs. These infections are common and usually resolve on their own within a week or two.',
            'precautions': ['Cover mouth when coughing or sneezing', 'Wash hands frequently', 'Avoid touching face', 'Stay home when sick'],
            'medications': ['Cough syrup', 'Decongestants', 'Pain relievers', 'Throat lozenges'],
            'diets': ['Warm liquids', 'Honey and lemon tea', 'Clear broths', 'Soft foods'],
            'workout': ['Rest until symptoms subside', 'Avoid strenuous activities'],
        },
        'Sinusitis': {
            'description': 'Sinusitis is an inflammation or swelling of the tissue lining the sinuses. Common symptoms include nasal congestion, facial pain, and headache.',
            'precautions': ['Use a humidifier', 'Avoid allergens', 'Stay hydrated', 'Practice good nasal hygiene'],
            'medications': ['Decongestants', 'Nasal corticosteroids', 'Saline nasal sprays', 'Pain relievers'],
            'diets': ['Anti-inflammatory foods', 'Plenty of water', 'Warm liquids', 'Spicy foods to clear sinuses'],
            'workout': ['Light activities if feeling well', 'Avoid activities that increase head pressure'],
        }
    }
    
    return custom_disease_info.get(disease_name, None)

def helper(dis):
    # Check if we have custom information for this disease
    custom_info = get_custom_disease_info(dis)
    if custom_info:
        return (
            custom_info['description'],
            custom_info['precautions'],
            custom_info['medications'],
            custom_info['diets'],
            custom_info['workout']
        )
    
    # Normalize disease name to match CSV format
    dis_normalized = normalize_disease_name(dis)
    
    # Get description
    desc_rows = description[description['Disease'] == dis_normalized]['Description']
    if len(desc_rows) > 0:
        # Convert to list and get first element
        desc_list = list(desc_rows)
        desc = desc_list[0] if desc_list else "Description not available"
    else:
        desc = "Description not available"

    # Get precautions - return as a flat list
    pre_rows = precautions[precautions['Disease'] == dis_normalized]
    my_precautions = []
    if len(pre_rows) > 0:
        # Get the first row
        pre_row = pre_rows.iloc[0]
        # Extract all precaution columns (Precaution_1, Precaution_2, etc.)
        for i in range(1, 5):  # 1 to 4
            precaution_col = f'Precaution_{i}'
            if precaution_col in pre_row and pd.notna(pre_row[precaution_col]):
                my_precautions.append(pre_row[precaution_col])

    # Get medications - parse string representation of list
    med_rows = medications[medications['Disease'] == dis_normalized]['Medication']
    med_list = []
    if len(med_rows) > 0:
        # Convert to list and get first element
        med_list_vals = list(med_rows)
        if med_list_vals:
            med_str = med_list_vals[0]
            try:
                # Parse the string representation of a list
                med_list = ast.literal_eval(med_str) if isinstance(med_str, str) else []
            except (ValueError, SyntaxError):
                med_list = [med_str] if med_str else []

    # Get diets - parse string representation of list
    die_rows = diets[diets['Disease'] == dis_normalized]['Diet']
    die_list = []
    if len(die_rows) > 0:
        # Convert to list and get first element
        die_list_vals = list(die_rows)
        if die_list_vals:
            die_str = die_list_vals[0]
            try:
                # Parse the string representation of a list
                die_list = ast.literal_eval(die_str) if isinstance(die_str, str) else []
            except (ValueError, SyntaxError):
                die_list = [die_str] if die_str else []

    # Get workout - get all workout values as a list
    wrkout_rows = workout[workout['disease'] == dis_normalized]['workout']
    wrkout_list = []
    if len(wrkout_rows) > 0:
        # Convert to list
        wrkout_list_vals = list(wrkout_rows)
        # Filter out NaN values
        wrkout_list = [w for w in wrkout_list_vals if pd.notna(w)]

    return desc, my_precautions, med_list, die_list, wrkout_list

# Initialize dataset mappings when the application starts
initialize_dataset_mappings()

# Keep the original symptoms_dict for backward compatibility with existing model
symptoms_dict = {'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3, 'shivering': 4, 'chills': 5, 'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8, 'ulcers_on_tongue': 9, 'muscle_wasting': 10, 'vomiting': 11, 'burning_micturition': 12, 'spotting_ urination': 13, 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16, 'cold_hands_and_feets': 17, 'mood_swings': 18, 'weight_loss': 19, 'restlessness': 20, 'lethargy': 21, 'patches_in_throat': 22, 'irregular_sugar_level': 23, 'cough': 24, 'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27, 'sweating': 28, 'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32, 'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36, 'back_pain': 37, 'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40, 'mild_fever': 41, 'yellow_urine': 42, 'yellowing_of_eyes': 43, 'acute_liver_failure': 44, 'fluid_overload': 45, 'swelling_of_stomach': 46, 'swelled_lymph_nodes': 47, 'malaise': 48, 'blurred_and_distorted_vision': 49, 'phlegm': 50, 'throat_irritation': 51, 'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54, 'congestion': 55, 'chest_pain': 56, 'weakness_in_limbs': 57, 'fast_heart_rate': 58, 'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61, 'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65, 'bruising': 66, 'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69, 'puffy_face_and_eyes': 70, 'enlarged_thyroid': 71, 'brittle_nails': 72, 'swollen_extremeties': 73, 'excessive_hunger': 74, 'extra_marital_contacts': 75, 'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78, 'hip_joint_pain': 79, 'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82, 'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85, 'unsteadiness': 86, 'weakness_of_one_body_side': 87, 'loss_of_smell': 88, 'bladder_discomfort': 89, 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91, 'passage_of_gases': 92, 'internal_itching': 93, 'toxic_look_(typhos)': 94, 'depression': 95, 'irritability': 96, 'muscle_pain': 97, 'altered_sensorium': 98, 'red_spots_over_body': 99, 'belly_pain': 100, 'abnormal_menstruation': 101, 'dischromic _patches': 102, 'watering_from_eyes': 103, 'increased_appetite': 104, 'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107, 'rusty_sputum': 108, 'lack_of_concentration': 109, 'visual_disturbances': 110, 'receiving_blood_transfusion': 111, 'receiving_unsterile_injections': 112, 'coma': 113, 'stomach_bleeding': 114, 'distention_of_abdomen': 115, 'history_of_alcohol_consumption': 116, 'fluid_overload.1': 117, 'blood_in_sputum': 118, 'prominent_veins_on_calf': 119, 'palpitations': 120, 'painful_walking': 121, 'pus_filled_pimples': 122, 'blackheads': 123, 'scurring': 124, 'skin_peeling': 125, 'silver_like_dusting': 126, 'small_dents_in_nails': 127, 'inflammatory_nails': 128, 'blister': 129, 'red_sore_around_nose': 130, 'yellow_crust_ooze': 131}
diseases_list = {15: 'Fungal infection', 4: 'Allergy', 16: 'GERD', 9: 'Chronic cholestasis', 14: 'Drug Reaction', 33: 'Peptic ulcer diseae', 1: 'AIDS', 12: 'Diabetes ', 17: 'Gastroenteritis', 6: 'Bronchial Asthma', 23: 'Hypertension ', 30: 'Migraine', 7: 'Cervical spondylosis', 32: 'Paralysis (brain hemorrhage)', 28: 'Jaundice', 29: 'Malaria', 8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A', 19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E', 3: 'Alcoholic hepatitis', 36: 'Tuberculosis', 10: 'Common Cold', 34: 'Pneumonia', 13: 'Dimorphic hemmorhoids(piles)', 18: 'Heart attack', 39: 'Varicose veins', 26: 'Hypothyroidism', 24: 'Hyperthyroidism', 25: 'Hypoglycemia', 31: 'Osteoarthristis', 5: 'Arthritis', 0: '(vertigo) Paroymsal  Positional Vertigo', 2: 'Acne', 38: 'Urinary tract infection', 35: 'Psoriasis', 27: 'Impetigo'}

# Function to convert symptoms to feature vector for the new model
def symptoms_to_vector(symptoms):
    """Convert symptoms to feature vector for model prediction"""
    if symptom_to_index is None:
        # Fallback to original method
        input_vector = np.zeros(len(symptoms_dict))
        for item in symptoms:
            if item in symptoms_dict:
                input_vector[symptoms_dict[item]] = 1
        return input_vector
    
    # Use new model approach
    input_vector = np.zeros(len(symptom_to_index))
    for symptom in symptoms:
        if symptom in symptom_to_index:
            input_vector[symptom_to_index[symptom]] = 1
    return input_vector

# Enhanced model prediction function
def get_predicted_value(patient_symptoms):
    """Predict disease based on symptoms using the trained model"""
    # Convert symptoms to feature vector
    input_vector = symptoms_to_vector(patient_symptoms)
    
    # Predict using the model
    if symptom_to_index is not None and isinstance(model, RandomForestClassifier):
        # Use new model
        prediction = model.predict([input_vector])[0]
        probabilities = model.predict_proba([input_vector])[0]
        # Get the maximum probability
        max_prob = np.max(probabilities)
        # If confidence is too low, return None
        if max_prob < 0.1:  # 10% threshold
            return None
        return prediction
    else:
        # Fallback to original method
        prediction = model.predict([input_vector])[0]
        return diseases_list[prediction]

# Doctor recommendation based on disease category
def get_doctor_recommendation(disease):
    """Return doctor recommendation based on disease category"""
    # Mapping of diseases to specialists
    doctor_mapping = {
        # Fever and general symptoms
        'Fungal infection': 'Dermatologist',
        'Allergy': 'Allergist',
        'Common Cold': 'General Physician',
        'Malaria': 'General Physician',
        'Dengue': 'General Physician',
        'Typhoid': 'General Physician',
        'Chicken pox': 'General Physician',
        'AIDS': 'Infectious Disease Specialist',
        'Tuberculosis': 'Pulmonologist',
        'hepatitis A': 'Hepatologist',
        'Hepatitis B': 'Hepatologist',
        'Hepatitis C': 'Hepatologist',
        'Hepatitis D': 'Hepatologist',
        'Hepatitis E': 'Hepatologist',
        'Alcoholic hepatitis': 'Hepatologist',
        
        # Heart related
        'Heart attack': 'Cardiologist',
        'Hypertension': 'Cardiologist',
        'Bradycardia': 'Cardiologist',
        'Tachycardia': 'Cardiologist',
        
        # Digestive system
        'GERD': 'Gastroenterologist',
        'Chronic cholestasis': 'Gastroenterologist',
        'Peptic ulcer disease': 'Gastroenterologist',
        'Gastroenteritis': 'Gastroenterologist',
        'Jaundice': 'Gastroenterologist',
        'Diabetes': 'Endocrinologist',
        'Hyperthyroidism': 'Endocrinologist',
        'Hypothyroidism': 'Endocrinologist',
        'Hypoglycemia': 'Endocrinologist',
        
        # Respiratory system
        'Bronchial Asthma': 'Pulmonologist',
        'Pneumonia': 'Pulmonologist',
        
        # Neurological
        'Migraine': 'Neurologist',
        'Cervical spondylosis': 'Orthopedist',
        'Paralysis (brain hemorrhage)': 'Neurologist',
        '(vertigo) Paroymsal  Positional Vertigo': 'ENT Specialist',
        
        # Musculoskeletal
        'Osteoarthristis': 'Orthopedist',
        'Arthritis': 'Rheumatologist',
        'Cervical spondylosis': 'Orthopedist',
        
        # Skin conditions
        'Acne': 'Dermatologist',
        'Impetigo': 'Dermatologist',
        'Psoriasis': 'Dermatologist',
        
        # Other systems
        'Urinary tract infection': 'Urologist',
        'Dimorphic hemmorhoids(piles)': 'Proctologist',
        
        # Mental health
        'Depression': 'Psychiatrist',
        'Anxiety': 'Psychiatrist',
        
        # New mappings as per requirements
        'Viral Infection': 'General Physician',
        'Viral Respiratory Infection': 'Pulmonologist',
        'Sinusitis': 'ENT Specialist',
        'Sinus': 'ENT Specialist',
        
        # Default recommendation
        'default': 'General Physician'
    }
    
    # Return specific doctor or default to General Physician
    return doctor_mapping.get(disease, doctor_mapping['default'])

# Function to clean speech input (same as JavaScript implementation)
def clean_speech_input(text):
    """Clean speech input to match JavaScript processing"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and special characters BUT KEEP COMMAS
    text = re.sub(r'[^\w\s,]', '', text)
    
    # Replace multiple spaces with single space and trim
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Apply fuzzy matching for common mispronunciations (same as JavaScript)
    fuzzy_corrections = {
        'feaver': 'fever',
        'fevr': 'fever',
        'couh': 'cough',
        'cugh': 'cough',
        'colt': 'cold',
        'codl': 'cold',
        'headack': 'headache',
        'headace': 'headache',
        'stomac': 'stomach',
        'stomache': 'stomach',
        'throte': 'throat',
        'sorn': 'sore',
        'soar': 'sore',
        'paine': 'pain',
        'aching': 'ache',
        'runny nose': 'runny nose',
        'sore throat': 'sore throat',
        'body pain': 'body pain',
        'chest pain': 'chest pain'
    }
    
    # Apply corrections
    for mispronounced, correct in fuzzy_corrections.items():
        text = re.sub(r'\b' + re.escape(mispronounced) + r'\b', correct, text)
    
    return text

# Function to calculate similarity between two strings (enhanced Levenshtein distance)
def calculate_similarity(str1, str2):
    """Calculate similarity ratio between two strings using enhanced Levenshtein distance"""
    if not str1 or not str2:
        return 0.0
    
    # Convert to lowercase for comparison
    str1, str2 = str1.lower(), str2.lower()
    
    # If strings are identical, return 1.0
    if str1 == str2:
        return 1.0
    
    # Calculate Levenshtein distance
    len1, len2 = len(str1), len(str2)
    
    # Create matrix
    matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    
    # Initialize first row and column
    for i in range(len1 + 1):
        matrix[i][0] = i
    for j in range(len2 + 1):
        matrix[0][j] = j
    
    # Fill matrix
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if str1[i-1] == str2[j-1]:
                cost = 0
            else:
                cost = 1
            matrix[i][j] = min(
                matrix[i-1][j] + 1,      # deletion
                matrix[i][j-1] + 1,      # insertion
                matrix[i-1][j-1] + cost  # substitution
            )
    
    # Calculate similarity ratio
    distance = matrix[len1][len2]
    max_len = max(len1, len2)
    
    if max_len == 0:
        return 1.0
    
    return 1.0 - (distance / max_len)

# Function to find best matching symptoms using enhanced fuzzy matching
def find_matching_symptoms(user_input, threshold=0.75):
    """Find matching symptoms using enhanced fuzzy matching with threshold (0.0-1.0)"""
    if not user_input or not DATASET_SYMPTOMS:
        return []
    
    # Normalize user input
    normalized_input = normalize_input(user_input)
    
    # Direct mapping for common symptoms that might not match exactly
    common_symptom_mappings = {
        'fever': 'high_fever',
        'cold': 'chills',
        'head ache': 'headache',
        'head-ache': 'headache',
        'coughing': 'cough',
        'sneezing': 'continuous_sneezing'
    }
    
    # Check for direct mappings first
    if normalized_input in common_symptom_mappings:
        mapped_symptom = common_symptom_mappings[normalized_input]
        if mapped_symptom in DATASET_SYMPTOMS:
            return [mapped_symptom]
    
    # First try to match the entire input as a multi-word symptom
    if normalized_input in DATASET_SYMPTOMS:
        return [normalized_input]
    
    # Try to find exact matches for multi-word phrases
    matched_symptoms = []
    
    # Split input into potential symptoms
    input_symptoms = [s.strip() for s in normalized_input.split() if s.strip()]
    
    # Try to match multi-word phrases first (3-word, 2-word, then 1-word)
    i = 0
    while i < len(input_symptoms):
        matched = False
        
        # Try matching 4-word phrases
        if i + 3 < len(input_symptoms):
            four_word = ' '.join(input_symptoms[i:i+4])
            if four_word in DATASET_SYMPTOMS:
                matched_symptoms.append(four_word)
                i += 4
                matched = True
                continue
        
        # Try matching 3-word phrases
        if i + 2 < len(input_symptoms):
            three_word = ' '.join(input_symptoms[i:i+3])
            if three_word in DATASET_SYMPTOMS:
                matched_symptoms.append(three_word)
                i += 3
                matched = True
                continue
        
        # Try matching 2-word phrases
        if i + 1 < len(input_symptoms):
            two_word = ' '.join(input_symptoms[i:i+2])
            if two_word in DATASET_SYMPTOMS:
                matched_symptoms.append(two_word)
                i += 2
                matched = True
                continue
        
        # Try matching single words with fuzzy matching
        if not matched:
            best_match = None
            best_score = 0
            
            # Check for direct mapping first
            word = input_symptoms[i]
            if word in common_symptom_mappings:
                mapped_word = common_symptom_mappings[word]
                if mapped_word in DATASET_SYMPTOMS:
                    if mapped_word not in matched_symptoms:
                        matched_symptoms.append(mapped_word)
                    i += 1
                    continue
            
            # Check against all dataset symptoms
            for dataset_symptom in DATASET_SYMPTOMS:
                # Calculate similarity
                score = calculate_similarity(word, dataset_symptom)
                
                # If score is above threshold and better than current best
                if score >= threshold and score > best_score:
                    best_match = dataset_symptom
                    best_score = score
            
            # Add best match if found
            if best_match and best_match not in matched_symptoms:
                matched_symptoms.append(best_match)
            
            i += 1
    
    return matched_symptoms

# Function to predict disease based on symptoms with enhanced scoring
def predict_disease_from_symptoms(matched_symptoms):
    """Predict disease based on matched symptoms using enhanced scoring mechanism"""
    if not matched_symptoms or not DISEASE_SYMPTOMS:
        return None
    
    # Special rule-based mappings as per requirements
    fever_symptoms = {'fever', 'high_fever'}
    cold_symptoms = {'cold', 'chills'}
    cough_symptoms = {'cough'}
    headache_symptoms = {'headache'}
    
    # Check for specific symptom mappings
    if len(matched_symptoms) == 1:
        symptom = matched_symptoms[0]
        if symptom in fever_symptoms:
            return 'Viral Infection'
        elif symptom in cold_symptoms:
            return 'Common Cold'
        elif symptom in cough_symptoms:
            return 'Viral Respiratory Infection'
        elif symptom in headache_symptoms:
            return 'Sinusitis'  # Using Sinusitis for sinus as per requirement
    
    # Check for cluster of symptoms (fever, cold, cough, headache)
    # If any 2 or more of these symptoms are present, return Viral Infection
    fever_present = any(symptom in fever_symptoms for symptom in matched_symptoms)
    cold_present = any(symptom in cold_symptoms for symptom in matched_symptoms)
    cough_present = any(symptom in cough_symptoms for symptom in matched_symptoms)
    headache_present = any(symptom in headache_symptoms for symptom in matched_symptoms)
    
    # Count how many of the key symptoms are present
    key_symptoms_present = sum([fever_present, cold_present, cough_present, headache_present])
    
    # If 2 or more key symptoms are present, return Viral Infection
    if key_symptoms_present >= 2:
        return 'Viral Infection'
    
    # Special handling for common symptoms that are often misclassified
    common_symptom_mapping = {
        'fever': 'Viral Infection',
        'high_fever': 'Viral Infection',
        'cold': 'Common Cold',
        'chills': 'Common Cold',
        'cough': 'Viral Respiratory Infection',
        'headache': 'Migraine'
    }
    
    # If we have a single common symptom, map it directly
    if len(matched_symptoms) == 1:
        symptom = matched_symptoms[0]
        if symptom in common_symptom_mapping:
            return common_symptom_mapping[symptom]
    
    # Score each disease based on symptom matches
    disease_scores = {}
    
    for disease, disease_symptoms in DISEASE_SYMPTOMS.items():
        if not disease_symptoms:
            continue
            
        # Count matching symptoms
        matching_count = sum(1 for symptom in matched_symptoms if symptom in disease_symptoms)
        
        # Skip diseases with no matching symptoms
        if matching_count == 0:
            continue
        
        # Calculate match percentage (how many of the disease's symptoms are present)
        match_percentage = matching_count / len(disease_symptoms) if disease_symptoms else 0
        
        # Also consider how many of the user's symptoms match this disease (precision)
        user_match_percentage = matching_count / len(matched_symptoms) if matched_symptoms else 0
        
        # Enhanced scoring with bonus for common disease-symptom combinations
        common_disease_bonus = 0
        if disease == 'Common Cold' and any(symptom in ['fever', 'high_fever', 'cold', 'cough', 'chills', 'fatigue'] for symptom in matched_symptoms):
            common_disease_bonus = 0.2
        elif disease == 'Migraine' and 'headache' in matched_symptoms:
            common_disease_bonus = 0.15
        elif disease == 'Malaria' and any(symptom in ['fever', 'high_fever', 'chills'] for symptom in matched_symptoms):
            common_disease_bonus = 0.1
        elif disease == 'Typhoid' and any(symptom in ['fever', 'high_fever', 'chills'] for symptom in matched_symptoms):
            common_disease_bonus = 0.1
        
        # Combined score (weighted average - favor diseases that explain more user symptoms)
        combined_score = (match_percentage * 0.3) + (user_match_percentage * 0.7) + common_disease_bonus
        
        disease_scores[disease] = combined_score
    
    # Return disease with highest score
    if disease_scores:
        # Convert to list of items and find max
        items = list(disease_scores.items())
        if items:
            predicted_disease, _ = max(items, key=lambda x: x[1])
            # Only return if score is above minimum threshold
            if disease_scores[predicted_disease] > 0.1:
                return predicted_disease
    
    return None

# creating routes========================================

@app.route("/")
def index():
    return render_template("index.html")

# Define a route for the home page
@app.route('/predict', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        
        # Store original symptoms for preservation
        original_symptoms = symptoms
        
        # Validate symptoms input
        if not symptoms or symptoms.strip() == "" or symptoms == "Symptoms":
            message = "Please enter your symptoms. Symptoms should be comma-separated (e.g., itching, fever, headache)"
            return render_template('index.html', message=message, symptoms=symptoms)
        
        try:
            # Clean speech input if it comes from speech recognition
            symptoms = clean_speech_input(symptoms)
            
            # Use our new symptom matching approach for both speech and manual input
            # Find matching symptoms using fuzzy matching
            matched_symptoms = find_matching_symptoms(symptoms, threshold=0.7)  # 70% threshold for fuzzy matching
            
            # If no matches found, try to split by commas for manual input
            if not matched_symptoms:
                # Split the user's input into a list of symptoms (assuming they are comma-separated)
                user_symptoms = [s.strip() for s in symptoms.split(',')]
                # Remove any extra characters, if any
                user_symptoms = [symptom.strip("[]' \"") for symptom in user_symptoms]
                # Remove empty strings
                user_symptoms = [s for s in user_symptoms if s]
                
                # Try to find matches for each symptom
                for symptom in user_symptoms:
                    symptom_matches = find_matching_symptoms(symptom, threshold=0.6)  # Lower threshold for individual symptoms
                    matched_symptoms.extend(symptom_matches)
                
                # Remove duplicates while preserving order
                seen = set()
                matched_symptoms = [x for x in matched_symptoms if not (x in seen or seen.add(x))]
            
            # Handle case where no valid symptoms remain after cleaning
            # Allow single symptoms to proceed - remove the strict validation
            if not matched_symptoms:
                # For single symptoms, try to match directly
                single_symptom = symptoms.strip().lower()
                if single_symptom and single_symptom != "symptoms":
                    matched_symptoms = find_matching_symptoms(single_symptom, threshold=0.6)
                
                # If still no matches, show a more helpful message but allow processing
                if not matched_symptoms:
                    # Try to use the original symptoms as-is for the model
                    matched_symptoms = [symptoms.strip().lower()] if symptoms.strip() else []
            
            # Predict disease based on matched symptoms with special rules
            predicted_disease = predict_disease_from_symptoms(matched_symptoms)
            
            # If no disease predicted, try the model-based approach
            if not predicted_disease and matched_symptoms:
                predicted_disease = get_predicted_value(matched_symptoms)
            
            # If still no disease predicted, use a default for common symptoms
            if not predicted_disease:
                # Check for very common symptoms and provide a default disease
                common_symptoms = {'fever', 'headache', 'cough', 'cold', 'flu', 'high_fever'}
                if any(symptom in common_symptoms for symptom in matched_symptoms):
                    predicted_disease = 'Common Cold'  # Default fallback disease
            
            # Handle case where prediction fails
            if not predicted_disease:
                message = "Unable to predict disease. Please try again with different symptoms."
                return render_template('index.html', message=message, symptoms=original_symptoms)
            
            dis_des, my_precautions, medications, rec_diet, workout = helper(predicted_disease)
            
            # Get doctor recommendation
            doctor_recommendation = get_doctor_recommendation(predicted_disease)

            # Pass the original symptoms back to the template to preserve them
            return render_template('index.html', predicted_disease=predicted_disease, dis_des=dis_des,
                                   my_precautions=my_precautions, medications=medications, my_diet=rec_diet,
                                   workout=workout, doctor_recommendation=doctor_recommendation, 
                                   symptoms=original_symptoms)
        except Exception as e:
            message = f"An error occurred: {str(e)}. Please try again with valid symptoms."
            return render_template('index.html', message=message, symptoms=original_symptoms)

    return render_template('index.html')

# about view funtion and path
@app.route('/about')
def about():
    return render_template("about.html")
# contact view funtion and path
@app.route('/contact')
def contact():
    return render_template("contact.html")

# developer view funtion and path
@app.route('/developer')
def developer():
    return render_template("developer.html")

# about view funtion and path
@app.route('/blog')
def blog():
    return render_template("blog.html")


if __name__ == '__main__':
    app.run(debug=True)