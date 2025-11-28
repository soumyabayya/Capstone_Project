import kotlin.math.max
import kotlin.math.min

/**
 * Symptom matching utility class for finding matching symptoms using fuzzy matching
 */
class SymptomMatcher {
    
    // Threshold for fuzzy matching (0.0-1.0)
    private val DEFAULT_THRESHOLD = 0.7
    
    // Dataset symptoms for fast lookup
    private val datasetSymptoms = mutableSetOf<String>()
    
    // Map symptoms to diseases
    private val symptomToDiseases = mutableMapOf<String, MutableSet<String>>()
    
    // Map diseases to their symptoms
    private val diseaseSymptoms = mutableMapOf<String, MutableSet<String>>()
    
    /**
     * Initialize dataset symptoms and mappings
     * @param symptomsData List of symptom data from dataset
     */
    fun initializeDatasetMappings(symptomsData: List<SymptomData>) {
        // Clear existing data
        datasetSymptoms.clear()
        symptomToDiseases.clear()
        diseaseSymptoms.clear()
        
        // Process the symptoms dataset
        for (data in symptomsData) {
            val disease = data.disease
            
            // Collect all symptoms for this disease
            val diseaseSymptomsSet = mutableSetOf<String>()
            
            // Add all symptoms for this disease
            for (symptom in data.symptoms) {
                if (!symptom.isNullOrBlank()) {
                    val normalizedSymptom = symptom.trim().lowercase()
                    
                    // Add to dataset symptoms set
                    datasetSymptoms.add(normalizedSymptom)
                    
                    // Map symptom to disease
                    symptomToDiseases.getOrPut(normalizedSymptom) { mutableSetOf() }.add(disease)
                    
                    // Add to disease symptoms list
                    diseaseSymptomsSet.add(normalizedSymptom)
                }
            }
            
            // Map disease to its symptoms
            diseaseSymptoms[disease] = diseaseSymptomsSet
        }
    }
    
    /**
     * Calculate similarity between two strings using Levenshtein distance
     * @param str1 First string
     * @param str2 Second string
     * @return Similarity ratio (0.0-1.0)
     */
    fun calculateSimilarity(str1: String?, str2: String?): Double {
        if (str1 == null || str2 == null) {
            return 0.0
        }
        
        // Convert to lowercase for comparison
        val s1 = str1.lowercase()
        val s2 = str2.lowercase()
        
        // If strings are identical, return 1.0
        if (s1 == s2) {
            return 1.0
        }
        
        // Calculate Levenshtein distance
        val len1 = s1.length
        val len2 = s2.length
        
        // Create matrix
        val matrix = Array(len1 + 1) { IntArray(len2 + 1) }
        
        // Initialize first row and column
        for (i in 0..len1) {
            matrix[i][0] = i
        }
        for (j in 0..len2) {
            matrix[0][j] = j
        }
        
        // Fill matrix
        for (i in 1..len1) {
            for (j in 1..len2) {
                val cost = if (s1[i - 1] == s2[j - 1]) 0 else 1
                matrix[i][j] = min(
                    min(matrix[i - 1][j] + 1,      // deletion
                        matrix[i][j - 1] + 1),      // insertion
                    matrix[i - 1][j - 1] + cost)    // substitution
            }
        }
        
        // Calculate similarity ratio
        val distance = matrix[len1][len2]
        val maxLen = max(len1, len2)
        
        return if (maxLen == 0) 1.0 else 1.0 - (distance.toDouble() / maxLen)
    }
    
    /**
     * Find matching symptoms using fuzzy matching
     * @param userInput User input text
     * @param threshold Similarity threshold (0.0-1.0)
     * @return List of matching symptoms
     */
    fun findMatchingSymptoms(userInput: String?, threshold: Double = DEFAULT_THRESHOLD): List<String> {
        val matchedSymptoms = mutableListOf<String>()
        
        if (userInput.isNullOrBlank() || datasetSymptoms.isEmpty()) {
            return matchedSymptoms
        }
        
        // Normalize user input
        val normalizedInput = SpeechProcessor.normalizeInput(userInput)
        
        // Split input into potential symptoms
        val inputSymptoms = normalizedInput.split("\\s+".toRegex())
            .map { it.trim() }
            .filter { it.isNotEmpty() }
        
        // Try to match multi-word phrases first
        if (datasetSymptoms.contains(normalizedInput)) {
            matchedSymptoms.add(normalizedInput)
        }
        
        // Try fuzzy matching for each input symptom
        for (inputSymptom in inputSymptoms) {
            var bestMatch: String? = null
            var bestScore = 0.0
            
            // Check against all dataset symptoms
            for (datasetSymptom in datasetSymptoms) {
                // Calculate similarity
                val score = calculateSimilarity(inputSymptom, datasetSymptom)
                
                // If score is above threshold and better than current best
                if (score >= threshold && score > bestScore) {
                    bestMatch = datasetSymptom
                    bestScore = score
                }
            }
            
            // Add best match if found
            if (bestMatch != null && !matchedSymptoms.contains(bestMatch)) {
                matchedSymptoms.add(bestMatch)
            }
        }
        
        return matchedSymptoms
    }
    
    /**
     * Predict disease based on matched symptoms using scoring mechanism
     * @param matchedSymptoms List of matched symptoms
     * @return Predicted disease or null if none found
     */
    fun predictDiseaseFromSymptoms(matchedSymptoms: List<String>?): String? {
        if (matchedSymptoms.isNullOrEmpty() || diseaseSymptoms.isEmpty()) {
            return null
        }
        
        // Score each disease based on symptom matches
        val diseaseScores = mutableMapOf<String, Double>()
        
        for ((disease, diseaseSymptomSet) in diseaseSymptoms) {
            if (diseaseSymptomSet.isNullOrEmpty()) {
                continue
            }
            
            // Count matching symptoms
            val matchingCount = matchedSymptoms.count { it in diseaseSymptomSet }
            
            // Calculate match percentage
            val matchPercentage = matchingCount.toDouble() / diseaseSymptomSet.size
            
            // Also consider how many of the user's symptoms match this disease
            val userMatchPercentage = matchingCount.toDouble() / matchedSymptoms.size
            
            // Combined score (weighted average)
            val combinedScore = (matchPercentage * 0.5) + (userMatchPercentage * 0.5)
            
            diseaseScores[disease] = combinedScore
        }
        
        // Return disease with highest score
        if (diseaseScores.isNotEmpty()) {
            val predictedDisease = diseaseScores.maxByOrNull { it.value }?.key
            
            // Only return if score is above minimum threshold
            if (predictedDisease != null && diseaseScores[predictedDisease]!! > 0.1) {
                return predictedDisease
            }
        }
        
        return null
    }
    
    /**
     * Get diseases associated with a symptom
     * @param symptom The symptom to look up
     * @return Set of diseases associated with the symptom
     */
    fun getDiseasesForSymptom(symptom: String?): Set<String> {
        if (symptom == null) {
            return emptySet()
        }
        
        val normalizedSymptom = symptom.trim().lowercase()
        return symptomToDiseases[normalizedSymptom] ?: emptySet()
    }
    
    /**
     * Get symptoms associated with a disease
     * @param disease The disease to look up
     * @return Set of symptoms associated with the disease
     */
    fun getSymptomsForDisease(disease: String?): Set<String> {
        if (disease == null) {
            return emptySet()
        }
        
        return diseaseSymptoms[disease] ?: emptySet()
    }
}