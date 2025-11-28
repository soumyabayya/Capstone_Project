import java.io.*;
import java.util.*;

/**
 * Dataset loader utility class for loading symptoms data from CSV files
 */
public class DatasetLoader {
    
    /**
     * Load symptoms data from CSV file
     * @param filePath Path to the CSV file
     * @return List of SymptomData objects
     * @throws IOException If there's an error reading the file
     */
    public static List<SymptomData> loadSymptomsFromCSV(String filePath) throws IOException {
        List<SymptomData> symptomsData = new ArrayList<>();
        
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            boolean isFirstLine = true;
            
            while ((line = reader.readLine()) != null) {
                // Skip header line
                if (isFirstLine) {
                    isFirstLine = false;
                    continue;
                }
                
                // Parse CSV line
                String[] parts = parseCSVLine(line);
                if (parts.length < 2) {
                    continue;
                }
                
                String disease = parts[1].trim();
                List<String> symptoms = new ArrayList<>();
                
                // Extract symptoms from columns 2 onwards
                for (int i = 2; i < parts.length; i++) {
                    String symptom = parts[i].trim();
                    if (!symptom.isEmpty() && !symptom.equals("null")) {
                        symptoms.add(symptom);
                    }
                }
                
                if (!disease.isEmpty() && !symptoms.isEmpty()) {
                    symptomsData.add(new SymptomData(disease, symptoms));
                }
            }
        }
        
        return symptomsData;
    }
    
    /**
     * Parse a CSV line, handling quoted fields
     * @param line The CSV line to parse
     * @return Array of field values
     */
    private static String[] parseCSVLine(String line) {
        List<String> fields = new ArrayList<>();
        boolean inQuotes = false;
        StringBuilder currentField = new StringBuilder();
        
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            
            if (c == '"') {
                inQuotes = !inQuotes;
            } else if (c == ',' && !inQuotes) {
                fields.add(currentField.toString().trim());
                currentField = new StringBuilder();
            } else {
                currentField.append(c);
            }
        }
        
        // Add the last field
        fields.add(currentField.toString().trim());
        
        return fields.toArray(new String[0]);
    }
    
    /**
     * Load description data from CSV file
     * @param filePath Path to the CSV file
     * @return Map of disease to description
     * @throws IOException If there's an error reading the file
     */
    public static Map<String, String> loadDescriptionsFromCSV(String filePath) throws IOException {
        Map<String, String> descriptions = new HashMap<>();
        
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            boolean isFirstLine = true;
            
            while ((line = reader.readLine()) != null) {
                // Skip header line
                if (isFirstLine) {
                    isFirstLine = false;
                    continue;
                }
                
                // Parse CSV line
                String[] parts = parseCSVLine(line);
                if (parts.length >= 2) {
                    String disease = parts[0].trim();
                    String description = parts[1].trim();
                    
                    if (!disease.isEmpty() && !description.isEmpty()) {
                        descriptions.put(disease, description);
                    }
                }
            }
        }
        
        return descriptions;
    }
    
    /**
     * Load medications data from CSV file
     * @param filePath Path to the CSV file
     * @return Map of disease to medications list
     * @throws IOException If there's an error reading the file
     */
    public static Map<String, List<String>> loadMedicationsFromCSV(String filePath) throws IOException {
        Map<String, List<String>> medications = new HashMap<>();
        
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            boolean isFirstLine = true;
            
            while ((line = reader.readLine()) != null) {
                // Skip header line
                if (isFirstLine) {
                    isFirstLine = false;
                    continue;
                }
                
                // Parse CSV line
                String[] parts = parseCSVLine(line);
                if (parts.length >= 2) {
                    String disease = parts[0].trim();
                    String medicationsStr = parts[1].trim();
                    
                    if (!disease.isEmpty() && !medicationsStr.isEmpty()) {
                        // Parse the string representation of a list
                        List<String> medList = parseMedicationsList(medicationsStr);
                        medications.put(disease, medList);
                    }
                }
            }
        }
        
        return medications;
    }
    
    /**
     * Parse medications list from string representation
     * @param medicationsStr String representation of medications list
     * @return List of medications
     */
    private static List<String> parseMedicationsList(String medicationsStr) {
        List<String> medications = new ArrayList<>();
        
        // Remove brackets and quotes
        medicationsStr = medicationsStr.replaceAll("[\\[\\]\"']", "").trim();
        
        // Split by comma
        String[] meds = medicationsStr.split(",");
        for (String med : meds) {
            String trimmedMed = med.trim();
            if (!trimmedMed.isEmpty()) {
                medications.add(trimmedMed);
            }
        }
        
        return medications;
    }
    
    /**
     * Load precautions data from CSV file
     * @param filePath Path to the CSV file
     * @return Map of disease to precautions list
     * @throws IOException If there's an error reading the file
     */
    public static Map<String, List<String>> loadPrecautionsFromCSV(String filePath) throws IOException {
        Map<String, List<String>> precautions = new HashMap<>();
        
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            boolean isFirstLine = true;
            
            while ((line = reader.readLine()) != null) {
                // Skip header line
                if (isFirstLine) {
                    isFirstLine = false;
                    continue;
                }
                
                // Parse CSV line
                String[] parts = parseCSVLine(line);
                if (parts.length >= 2) {
                    String disease = parts[1].trim(); // Disease is in column 1 (0-indexed)
                    List<String> precautionList = new ArrayList<>();
                    
                    // Extract precautions from columns 2 onwards
                    for (int i = 2; i < parts.length; i++) {
                        String precaution = parts[i].trim();
                        if (!precaution.isEmpty() && !precaution.equals("null")) {
                            precautionList.add(precaution);
                        }
                    }
                    
                    if (!disease.isEmpty() && !precautionList.isEmpty()) {
                        precautions.put(disease, precautionList);
                    }
                }
            }
        }
        
        return precautions;
    }
    
    /**
     * Load diets data from CSV file
     * @param filePath Path to the CSV file
     * @return Map of disease to diets list
     * @throws IOException If there's an error reading the file
     */
    public static Map<String, List<String>> loadDietsFromCSV(String filePath) throws IOException {
        Map<String, List<String>> diets = new HashMap<>();
        
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            boolean isFirstLine = true;
            
            while ((line = reader.readLine()) != null) {
                // Skip header line
                if (isFirstLine) {
                    isFirstLine = false;
                    continue;
                }
                
                // Parse CSV line
                String[] parts = parseCSVLine(line);
                if (parts.length >= 2) {
                    String disease = parts[0].trim();
                    String dietsStr = parts[1].trim();
                    
                    if (!disease.isEmpty() && !dietsStr.isEmpty()) {
                        // Parse the string representation of a list
                        List<String> dietList = parseMedicationsList(dietsStr);
                        diets.put(disease, dietList);
                    }
                }
            }
        }
        
        return diets;
    }
    
    /**
     * Load workouts data from CSV file
     * @param filePath Path to the CSV file
     * @return Map of disease to workouts list
     * @throws IOException If there's an error reading the file
     */
    public static Map<String, List<String>> loadWorkoutsFromCSV(String filePath) throws IOException {
        Map<String, List<String>> workouts = new HashMap<>();
        
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            boolean isFirstLine = true;
            
            while ((line = reader.readLine()) != null) {
                // Skip header line
                if (isFirstLine) {
                    isFirstLine = false;
                    continue;
                }
                
                // Parse CSV line
                String[] parts = parseCSVLine(line);
                if (parts.length >= 3) {
                    String disease = parts[2].trim(); // Disease is in column 2 (0-indexed)
                    String workout = parts[3].trim(); // Workout is in column 3 (0-indexed)
                    
                    if (!disease.isEmpty() && !workout.isEmpty() && !workout.equals("null")) {
                        workouts.computeIfAbsent(disease, k -> new ArrayList<>()).add(workout);
                    }
                }
            }
        }
        
        return workouts;
    }
}