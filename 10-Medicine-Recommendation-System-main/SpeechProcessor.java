import java.util.regex.Pattern;

/**
 * Speech processing utility class for cleaning and normalizing speech input
 */
public class SpeechProcessor {
    
    /**
     * Clean speech input to match the JavaScript processing
     * @param text The raw speech input text
     * @return Cleaned and normalized text
     */
    public static String cleanSpeechInput(String text) {
        if (text == null || text.isEmpty()) {
            return "";
        }
        
        // Convert to lowercase
        text = text.toLowerCase();
        
        // Remove punctuation and special characters
        text = text.replaceAll("[^a-zA-Z0-9\\s]", "");
        
        // Replace multiple spaces with single space and trim
        text = text.replaceAll("\\s+", " ").trim();
        
        return text;
    }
    
    /**
     * Normalize input text by removing punctuation and normalizing spaces
     * @param text The input text to normalize
     * @return Normalized text
     */
    public static String normalizeInput(String text) {
        if (text == null || text.isEmpty()) {
            return "";
        }
        
        // Convert to lowercase
        text = text.toLowerCase();
        
        // Remove punctuation (commas, periods, etc.)
        text = text.replaceAll("[^a-zA-Z0-9\\s]", "");
        
        // Replace multiple spaces with single space and trim
        text = text.replaceAll("\\s+", " ").trim();
        
        return text;
    }
}