import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import java.util.ArrayList;
import java.util.Locale;

public class SpeechRecognitionActivity extends AppCompatActivity implements RecognitionListener {
    private static final int PERMISSION_REQUEST_RECORD_AUDIO = 1;
    
    private SpeechRecognizer speechRecognizer;
    private Intent speechRecognizerIntent;
    private boolean isListening = false;
    
    private Button startSpeechButton;
    private Button stopSpeechButton;
    private Button resetButton;
    private TextView transcriptionText;
    private StringBuilder allSymptoms;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        initializeViews();
        initializeSpeechRecognizer();
        setupClickListeners();
        
        allSymptoms = new StringBuilder();
        
        // Check for record audio permission
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) 
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, 
                    new String[]{Manifest.permission.RECORD_AUDIO}, 
                    PERMISSION_REQUEST_RECORD_AUDIO);
        }
    }
    
    private void initializeViews() {
        startSpeechButton = findViewById(R.id.startSpeechButton);
        stopSpeechButton = findViewById(R.id.stopSpeechButton);
        resetButton = findViewById(R.id.resetButton);
        transcriptionText = findViewById(R.id.transcriptionText);
    }
    
    private void initializeSpeechRecognizer() {
        if (SpeechRecognizer.isRecognitionAvailable(this)) {
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this);
            speechRecognizer.setRecognitionListener(this);
            
            speechRecognizerIntent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
            speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, 
                    RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
            speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault());
            speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true);
            speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 100);
            speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, 
                    this.getPackageName());
        } else {
            Toast.makeText(this, "Speech recognition not available on this device", 
                    Toast.LENGTH_LONG).show();
        }
    }
    
    private void setupClickListeners() {
        startSpeechButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startContinuousListening();
            }
        });
        
        stopSpeechButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopListening();
            }
        });
        
        resetButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                resetSymptoms();
            }
        });
    }
    
    /**
     * Start continuous speech listening
     */
    public void startContinuousListening() {
        if (speechRecognizer != null && !isListening) {
            isListening = true;
            startSpeechButton.setEnabled(false);
            stopSpeechButton.setEnabled(true);
            speechRecognizer.startListening(speechRecognizerIntent);
            Toast.makeText(this, "Listening... Speak your symptoms", Toast.LENGTH_SHORT).show();
        }
    }
    
    /**
     * Stop speech listening
     */
    public void stopListening() {
        if (speechRecognizer != null && isListening) {
            isListening = false;
            startSpeechButton.setEnabled(true);
            stopSpeechButton.setEnabled(false);
            speechRecognizer.stopListening();
            Toast.makeText(this, "Stopped listening", Toast.LENGTH_SHORT).show();
        }
    }
    
    /**
     * Reset all collected symptoms
     */
    public void resetSymptoms() {
        allSymptoms.setLength(0);
        transcriptionText.setText("Speech will appear here...");
        Toast.makeText(this, "Symptoms reset", Toast.LENGTH_SHORT).show();
    }
    
    /**
     * Append new symptoms to existing list without overwriting
     * @param newSymptoms The new symptoms to append
     */
    private void appendSymptoms(String newSymptoms) {
        if (newSymptoms != null && !newSymptoms.trim().isEmpty()) {
            // Clean the input - remove punctuation, convert to lowercase, trim spaces
            String cleanedSymptoms = SpeechProcessor.cleanSpeechInput(newSymptoms);
            
            if (allSymptoms.length() > 0 && !cleanedSymptoms.isEmpty()) {
                allSymptoms.append(" ");
            }
            allSymptoms.append(cleanedSymptoms);
            
            // Update the UI with all symptoms
            transcriptionText.setText(allSymptoms.toString());
        }
    }
    
    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        
        if (requestCode == PERMISSION_REQUEST_RECORD_AUDIO) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(this, "Microphone permission granted", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(this, "Microphone permission denied", Toast.LENGTH_LONG).show();
            }
        }
    }
    
    // RecognitionListener methods
    @Override
    public void onReadyForSpeech(Bundle params) {
        // Ready to receive speech
    }
    
    @Override
    public void onBeginningOfSpeech() {
        // User has started speaking
    }
    
    @Override
    public void onRmsChanged(float rmsdB) {
        // Sound level changed
    }
    
    @Override
    public void onBufferReceived(byte[] buffer) {
        // Buffer received
    }
    
    @Override
    public void onEndOfSpeech() {
        // User has stopped speaking
        // Automatically restart listening for continuous recognition
        if (isListening) {
            speechRecognizer.startListening(speechRecognizerIntent);
        }
    }
    
    @Override
    public void onError(int error) {
        String errorMessage = getErrorMessage(error);
        Toast.makeText(this, "Error: " + errorMessage, Toast.LENGTH_LONG).show();
        
        // Automatically restart on error for continuous recognition
        if (isListening) {
            speechRecognizer.startListening(speechRecognizerIntent);
        } else {
            startSpeechButton.setEnabled(true);
            stopSpeechButton.setEnabled(false);
        }
    }
    
    @Override
    public void onResults(Bundle results) {
        // Final results received
        ArrayList<String> matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
        if (matches != null && !matches.isEmpty()) {
            // Use the first (most likely) result
            String recognizedText = matches.get(0);
            appendSymptoms(recognizedText);
        }
        
        // Automatically restart for continuous recognition
        if (isListening) {
            speechRecognizer.startListening(speechRecognizerIntent);
        }
    }
    
    @Override
    public void onPartialResults(Bundle partialResults) {
        // Partial results received - show them as they come
        ArrayList<String> matches = partialResults.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
        if (matches != null && !matches.isEmpty()) {
            // Use the first (most likely) partial result
            String partialText = matches.get(0);
            // For partial results, we just update the display but don't append to allSymptoms yet
            // The final result will be appended in onResults()
            transcriptionText.setText(allSymptoms.toString() + (allSymptoms.length() > 0 ? " " : "") + partialText);
        }
    }
    
    @Override
    public void onEvent(int eventType, Bundle params) {
        // Reserved for future use
    }
    
    private String getErrorMessage(int errorCode) {
        switch (errorCode) {
            case SpeechRecognizer.ERROR_AUDIO:
                return "Audio recording error";
            case SpeechRecognizer.ERROR_CLIENT:
                return "Client side error";
            case SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS:
                return "Insufficient permissions";
            case SpeechRecognizer.ERROR_NETWORK:
                return "Network error";
            case SpeechRecognizer.ERROR_NETWORK_TIMEOUT:
                return "Network timeout";
            case SpeechRecognizer.ERROR_NO_MATCH:
                return "No match found";
            case SpeechRecognizer.ERROR_RECOGNIZER_BUSY:
                return "Recognition service busy";
            case SpeechRecognizer.ERROR_SERVER:
                return "Server error";
            case SpeechRecognizer.ERROR_SPEECH_TIMEOUT:
                return "No speech input";
            default:
                return "Unknown error";
        }
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (speechRecognizer != null) {
            speechRecognizer.destroy();
        }
    }
}