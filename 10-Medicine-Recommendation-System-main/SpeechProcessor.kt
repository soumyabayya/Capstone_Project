/**
 * Speech processing utility class for cleaning and normalizing speech input
 */
object SpeechProcessor {
    
    /**
     * Clean speech input to match the JavaScript processing
     * @param text The raw speech input text
     * @return Cleaned and normalized text
     */
    fun cleanSpeechInput(text: String?): String {
        if (text.isNullOrBlank()) {
            return ""
        }
        
        return text
            .lowercase()
            .replace(Regex("[^a-zA-Z0-9\\s]"), "")
            .replace(Regex("\\s+"), " ")
            .trim()
    }
    
    /**
     * Normalize input text by removing punctuation and normalizing spaces
     * @param text The input text to normalize
     * @return Normalized text
     */
    fun normalizeInput(text: String?): String {
        if (text.isNullOrBlank()) {
            return ""
        }
        
        return text
            .lowercase()
            .replace(Regex("[^a-zA-Z0-9\\s]"), "")
            .replace(Regex("\\s+"), " ")
            .trim()
    }
}