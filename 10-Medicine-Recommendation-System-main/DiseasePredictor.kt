/**
 * Disease prediction utility class
 */
object DiseasePredictor {
    
    // Default fallback disease for common symptoms
    private const val DEFAULT_FALLBACK_DISEASE = "Common Cold"
    
    // Common symptoms that should always return a disease prediction
    private val COMMON_SYMPTOMS = setOf("fever", "headache", "cough", "cold", "flu")
    
    /**
     * Predict disease based on matched symptoms with fallback mechanisms
     * @param symptomMatcher The symptom matcher instance
     * @param matchedSymptoms List of matched symptoms
     * @param originalMethod Fallback method for disease prediction
     * @return Predicted disease
     */
    fun predictDiseaseWithFallback(
        symptomMatcher: SymptomMatcher,
        matchedSymptoms: List<String>?,
        originalMethod: (List<String>) -> String?
    ): String? {
        
        // Handle case where no valid symptoms remain after cleaning
        if (matchedSymptoms.isNullOrEmpty()) {
            return null
        }
        
        // Predict disease based on matched symptoms
        var predictedDisease = symptomMatcher.predictDiseaseFromSymptoms(matchedSymptoms)
        
        // Handle case where prediction fails - ensure at least one disease is returned
        if (predictedDisease.isNullOrBlank()) {
            // Fallback: use the original method if our new method fails
            predictedDisease = originalMethod(matchedSymptoms)
        }
        
        // If still no disease predicted, use a default for common symptoms
        if (predictedDisease.isNullOrBlank()) {
            // Check for very common symptoms and provide a default disease
            val hasCommonSymptom = matchedSymptoms.any { 
                it.lowercase() in COMMON_SYMPTOMS 
            }
            
            if (hasCommonSymptom) {
                predictedDisease = DEFAULT_FALLBACK_DISEASE // Default fallback disease
            }
        }
        
        return predictedDisease
    }
    
    /**
     * Get doctor recommendation based on disease
     * @param disease The predicted disease
     * @return Recommended doctor specialist
     */
    fun getDoctorRecommendation(disease: String?): String {
        if (disease.isNullOrBlank()) {
            return "General Physician"
        }
        
        // Mapping of diseases to specialists
        val doctorMapping = mapOf(
            // Fever and general symptoms
            "Fungal infection" to "Dermatologist",
            "Allergy" to "Allergist",
            "Common Cold" to "General Physician",
            "Malaria" to "General Physician",
            "Dengue" to "General Physician",
            "Typhoid" to "General Physician",
            "Chicken pox" to "General Physician",
            "AIDS" to "Infectious Disease Specialist",
            "Tuberculosis" to "Pulmonologist",
            "hepatitis A" to "Hepatologist",
            "Hepatitis B" to "Hepatologist",
            "Hepatitis C" to "Hepatologist",
            "Hepatitis D" to "Hepatologist",
            "Hepatitis E" to "Hepatologist",
            "Alcoholic hepatitis" to "Hepatologist",
            
            // Heart related
            "Heart attack" to "Cardiologist",
            "Hypertension" to "Cardiologist",
            "Bradycardia" to "Cardiologist",
            "Tachycardia" to "Cardiologist",
            
            // Digestive system
            "GERD" to "Gastroenterologist",
            "Chronic cholestasis" to "Gastroenterologist",
            "Peptic ulcer disease" to "Gastroenterologist",
            "Gastroenteritis" to "Gastroenterologist",
            "Jaundice" to "Gastroenterologist",
            "Diabetes" to "Endocrinologist",
            "Hyperthyroidism" to "Endocrinologist",
            "Hypothyroidism" to "Endocrinologist",
            "Hypoglycemia" to "Endocrinologist",
            
            // Respiratory system
            "Bronchial Asthma" to "Pulmonologist",
            "Pneumonia" to "Pulmonologist",
            
            // Neurological
            "Migraine" to "Neurologist",
            "Cervical spondylosis" to "Orthopedist",
            "Paralysis (brain hemorrhage)" to "Neurologist",
            "(vertigo) Paroymsal  Positional Vertigo" to "ENT Specialist",
            
            // Musculoskeletal
            "Osteoarthristis" to "Orthopedist",
            "Arthritis" to "Rheumatologist",
            
            // Skin conditions
            "Acne" to "Dermatologist",
            "Impetigo" to "Dermatologist",
            "Psoriasis" to "Dermatologist",
            
            // Other systems
            "Urinary tract infection" to "Urologist",
            "Dimorphic hemmorhoids(piles)" to "Proctologist",
            
            // Mental health
            "Depression" to "Psychiatrist",
            "Anxiety" to "Psychiatrist"
        )
        
        // Return specific doctor or default to General Physician
        return doctorMapping[disease] ?: "General Physician"
    }
}