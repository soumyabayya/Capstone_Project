from flask import Flask, request, render_template, jsonify
import numpy as np
import pandas as pd
import pickle
import ast
import os

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

# load model===========================================
svc = pickle.load(open(os.path.join(BASE_DIR, 'models/svc.pkl'), 'rb'))

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
            if col.startswith('Symptom_') and pd.notna(row[col]):
                symptom = str(row[col]).strip().lower()
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
    import re
    
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation (commas, periods, etc.)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # Replace multiple spaces with single space and trim
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# Function to calculate similarity between two strings (Levenshtein distance)
def calculate_similarity(str1, str2):
    """Calculate similarity ratio between two strings using Levenshtein distance"""
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

# Function to find best matching symptoms using fuzzy matching
def find_matching_symptoms(user_input, threshold=0.8):
    """Find matching symptoms using fuzzy matching with threshold (0.0-1.0)"""
    if not user_input or not DATASET_SYMPTOMS:
        return []
    
    # Normalize user input
    normalized_input = normalize_input(user_input)
    
    # Split input into potential symptoms
    input_symptoms = [s.strip() for s in normalized_input.split() if s.strip()]
    
    # Try to match multi-word phrases first
    matched_symptoms = []
    
    # Check for exact matches first
    if normalized_input in DATASET_SYMPTOMS:
        matched_symptoms.append(normalized_input)
    
    # Try fuzzy matching for each input symptom
    for input_symptom in input_symptoms:
        best_match = None
        best_score = 0
        
        # Check against all dataset symptoms
        for dataset_symptom in DATASET_SYMPTOMS:
            # Calculate similarity
            score = calculate_similarity(input_symptom, dataset_symptom)
            
            # If score is above threshold and better than current best
            if score >= threshold and score > best_score:
                best_match = dataset_symptom
                best_score = score
        
        # Add best match if found
        if best_match and best_match not in matched_symptoms:
            matched_symptoms.append(best_match)
    
    return matched_symptoms

# Function to predict disease based on symptoms with scoring
def predict_disease_from_symptoms(matched_symptoms):
    """Predict disease based on matched symptoms using scoring mechanism"""
    if not matched_symptoms or not DISEASE_SYMPTOMS:
        return None
    
    # Score each disease based on symptom matches
    disease_scores = {}
    
    for disease, disease_symptoms in DISEASE_SYMPTOMS.items():
        if not disease_symptoms:
            continue
            
        # Count matching symptoms
        matching_count = sum(1 for symptom in matched_symptoms if symptom in disease_symptoms)
        
        # Calculate match percentage
        match_percentage = matching_count / len(disease_symptoms) if disease_symptoms else 0
        
        # Also consider how many of the user's symptoms match this disease
        user_match_percentage = matching_count / len(matched_symptoms) if matched_symptoms else 0
        
        # Combined score (weighted average)
        combined_score = (match_percentage * 0.5) + (user_match_percentage * 0.5)
        
        disease_scores[disease] = combined_score
    
    # Return disease with highest score
    if disease_scores:
        predicted_disease = max(disease_scores, key=disease_scores.get)
        # Only return if score is above minimum threshold
        if disease_scores[predicted_disease] > 0.1:
            return predicted_disease
    
    return None

# Disease name mapping to handle mismatches between model predictions and CSV data
def normalize_disease_name(disease_name):
    """Normalize disease names to match CSV file format"""
    disease_name = disease_name.strip()  # Remove leading/trailing spaces
    
    # Map model disease names to CSV disease names
    disease_mapping = {
        'Peptic ulcer diseae': 'Peptic ulcer disease',  # Fix typo
        'Diabetes ': 'Diabetes',  # Remove trailing space
        'Hypertension ': 'Hypertension',  # Remove trailing space
    }
    
    return disease_mapping.get(disease_name, disease_name)

def helper(dis):
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
    pre_rows = precautions[precautions['Disease'] == dis_normalized][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
    my_precautions = []
    if len(pre_rows) > 0:
        # Convert to list and get first row
        pre_list = list(pre_rows)
        if pre_list:
            pre_series = pre_list[0]
            # Convert series to list of values
            pre_values = list(pre_series) if hasattr(pre_series, '__iter__') and not isinstance(pre_series, str) else [pre_series]
            my_precautions = [p for p in pre_values if pd.notna(p) and str(p).strip()]

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

# Model Prediction function - enhanced version
def get_predicted_value(patient_symptoms):
    # First try the new symptom matching approach
    if patient_symptoms:
        # Use our new prediction method
        predicted_disease = predict_disease_from_symptoms(patient_symptoms)
        if predicted_disease:
            return predicted_disease
    
    # Fallback to original method
    input_vector = np.zeros(len(symptoms_dict))
    for item in patient_symptoms:
        if item in symptoms_dict:
            input_vector[symptoms_dict[item]] = 1
    prediction = svc.predict([input_vector])[0]
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
        
        # Default recommendation
        'default': 'General Physician'
    }
    
    # Return specific doctor or default to General Physician
    return doctor_mapping.get(disease, doctor_mapping['default'])

# Function to clean speech input (same as JavaScript implementation)
def clean_speech_input(text):
    """Clean speech input to match JavaScript processing"""
    import re
    
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and special characters
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # Replace multiple spaces with single space and trim
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# creating routes========================================

@app.route("/")
def index():
    return render_template("index.html")

# Define a route for the home page
@app.route('/predict', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        print(symptoms)
        
        # Validate symptoms input
        if not symptoms or symptoms.strip() == "" or symptoms == "Symptoms":
            message = "Please enter your symptoms. Symptoms should be comma-separated (e.g., itching, fever, headache)"
            return render_template('index.html', message=message)
        
        try:
            # Clean speech input if it comes from speech recognition
            symptoms = clean_speech_input(symptoms)
            
            # Split the user's input into a list of symptoms (assuming they are comma-separated)
            user_symptoms = [s.strip() for s in symptoms.split(',')]
            # Remove any extra characters, if any
            user_symptoms = [symptom.strip("[]' \"") for symptom in user_symptoms]
            # Remove empty strings
            user_symptoms = [s for s in user_symptoms if s]
            
            if not user_symptoms:
                message = "Please enter valid symptoms. Symptoms should be comma-separated (e.g., itching, fever, headache)"
                return render_template('index.html', message=message)
            
            # Validate that symptoms exist in the dictionary
            invalid_symptoms = [s for s in user_symptoms if s not in symptoms_dict]
            if invalid_symptoms:
                message = f"Invalid symptoms detected: {', '.join(invalid_symptoms)}. Please check the spelling."
                return render_template('index.html', message=message)
            
            # Handle case where no valid symptoms remain after cleaning
            if not user_symptoms:
                message = "No valid symptoms detected. Please try again with different symptoms."
                return render_template('index.html', message=message)
            
            predicted_disease = get_predicted_value(user_symptoms)
            
            # Handle case where prediction fails
            if not predicted_disease:
                message = "Unable to predict disease. Please try again with different symptoms."
                return render_template('index.html', message=message)
            
            dis_des, my_precautions, medications, rec_diet, workout = helper(predicted_disease)
            
            # Get doctor recommendation
            doctor_recommendation = get_doctor_recommendation(predicted_disease)

            return render_template('index.html', predicted_disease=predicted_disease, dis_des=dis_des,
                                   my_precautions=my_precautions, medications=medications, my_diet=rec_diet,
                                   workout=workout, doctor_recommendation=doctor_recommendation)
        except Exception as e:
            message = f"An error occurred: {str(e)}. Please try again with valid symptoms."
            return render_template('index.html', message=message)

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