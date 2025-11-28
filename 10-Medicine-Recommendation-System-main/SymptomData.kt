/**
 * Data class representing symptom data for a disease
 * @property disease The disease name
 * @property symptoms List of symptoms for the disease
 */
data class SymptomData(
    val disease: String,
    val symptoms: List<String>
)