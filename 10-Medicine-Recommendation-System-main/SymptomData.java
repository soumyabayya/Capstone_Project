import java.util.List;

/**
 * Data class representing symptom data for a disease
 */
public class SymptomData {
    private String disease;
    private List<String> symptoms;
    
    /**
     * Constructor
     * @param disease The disease name
     * @param symptoms List of symptoms for the disease
     */
    public SymptomData(String disease, List<String> symptoms) {
        this.disease = disease;
        this.symptoms = symptoms;
    }
    
    /**
     * Get the disease name
     * @return Disease name
     */
    public String getDisease() {
        return disease;
    }
    
    /**
     * Set the disease name
     * @param disease Disease name
     */
    public void setDisease(String disease) {
        this.disease = disease;
    }
    
    /**
     * Get the list of symptoms
     * @return List of symptoms
     */
    public List<String> getSymptoms() {
        return symptoms;
    }
    
    /**
     * Set the list of symptoms
     * @param symptoms List of symptoms
     */
    public void setSymptoms(List<String> symptoms) {
        this.symptoms = symptoms;
    }
}