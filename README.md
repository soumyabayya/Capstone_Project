# Symptom Checker and Doctor Recommendation 

## Overview
The Symptom Checker and Doctor Recommendation is an AI-powered healthcare application that predicts diseases based on symptoms and provides comprehensive medical recommendations including medications, precautions, diets, workouts, and doctor specializations. The system uses machine learning algorithms to analyze symptoms and provide accurate disease predictions along with personalized healthcare advice.

## Features
- **Symptom-based Disease Prediction**: Predicts diseases based on user-input symptoms using machine learning models
- **Speech Recognition**: Allows users to input symptoms via voice commands for accessibility
- **Comprehensive Medical Recommendations**: Provides detailed information including:
  - Disease description
  - Recommended medications
  - Necessary precautions
  - Suggested diets
  - Appropriate workouts
  - Doctor specialization recommendations
- **Fuzzy Matching**: Intelligent symptom matching with support for common mispellings and variations
- **User-friendly Interface**: Clean, responsive web interface built with Flask

## Technologies Used
- **Backend**: Python, Flask
- **Machine Learning**: Scikit-learn (RandomForestClassifier, SVM)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Data Processing**: Pandas, NumPy
- **Speech Recognition**: Web Speech API
- **Data Storage**: CSV files

## Dataset
The system uses a comprehensive medical dataset containing:
- Symptom-disease relationships
- Disease descriptions
- Medication recommendations
- Precautionary measures
- Dietary suggestions
- Workout recommendations
- Doctor specialization mappings

The dataset includes information on over 40 diseases with their associated symptoms and recommendations.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/medicine-recommendation-system.git
   cd medicine-recommendation-system
   ```

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   If requirements.txt is not available, install the main dependencies:
   ```bash
   pip install flask pandas numpy scikit-learn
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Access the application**:
   Open your web browser and go to `http://localhost:5000`

## Usage

1. **Manual Input**: Type your symptoms in the input field, separated by commas (e.g., "fever, cough, headache")
2. **Speech Recognition**: Click the "Start Speech Recognition" button and speak your symptoms
3. **Get Recommendations**: Click "Predict" to receive disease predictions and medical recommendations
4. **Consult Specialist**: Based on the predicted disease, the system recommends the appropriate medical specialist

## Project Structure
```
medicine-recommendation-system/
│
├── dataset/
│   ├── symtoms_df.csv          # Symptom-disease mapping
│   ├── description.csv         # Disease descriptions
│   ├── medications.csv         # Medication recommendations
│   ├── precautions_df.csv      # Precautionary measures
│   ├── diets.csv               # Dietary recommendations
│   └── workout_df.csv          # Workout suggestions
│
├── models/
│   ├── disease_prediction_model.pkl  # Trained ML model
│   └── svc.pkl                  # Alternative ML model
│
├── templates/
│   ├── index.html              # Main application page
│   ├── base.html               # Base template
│   ├── about.html              # About page
│   ├── contact.html            # Contact page
│   ├── developer.html          # Developer information
│   └── blog.html               # Blog page
│
├── static/
│   └── (CSS, JS, images)
│
├── main.py                     # Main application file
├── train_model.py              # Model training script
└── README.md
```

## Machine Learning Models
The system implements two machine learning approaches:
1. **RandomForestClassifier**: Primary model with enhanced accuracy
2. **Support Vector Machine (SVM)**: Fallback model for compatibility

The models are trained on symptom-disease relationships to predict diseases based on input symptoms.

## Special Features

### Enhanced Symptom Matching
- Fuzzy matching algorithms to handle variations in symptom descriptions
- Support for common mispellings and pronunciation errors
- Multi-word symptom recognition (e.g., "sore throat", "chest pain")

### Rule-based Disease Prediction
- Special handling for common symptom clusters (fever, cold, cough, headache)
- Direct mappings for frequently occurring symptoms
- Confidence scoring for predictions

### Doctor Recommendation System
- Maps predicted diseases to appropriate medical specialists
- Covers 40+ diseases and 20+ medical specializations
- Provides clear guidance on which doctor to consult

## Contributing
1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request


## Acknowledgments
- Medical datasets compiled from various public health resources
- Machine learning models implemented using scikit-learn
- UI designed with Bootstrap framework
