import java.util.*;

/**
 * Disease prediction utility class
 */
public class DiseasePredictor {
    
    // Default fallback disease for common symptoms
    private static final String DEFAULT_FALLBACK_DISEASE = "Common Cold";
    
    // Common symptoms that should always return a disease prediction
    private static final Set<String> COMMON_SYMPTOMS = new HashSet<>(Arrays.asList(
        "fever", "headache", "cough", "cold", "flu"
    ));
    
    /**
     * Predict disease based on matched symptoms with fallback mechanisms
     * @param symptomMatcher The symptom matcher instance
     * @param matchedSymptoms List of matched symptoms
     * @param originalMethod Fallback method for disease prediction
     * @return Predicted disease
     */
    public static String predictDiseaseWithFallback(
            SymptomMatcher symptomMatcher, 
            List<String> matchedSymptoms, 
            java.util.function.Function<List<String>, String> originalMethod) {
        
        // Handle case where no valid symptoms remain after cleaning
        if (matchedSymptoms == null || matchedSymptoms.isEmpty()) {
            return null;
        }
        
        // Predict disease based on matched symptoms
        String predictedDisease = symptomMatcher.predictDiseaseFromSymptoms(matchedSymptoms);
        
        // Handle case where prediction fails - ensure at least one disease is returned
        if (predictedDisease == null || predictedDisease.isEmpty()) {
            // Fallback: use the original method if our new method fails
            predictedDisease = originalMethod.apply(matchedSymptoms);
        }
        
        // If still no disease predicted, use a default for common symptoms
        if (predictedDisease == null || predictedDisease.isEmpty()) {
            // Check for very common symptoms and provide a default disease
            boolean hasCommonSymptom = matchedSymptoms.stream()
                    .anyMatch(symptom -> COMMON_SYMPTOMS.contains(symptom.toLowerCase()));
            
            if (hasCommonSymptom) {
                predictedDisease = DEFAULT_FALLBACK_DISEASE; // Default fallback disease
            }
        }
        
        return predictedDisease;
    }
    
    /**
     * Get doctor recommendation based on disease
     * @param disease The predicted disease
     * @return Recommended doctor specialist
     */
    public static String getDoctorRecommendation(String disease) {
        if (disease == null || disease.isEmpty()) {
            return "General Physician";
        }
        
        // Mapping of diseases to specialists
        Map<String, String> doctorMapping = new HashMap<>();
        
        // Fever and general symptoms
        doctorMapping.put("Fungal infection", "Dermatologist");
        doctorMapping.put("Allergy", "Allergist");
        doctorMapping.put("Common Cold", "General Physician");
        doctorMapping.put("Malaria", "General Physician");
        doctorMapping.put("Dengue", "General Physician");
        doctorMapping.put("Typhoid", "General Physician");
        doctorMapping.put("Chicken pox", "General Physician");
        doctorMapping.put("AIDS", "Infectious Disease Specialist");
        doctorMapping.put("Tuberculosis", "Pulmonologist");
        doctorMapping.put("hepatitis A", "Hepatologist");
        doctorMapping.put("Hepatitis B", "Hepatologist");
        doctorMapping.put("Hepatitis C", "Hepatologist");
        doctorMapping.put("Hepatitis D", "Hepatologist");
        doctorMapping.put("Hepatitis E", "Hepatologist");
        doctorMapping.put("Alcoholic hepatitis", "Hepatologist");
        
        // Heart related
        doctorMapping.put("Heart attack", "Cardiologist");
        doctorMapping.put("Hypertension", "Cardiologist");
        doctorMapping.put("Bradycardia", "Cardiologist");
        doctorMapping.put("Tachycardia", "Cardiologist");
        
        // Digestive system
        doctorMapping.put("GERD", "Gastroenterologist");
        doctorMapping.put("Chronic cholestasis", "Gastroenterologist");
        doctorMapping.put("Peptic ulcer disease", "Gastroenterologist");
        doctorMapping.put("Gastroenteritis", "Gastroenterologist");
        doctorMapping.put("Jaundice", "Gastroenterologist");
        doctorMapping.put("Diabetes", "Endocrinologist");
        doctorMapping.put("Hyperthyroidism", "Endocrinologist");
        doctorMapping.put("Hypothyroidism", "Endocrinologist");
        doctorMapping.put("Hypoglycemia", "Endocrinologist");
        
        // Respiratory system
        doctorMapping.put("Bronchial Asthma", "Pulmonologist");
        doctorMapping.put("Pneumonia", "Pulmonologist");
        
        // Neurological
        doctorMapping.put("Migraine", "Neurologist");
        doctorMapping.put("Cervical spondylosis", "Orthopedist");
        doctorMapping.put("Paralysis (brain hemorrhage)", "Neurologist");
        doctorMapping.put("(vertigo) Paroymsal  Positional Vertigo", "ENT Specialist");
        
        // Musculoskeletal
        doctorMapping.put("Osteoarthristis", "Orthopedist");
        doctorMapping.put("Arthritis", "Rheumatologist");
        
        // Skin conditions
        doctorMapping.put("Acne", "Dermatologist");
        doctorMapping.put("Impetigo", "Dermatologist");
        doctorMapping.put("Psoriasis", "Dermatologist");
        
        // Other systems
        doctorMapping.put("Urinary tract infection", "Urologist");
        doctorMapping.put("Dimorphic hemmorhoids(piles)", "Proctologist");
        
        // Mental health
        doctorMapping.put("Depression", "Psychiatrist");
        doctorMapping.put("Anxiety", "Psychiatrist");
        
        // Return specific doctor or default to General Physician
        return doctorMapping.getOrDefault(disease, "General Physician");
    }
}