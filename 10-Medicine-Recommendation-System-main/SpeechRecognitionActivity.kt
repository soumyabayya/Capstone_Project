import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.util.*

class SpeechRecognitionActivity : AppCompatActivity(), RecognitionListener {
    companion object {
        private const val PERMISSION_REQUEST_RECORD_AUDIO = 1
    }
    
    private var speechRecognizer: SpeechRecognizer? = null
    private lateinit var speechRecognizerIntent: Intent
    private var isListening = false
    
    private lateinit var startSpeechButton: Button
    private lateinit var stopSpeechButton: Button
    private lateinit var resetButton: Button
    private lateinit var transcriptionText: TextView
    private val allSymptoms = StringBuilder()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initializeViews()
        initializeSpeechRecognizer()
        setupClickListeners()
        
        // Check for record audio permission
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) 
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, 
                    arrayOf(Manifest.permission.RECORD_AUDIO), 
                    PERMISSION_REQUEST_RECORD_AUDIO)
        }
    }
    
    private fun initializeViews() {
        startSpeechButton = findViewById(R.id.startSpeechButton)
        stopSpeechButton = findViewById(R.id.stopSpeechButton)
        resetButton = findViewById(R.id.resetButton)
        transcriptionText = findViewById(R.id.transcriptionText)
    }
    
    private fun initializeSpeechRecognizer() {
        if (SpeechRecognizer.isRecognitionAvailable(this)) {
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this)
            speechRecognizer?.setRecognitionListener(this)
            
            speechRecognizerIntent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, 
                        RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
                putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
                putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 100)
                putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, 
                        this@SpeechRecognitionActivity.packageName)
            }
        } else {
            Toast.makeText(this, "Speech recognition not available on this device", 
                    Toast.LENGTH_LONG).show()
        }
    }
    
    private fun setupClickListeners() {
        startSpeechButton.setOnClickListener {
            startContinuousListening()
        }
        
        stopSpeechButton.setOnClickListener {
            stopListening()
        }
        
        resetButton.setOnClickListener {
            resetSymptoms()
        }
    }
    
    /**
     * Start continuous speech listening
     */
    fun startContinuousListening() {
        if (speechRecognizer != null && !isListening) {
            isListening = true
            startSpeechButton.isEnabled = false
            stopSpeechButton.isEnabled = true
            speechRecognizer?.startListening(speechRecognizerIntent)
            Toast.makeText(this, "Listening... Speak your symptoms", Toast.LENGTH_SHORT).show()
        }
    }
    
    /**
     * Stop speech listening
     */
    fun stopListening() {
        if (speechRecognizer != null && isListening) {
            isListening = false
            startSpeechButton.isEnabled = true
            stopSpeechButton.isEnabled = false
            speechRecognizer?.stopListening()
            Toast.makeText(this, "Stopped listening", Toast.LENGTH_SHORT).show()
        }
    }
    
    /**
     * Reset all collected symptoms
     */
    fun resetSymptoms() {
        allSymptoms.clear()
        transcriptionText.text = "Speech will appear here..."
        Toast.makeText(this, "Symptoms reset", Toast.LENGTH_SHORT).show()
    }
    
    /**
     * Append new symptoms to existing list without overwriting
     * @param newSymptoms The new symptoms to append
     */
    private fun appendSymptoms(newSymptoms: String?) {
        if (!newSymptoms.isNullOrBlank()) {
            // Clean the input - remove punctuation, convert to lowercase, trim spaces
            val cleanedSymptoms = SpeechProcessor.cleanSpeechInput(newSymptoms)
            
            if (allSymptoms.isNotEmpty() && cleanedSymptoms.isNotEmpty()) {
                allSymptoms.append(" ")
            }
            allSymptoms.append(cleanedSymptoms)
            
            // Update the UI with all symptoms
            transcriptionText.text = allSymptoms.toString()
        }
    }
    
    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        
        if (requestCode == PERMISSION_REQUEST_RECORD_AUDIO) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(this, "Microphone permission granted", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, "Microphone permission denied", Toast.LENGTH_LONG).show()
            }
        }
    }
    
    // RecognitionListener methods
    override fun onReadyForSpeech(params: Bundle?) {
        // Ready to receive speech
    }
    
    override fun onBeginningOfSpeech() {
        // User has started speaking
    }
    
    override fun onRmsChanged(rmsdB: Float) {
        // Sound level changed
    }
    
    override fun onBufferReceived(buffer: ByteArray?) {
        // Buffer received
    }
    
    override fun onEndOfSpeech() {
        // User has stopped speaking
        // Automatically restart listening for continuous recognition
        if (isListening) {
            speechRecognizer?.startListening(speechRecognizerIntent)
        }
    }
    
    override fun onError(error: Int) {
        val errorMessage = getErrorMessage(error)
        Toast.makeText(this, "Error: $errorMessage", Toast.LENGTH_LONG).show()
        
        // Automatically restart on error for continuous recognition
        if (isListening) {
            speechRecognizer?.startListening(speechRecognizerIntent)
        } else {
            startSpeechButton.isEnabled = true
            stopSpeechButton.isEnabled = false
        }
    }
    
    override fun onResults(results: Bundle?) {
        // Final results received
        val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
        if (!matches.isNullOrEmpty()) {
            // Use the first (most likely) result
            val recognizedText = matches[0]
            appendSymptoms(recognizedText)
        }
        
        // Automatically restart for continuous recognition
        if (isListening) {
            speechRecognizer?.startListening(speechRecognizerIntent)
        }
    }
    
    override fun onPartialResults(partialResults: Bundle?) {
        // Partial results received - show them as they come
        val matches = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
        if (!matches.isNullOrEmpty()) {
            // Use the first (most likely) partial result
            val partialText = matches[0]
            // For partial results, we just update the display but don't append to allSymptoms yet
            // The final result will be appended in onResults()
            transcriptionText.text = allSymptoms.toString() + 
                    if (allSymptoms.isNotEmpty()) " " else "" + partialText
        }
    }
    
    override fun onEvent(eventType: Int, params: Bundle?) {
        // Reserved for future use
    }
    
    private fun getErrorMessage(errorCode: Int): String {
        return when (errorCode) {
            SpeechRecognizer.ERROR_AUDIO -> "Audio recording error"
            SpeechRecognizer.ERROR_CLIENT -> "Client side error"
            SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Insufficient permissions"
            SpeechRecognizer.ERROR_NETWORK -> "Network error"
            SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "Network timeout"
            SpeechRecognizer.ERROR_NO_MATCH -> "No match found"
            SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "Recognition service busy"
            SpeechRecognizer.ERROR_SERVER -> "Server error"
            SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "No speech input"
            else -> "Unknown error"
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        speechRecognizer?.destroy()
    }
}