# Medicine Recommendation System - Integration Instructions

## Overview
This document provides instructions for integrating the updated Java/Kotlin classes, XML layout, and related components into your medicine recommendation system.

## File Structure
```
project/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   ├── SpeechRecognitionActivity.java
│   │   │   ├── SpeechProcessor.java
│   │   │   ├── SymptomMatcher.java
│   │   │   ├── SymptomData.java
│   │   │   ├── DiseasePredictor.java
│   │   │   └── DatasetLoader.java
│   │   ├── kotlin/
│   │   │   ├── SpeechRecognitionActivity.kt
│   │   │   ├── SpeechProcessor.kt
│   │   │   ├── SymptomMatcher.kt
│   │   │   ├── SymptomData.kt
│   │   │   └── DiseasePredictor.kt
│   │   └── res/
│   │       └── layout/
│   │           └── activity_main.xml
└── datasets/
    ├── symtoms_df.csv
    ├── description.csv
    ├── medications.csv
    ├── precautions_df.csv
    ├── diets.csv
    └── workout_df.csv
```

## Java/Kotlin Classes Integration

### 1. SpeechRecognitionActivity.java
**Purpose**: Implements continuous speech recognition for unlimited symptom capture.

**Integration Steps**:
1. Copy `SpeechRecognitionActivity.java` to your project's `src/main/java/` directory
2. Ensure `SpeechProcessor.java` is available in the same directory
3. Update your `AndroidManifest.xml` with required permissions:
```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
```
4. Register the activity in `AndroidManifest.xml`:
```xml
<activity android:name=".SpeechRecognitionActivity" />
```

### 2. SpeechProcessor.java
**Purpose**: Handles speech input cleaning and text normalization.

**Integration Steps**:
1. Copy `SpeechProcessor.java` to your project's `src/main/java/` directory
2. Use in your speech recognition handler:
```java
String cleanedText = SpeechProcessor.cleanSpeechInput(rawSpeechText);
String normalizedText = SpeechProcessor.normalizeInput(userInput);
```

### 2. SymptomData.java
**Purpose**: Data class for holding disease and symptom information.

**Integration Steps**:
1. Copy `SymptomData.java` to your project's `src/main/java/` directory
2. Use when loading dataset information

### 3. SymptomMatcher.java
**Purpose**: Implements symptom matching with fuzzy matching and disease prediction.

**Integration Steps**:
1. Copy `SymptomMatcher.java` to your project's `src/main/java/` directory
2. Initialize with dataset:
```java
SymptomMatcher matcher = new SymptomMatcher();
List<SymptomData> symptomsData = DatasetLoader.loadSymptomsFromCSV("path/to/symtoms_df.csv");
matcher.initializeDatasetMappings(symptomsData);
```
3. Use for matching:
```java
List<String> matchedSymptoms = matcher.findMatchingSymptoms(userInput);
String predictedDisease = matcher.predictDiseaseFromSymptoms(matchedSymptoms);
```

### 4. DiseasePredictor.java
**Purpose**: Handles disease prediction with fallback mechanisms and doctor recommendations.

**Integration Steps**:
1. Copy `DiseasePredictor.java` to your project's `src/main/java/` directory
2. Use for prediction with fallback:
```java
String predictedDisease = DiseasePredictor.predictDiseaseWithFallback(
    symptomMatcher, 
    matchedSymptoms, 
    this::originalPredictionMethod
);
```
3. Get doctor recommendation:
```java
String doctorRecommendation = DiseasePredictor.getDoctorRecommendation(predictedDisease);
```

### 5. DatasetLoader.java
**Purpose**: Loads dataset information from CSV files.

**Integration Steps**:
1. Copy `DatasetLoader.java` to your project's `src/main/java/` directory
2. Load datasets:
```java
List<SymptomData> symptomsData = DatasetLoader.loadSymptomsFromCSV("datasets/symtoms_df.csv");
Map<String, String> descriptions = DatasetLoader.loadDescriptionsFromCSV("datasets/description.csv");
Map<String, List<String>> medications = DatasetLoader.loadMedicationsFromCSV("datasets/medications.csv");
Map<String, List<String>> precautions = DatasetLoader.loadPrecautionsFromCSV("datasets/precautions_df.csv");
Map<String, List<String>> diets = DatasetLoader.loadDietsFromCSV("datasets/diets.csv");
Map<String, List<String>> workouts = DatasetLoader.loadWorkoutsFromCSV("datasets/workout_df.csv");
```

## XML Layout Integration

### activity_main.xml
**Purpose**: Main UI layout with speech recognition and results display.

**Integration Steps**:
1. Copy `activity_main.xml` to your project's `src/main/res/layout/` directory
2. Update your `MainActivity.java` to reference the new UI elements:
```java
// Find views
EditText symptomsInput = findViewById(R.id.symptomsInput);
Button startSpeechButton = findViewById(R.id.startSpeechButton);
TextView transcriptionText = findViewById(R.id.transcriptionText);
Button predictButton = findViewById(R.id.predictButton);
ScrollView resultsContainer = findViewById(R.id.resultsContainer);

// Results views
TextView diseaseResult = findViewById(R.id.diseaseResult);
TextView descriptionResult = findViewById(R.id.descriptionResult);
// ... other result views
```

## Key Features Implemented

### 1. Symptom Matching Improvements
- **Dataset Loading**: Symptoms are loaded directly from the dataset instead of hardcoded lists
- **Input Normalization**: Text is normalized by removing punctuation, converting to lowercase, and trimming spaces
- **Multi-word Symptom Support**: Supports symptoms like "sore throat", "body pain", etc.
- **Fuzzy Matching**: Uses Levenshtein distance for 70-80% text similarity matching
- **Example Mappings**: 
  - "feaver" → "fever"
  - "couh" → "cough" 
  - "colt" → "cold"

### 2. Disease Prediction Improvements
- **Scoring Mechanism**: Diseases are scored based on symptom match percentage
- **Fallback Mechanisms**: Ensures at least one disease is returned even with minimal symptoms
- **Common Symptom Handling**: Provides default predictions for common symptoms like "fever"

### 3. Input Handling Improvements
- **Unified Processing**: Both speech and manual input use the same matching logic
- **No Hardcoded Symptoms**: Always relies on dataset symptoms

### 4. Output Improvements
- **Complete Information**: Returns Disease, Medications, Precautions, Workouts, Diet, and Doctor Recommendation

## Usage Example

```java
// Initialize symptom matcher
SymptomMatcher symptomMatcher = new SymptomMatcher();
List<SymptomData> symptomsData = DatasetLoader.loadSymptomsFromCSV("datasets/symtoms_df.csv");
symptomMatcher.initializeDatasetMappings(symptomsData);

// Process user input (speech or manual)
String userInput = "feaver and couh"; // Example user input
String cleanedInput = SpeechProcessor.cleanSpeechInput(userInput);

// Find matching symptoms
List<String> matchedSymptoms = symptomMatcher.findMatchingSymptoms(cleanedInput);

// Predict disease with fallback
String predictedDisease = DiseasePredictor.predictDiseaseWithFallback(
    symptomMatcher,
    matchedSymptoms,
    originalMethod -> {
        // Your original prediction method here
        return "Common Cold";
    }
);

// Get doctor recommendation
String doctorRecommendation = DiseasePredictor.getDoctorRecommendation(predictedDisease);

// Load additional information
Map<String, String> descriptions = DatasetLoader.loadDescriptionsFromCSV("datasets/description.csv");
Map<String, List<String>> medications = DatasetLoader.loadMedicationsFromCSV("datasets/medications.csv");
// ... load other datasets

// Display results in UI
```

## Testing Recommendations

1. **Speech Input Testing**:
   - Test with common mispronunciations: "feaver" → "fever", "couh" → "cough"
   - Test multi-word symptoms: "sore throat", "body pain"
   - Test mixed input: "fever, headache, and sore throat"

2. **Manual Input Testing**:
   - Test with exact symptom names from dataset
   - Test with variations and typos
   - Test with comma-separated symptoms

3. **Edge Cases**:
   - Empty or null input
   - Single symptom input (e.g., just "fever")
   - Invalid symptoms that don't match dataset
   - Very long input with many symptoms

## Performance Considerations

1. **Dataset Loading**: Load datasets once at application startup, not for each prediction
2. **Caching**: Consider caching frequently accessed data
3. **Memory Management**: SymptomMatcher maintains in-memory mappings for fast lookup
4. **Threading**: Perform dataset loading and heavy processing on background threads

## Troubleshooting

1. **No Symptoms Matched**: 
   - Verify dataset files are correctly loaded
   - Check input normalization is working correctly
   - Test with exact symptom names from dataset

2. **Incorrect Disease Prediction**:
   - Verify symptom-to-disease mappings are correct
   - Check scoring algorithm parameters
   - Test with known symptom combinations

3. **UI Issues**:
   - Ensure all view IDs match between XML and Java code
   - Verify proper visibility toggling for results container
   - Check scroll view behavior with long content

## Dependencies

Ensure your project includes:
- Android Material Components
- AndroidX libraries
- Proper permissions for speech recognition in AndroidManifest.xml:
```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
```