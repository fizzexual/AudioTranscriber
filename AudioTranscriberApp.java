import javax.swing.*;
import javax.sound.sampled.*;
import java.awt.*;
import java.io.*;
import java.net.*;
import java.util.concurrent.*;
import javax.swing.border.*;

public class AudioTranscriberApp extends JFrame {
    private JTextArea textArea;
    private JButton startBtn, stopBtn, clearBtn;
    private JLabel statusLabel;
    private JComboBox<String> languageCombo;
    private volatile boolean isListening = false;
    private ExecutorService executor;
    
    public AudioTranscriberApp() {
        setTitle("Auto Audio-to-Text Transcriber");
        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        
        setupUI();
        executor = Executors.newSingleThreadExecutor();
    }
    
    private void setupUI() {
        JPanel mainPanel = new JPanel(new BorderLayout(10, 10));
        mainPanel.setBorder(new EmptyBorder(15, 15, 15, 15));
        
        // Title
        JLabel titleLabel = new JLabel("🎤 Automatic Audio Transcriber", JLabel.CENTER);
        titleLabel.setFont(new Font("Arial", Font.BOLD, 18));
        mainPanel.add(titleLabel, BorderLayout.NORTH);
        
        // Center panel
        JPanel centerPanel = new JPanel(new BorderLayout(10, 10));
        
        // Control panel
        JPanel controlPanel = new JPanel(new FlowLayout());
        
        startBtn = new JButton("Start Listening");
        startBtn.setBackground(new Color(76, 175, 80));
        startBtn.setForeground(Color.WHITE);
        startBtn.setFont(new Font("Arial", Font.BOLD, 12));
        startBtn.addActionListener(e -> startListening());
        
        stopBtn = new JButton("Stop Listening");
        stopBtn.setBackground(new Color(244, 67, 54));
        stopBtn.setForeground(Color.WHITE);
        stopBtn.setFont(new Font("Arial", Font.BOLD, 12));
        stopBtn.setEnabled(false);
        stopBtn.addActionListener(e -> stopListening());
        
        clearBtn = new JButton("Clear Text");
        clearBtn.setBackground(new Color(33, 150, 243));
        clearBtn.setForeground(Color.WHITE);
        clearBtn.setFont(new Font("Arial", Font.BOLD, 12));
        clearBtn.addActionListener(e -> textArea.setText(""));
        
        controlPanel.add(startBtn);
        controlPanel.add(stopBtn);
        controlPanel.add(clearBtn);
        
        // Status
        statusLabel = new JLabel("Status: Idle");
        statusLabel.setHorizontalAlignment(JLabel.CENTER);
        
        // Language selection
        JPanel langPanel = new JPanel(new FlowLayout());
        langPanel.add(new JLabel("Language:"));
        String[] languages = {"en-US", "es-ES", "fr-FR", "de-DE", "it-IT", 
                             "pt-BR", "ru-RU", "ja-JP", "zh-CN"};
        languageCombo = new JComboBox<>(languages);
        langPanel.add(languageCombo);
        
        JPanel topPanel = new JPanel(new BorderLayout());
        topPanel.add(controlPanel, BorderLayout.NORTH);
        topPanel.add(statusLabel, BorderLayout.CENTER);
        topPanel.add(langPanel, BorderLayout.SOUTH);
        
        centerPanel.add(topPanel, BorderLayout.NORTH);
        
        // Text area
        JPanel textPanel = new JPanel(new BorderLayout(5, 5));
        textPanel.add(new JLabel("Transcribed Text:"), BorderLayout.NORTH);
        
        textArea = new JTextArea();
        textArea.setFont(new Font("Consolas", Font.PLAIN, 12));
        textArea.setLineWrap(true);
        textArea.setWrapStyleWord(true);
        JScrollPane scrollPane = new JScrollPane(textArea);
        textPanel.add(scrollPane, BorderLayout.CENTER);
        
        centerPanel.add(textPanel, BorderLayout.CENTER);
        
        mainPanel.add(centerPanel, BorderLayout.CENTER);
        
        // Info
        JLabel infoLabel = new JLabel("Uses Google Speech Recognition API (requires internet)", JLabel.CENTER);
        infoLabel.setFont(new Font("Arial", Font.PLAIN, 10));
        infoLabel.setForeground(Color.GRAY);
        mainPanel.add(infoLabel, BorderLayout.SOUTH);
        
        add(mainPanel);
    }
    
    private void startListening() {
        isListening = true;
        startBtn.setEnabled(false);
        stopBtn.setEnabled(true);
        statusLabel.setText("Status: Listening...");
        statusLabel.setForeground(new Color(76, 175, 80));
        
        executor.submit(this::listenContinuously);
    }
    
    private void stopListening() {
        isListening = false;
        startBtn.setEnabled(true);
        stopBtn.setEnabled(false);
        statusLabel.setText("Status: Stopped");
        statusLabel.setForeground(Color.RED);
    }
    
    private void listenContinuously() {
        AudioFormat format = new AudioFormat(16000, 16, 1, true, false);
        DataLine.Info info = new DataLine.Info(TargetDataLine.class, format);
        
        if (!AudioSystem.isLineSupported(info)) {
            SwingUtilities.invokeLater(() -> {
                statusLabel.setText("Error: Microphone not supported");
                stopListening();
            });
            return;
        }
        
        try (TargetDataLine microphone = (TargetDataLine) AudioSystem.getLine(info)) {
            microphone.open(format);
            microphone.start();
            
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buffer = new byte[4096];
            
            while (isListening) {
                SwingUtilities.invokeLater(() -> 
                    statusLabel.setText("Status: Recording..."));
                
                // Record for 3 seconds
                long startTime = System.currentTimeMillis();
                out.reset();
                
                while (System.currentTimeMillis() - startTime < 3000 && isListening) {
                    int bytesRead = microphone.read(buffer, 0, buffer.length);
                    out.write(buffer, 0, bytesRead);
                }
                
                if (!isListening) break;
                
                SwingUtilities.invokeLater(() -> 
                    statusLabel.setText("Status: Processing..."));
                
                // Convert to FLAC and send to Google
                byte[] audioData = out.toByteArray();
                String text = recognizeSpeech(audioData, format);
                
                if (text != null && !text.isEmpty()) {
                    SwingUtilities.invokeLater(() -> {
                        textArea.append(text + " ");
                        textArea.setCaretPosition(textArea.getDocument().getLength());
                    });
                }
            }
            
        } catch (Exception e) {
            e.printStackTrace();
            SwingUtilities.invokeLater(() -> {
                statusLabel.setText("Error: " + e.getMessage());
                stopListening();
            });
        }
    }
    
    private String recognizeSpeech(byte[] audioData, AudioFormat format) {
        try {
            // Convert to WAV format
            ByteArrayInputStream bais = new ByteArrayInputStream(audioData);
            AudioInputStream audioInputStream = new AudioInputStream(bais, format, 
                audioData.length / format.getFrameSize());
            
            ByteArrayOutputStream wavOut = new ByteArrayOutputStream();
            AudioSystem.write(audioInputStream, AudioFileFormat.Type.WAVE, wavOut);
            byte[] wavData = wavOut.toByteArray();
            
            // Send to Google Speech API
            String language = (String) languageCombo.getSelectedItem();
            String apiUrl = "https://www.google.com/speech-api/v2/recognize?output=json&lang=" + language + "&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw";
            
            URL url = new URL(apiUrl);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setDoOutput(true);
            conn.setRequestProperty("Content-Type", "audio/l16; rate=16000");
            
            try (OutputStream os = conn.getOutputStream()) {
                os.write(wavData);
            }
            
            int responseCode = conn.getResponseCode();
            if (responseCode == 200) {
                try (BufferedReader br = new BufferedReader(
                        new InputStreamReader(conn.getInputStream()))) {
                    String line;
                    StringBuilder response = new StringBuilder();
                    while ((line = br.readLine()) != null) {
                        response.append(line);
                    }
                    
                    // Parse JSON response (simple parsing)
                    String result = response.toString();
                    if (result.contains("\"transcript\":")) {
                        int start = result.indexOf("\"transcript\":\"") + 14;
                        int end = result.indexOf("\"", start);
                        if (start > 13 && end > start) {
                            return result.substring(start, end);
                        }
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            AudioTranscriberApp app = new AudioTranscriberApp();
            app.setVisible(true);
        });
    }
}
