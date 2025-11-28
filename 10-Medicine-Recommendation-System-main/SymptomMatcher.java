import java.util.*;
import java.util.stream.Collectors;

/**
 * Symptom matching utility class for finding matching symptoms using fuzzy matching
 */
public class SymptomMatcher {
    
    // Threshold for fuzzy matching (0.0-1.0)
    private static final double DEFAULT_THRESHOLD = 0.7;
    
    // Dataset symptoms for fast lookup
    private Set<String> datasetSymptoms;
    
    // Map symptoms to diseases
    private Map<String, Set<String>> symptomToDiseases;
    
    // Map diseases to their symptoms
    private Map<String, Set<String>> diseaseSymptoms;
    
    /**
     * Constructor
     */
    public SymptomMatcher() {
        this.datasetSymptoms = new HashSet<>();
        this.symptomToDiseases = new HashMap<>();
        this.diseaseSymptoms = new HashMap<>();
    }
    
    /**
     * Initialize dataset symptoms and mappings
     * @param symptomsData List of symptom data from dataset
     */
    public void initializeDatasetMappings(List<SymptomData> symptomsData) {
        // Clear existing data
        datasetSymptoms.clear();
        symptomToDiseases.clear();
        diseaseSymptoms.clear();
        
        // Process the symptoms dataset
        for (SymptomData data : symptomsData) {
            String disease = data.getDisease();
            
            // Collect all symptoms for this disease
            Set<String> diseaseSymptomsSet = new HashSet<>();
            
            // Add all symptoms for this disease
            for (String symptom : data.getSymptoms()) {
                if (symptom != null && !symptom.trim().isEmpty()) {
                    String normalizedSymptom = symptom.trim().toLowerCase();
                    
                    // Add to dataset symptoms set
                    datasetSymptoms.add(normalizedSymptom);
                    
                    // Map symptom to disease
                    symptomToDiseases.computeIfAbsent(normalizedSymptom, k -> new HashSet<>()).add(disease);
                    
                    // Add to disease symptoms list
                    diseaseSymptomsSet.add(normalizedSymptom);
                }
            }
            
            // Map disease to its symptoms
            diseaseSymptoms.put(disease, diseaseSymptomsSet);
        }
    }
    
    /**
     * Calculate similarity between two strings using Levenshtein distance
     * @param str1 First string
     * @param str2 Second string
     * @return Similarity ratio (0.0-1.0)
     */
    public static double calculateSimilarity(String str1, String str2) {
        if (str1 == null || str2 == null) {
            return 0.0;
        }
        
        // Convert to lowercase for comparison
        str1 = str1.toLowerCase();
        str2 = str2.toLowerCase();
        
        // If strings are identical, return 1.0
        if (str1.equals(str2)) {
            return 1.0;
        }
        
        // Calculate Levenshtein distance
        int len1 = str1.length();
        int len2 = str2.length();
        
        // Create matrix
        int[][] matrix = new int[len1 + 1][len2 + 1];
        
        // Initialize first row and column
        for (int i = 0; i <= len1; i++) {
            matrix[i][0] = i;
        }
        for (int j = 0; j <= len2; j++) {
            matrix[0][j] = j;
        }
        
        // Fill matrix
        for (int i = 1; i <= len1; i++) {
            for (int j = 1; j <= len2; j++) {
                int cost = (str1.charAt(i - 1) == str2.charAt(j - 1)) ? 0 : 1;
                matrix[i][j] = Math.min(
                    Math.min(matrix[i - 1][j] + 1,      // deletion
                             matrix[i][j - 1] + 1),      // insertion
                    matrix[i - 1][j - 1] + cost);        // substitution
            }
        }
        
        // Calculate similarity ratio
        int distance = matrix[len1][len2];
        int maxLen = Math.max(len1, len2);
        
        if (maxLen == 0) {
            return 1.0;
        }
        
        return 1.0 - ((double) distance / maxLen);
    }
    
    /**
     * Find matching symptoms using fuzzy matching
     * @param userInput User input text
     * @param threshold Similarity threshold (0.0-1.0)
     * @return List of matching symptoms
     */
    public List<String> findMatchingSymptoms(String userInput, double threshold) {
        List<String> matchedSymptoms = new ArrayList<>();
        
        if (userInput == null || userInput.isEmpty() || datasetSymptoms.isEmpty()) {
            return matchedSymptoms;
        }
        
        // Normalize user input
        String normalizedInput = SpeechProcessor.normalizeInput(userInput);
        
        // Split input into potential symptoms
        String[] inputSymptoms = normalizedInput.split("\\s+");
        List<String> inputSymptomsList = Arrays.stream(inputSymptoms)
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .collect(Collectors.toList());
        
        // Try to match multi-word phrases first
        if (datasetSymptoms.contains(normalizedInput)) {
            matchedSymptoms.add(normalizedInput);
        }
        
        // Try fuzzy matching for each input symptom
        for (String inputSymptom : inputSymptomsList) {
            String bestMatch = null;
            double bestScore = 0;
            
            // Check against all dataset symptoms
            for (String datasetSymptom : datasetSymptoms) {
                // Calculate similarity
                double score = calculateSimilarity(inputSymptom, datasetSymptom);
                
                // If score is above threshold and better than current best
                if (score >= threshold && score > bestScore) {
                    bestMatch = datasetSymptom;
                    bestScore = score;
                }
            }
            
            // Add best match if found
            if (bestMatch != null && !matchedSymptoms.contains(bestMatch)) {
                matchedSymptoms.add(bestMatch);
            }
        }
        
        return matchedSymptoms;
    }
    
    /**
     * Find matching symptoms using default threshold
     * @param userInput User input text
     * @return List of matching symptoms
     */
    public List<String> findMatchingSymptoms(String userInput) {
        return findMatchingSymptoms(userInput, DEFAULT_THRESHOLD);
    }
    
    /**
     * Predict disease based on matched symptoms using scoring mechanism
     * @param matchedSymptoms List of matched symptoms
     * @return Predicted disease or null if none found
     */
    public String predictDiseaseFromSymptoms(List<String> matchedSymptoms) {
        if (matchedSymptoms == null || matchedSymptoms.isEmpty() || diseaseSymptoms.isEmpty()) {
            return null;
        }
        
        // Score each disease based on symptom matches
        Map<String, Double> diseaseScores = new HashMap<>();
        
        for (Map.Entry<String, Set<String>> entry : diseaseSymptoms.entrySet()) {
            String disease = entry.getKey();
            Set<String> diseaseSymptomSet = entry.getValue();
            
            if (diseaseSymptomSet == null || diseaseSymptomSet.isEmpty()) {
                continue;
            }
            
            // Count matching symptoms
            long matchingCount = matchedSymptoms.stream()
                    .filter(diseaseSymptomSet::contains)
                    .count();
            
            // Calculate match percentage
            double matchPercentage = (double) matchingCount / diseaseSymptomSet.size();
            
            // Also consider how many of the user's symptoms match this disease
            double userMatchPercentage = (double) matchingCount / matchedSymptoms.size();
            
            // Combined score (weighted average)
            double combinedScore = (matchPercentage * 0.5) + (userMatchPercentage * 0.5);
            
            diseaseScores.put(disease, combinedScore);
        }
        
        // Return disease with highest score
        if (!diseaseScores.isEmpty()) {
            String predictedDisease = Collections.max(diseaseScores.entrySet(), 
                    Map.Entry.comparingByValue()).getKey();
            
            // Only return if score is above minimum threshold
            if (diseaseScores.get(predictedDisease) > 0.1) {
                return predictedDisease;
            }
        }
        
        return null;
    }
    
    /**
     * Get diseases associated with a symptom
     * @param symptom The symptom to look up
     * @return Set of diseases associated with the symptom
     */
    public Set<String> getDiseasesForSymptom(String symptom) {
        if (symptom == null) {
            return Collections.emptySet();
        }
        
        String normalizedSymptom = symptom.trim().toLowerCase();
        return symptomToDiseases.getOrDefault(normalizedSymptom, Collections.emptySet());
    }
    
    /**
     * Get symptoms associated with a disease
     * @param disease The disease to look up
     * @return Set of symptoms associated with the disease
     */
    public Set<String> getSymptomsForDisease(String disease) {
        if (disease == null) {
            return Collections.emptySet();
        }
        
        return diseaseSymptoms.getOrDefault(disease, Collections.emptySet());
    }
}