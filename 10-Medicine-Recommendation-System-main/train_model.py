import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import MultiLabelBinarizer
import pickle
import re

def load_and_preprocess_data():
    """Load and preprocess the dataset"""
    # Load the dataset
    df = pd.read_csv('dataset/symtoms_df.csv')
    
    # Clean symptom columns - remove leading spaces
    symptom_columns = [col for col in df.columns if col.startswith('Symptom_')]
    for col in symptom_columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Remove rows where all symptoms are 'nan'
    df = df[df[symptom_columns].apply(lambda x: (x != 'nan').any(), axis=1)]
    
    return df

def create_symptom_mapping(df):
    """Create a mapping of all unique symptoms"""
    symptom_columns = [col for col in df.columns if col.startswith('Symptom_')]
    all_symptoms = set()
    
    for col in symptom_columns:
        symptoms = df[col].unique()
        all_symptoms.update([symptom for symptom in symptoms if symptom != 'nan'])
    
    # Create symptom to index mapping
    symptom_to_index = {symptom: idx for idx, symptom in enumerate(sorted(all_symptoms))}
    return symptom_to_index

def create_feature_matrix(df, symptom_to_index):
    """Convert symptoms to multi-hot encoded feature matrix"""
    symptom_columns = [col for col in df.columns if col.startswith('Symptom_')]
    num_symptoms = len(symptom_to_index)
    num_samples = len(df)
    
    # Initialize feature matrix
    X = np.zeros((num_samples, num_symptoms))
    
    # Fill feature matrix
    for i, row in df.iterrows():
        for col in symptom_columns:
            symptom = row[col]
            if symptom != 'nan' and symptom in symptom_to_index:
                X[i, symptom_to_index[symptom]] = 1
    
    return X

def train_model():
    """Train the disease prediction model"""
    # Load and preprocess data
    df = load_and_preprocess_data()
    
    # Create symptom mapping
    symptom_to_index = create_symptom_mapping(df)
    
    # Create feature matrix
    X = create_feature_matrix(df, symptom_to_index)
    
    # Target variable (disease)
    y = df['Disease'].values
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest Classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save the model and symptom mapping
    with open('models/disease_prediction_model.pkl', 'wb') as f:
        pickle.dump({
            'model': model,
            'symptom_to_index': symptom_to_index,
            'index_to_symptom': {v: k for k, v in symptom_to_index.items()},
            'diseases': np.unique(y)
        }, f)
    
    print("\nModel saved successfully!")
    
    # Create symptom-disease mapping for reference
    symptom_disease_mapping = {}
    for _, row in df.iterrows():
        disease = row['Disease']
        for col in [c for c in df.columns if c.startswith('Symptom_')]:
            symptom = row[col]
            if symptom != 'nan':
                if symptom not in symptom_disease_mapping:
                    symptom_disease_mapping[symptom] = set()
                symptom_disease_mapping[symptom].add(disease)
    
    # Save symptom-disease mapping
    mapping_df = pd.DataFrame([
        {'Symptom': symptom, 'Diseases': ', '.join(diseases)}
        for symptom, diseases in symptom_disease_mapping.items()
    ])
    mapping_df.to_csv('dataset/symptom_disease_mapping.csv', index=False)
    print("Symptom-disease mapping saved successfully!")

if __name__ == "__main__":
    train_model()