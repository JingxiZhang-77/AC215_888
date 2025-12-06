# Safety Event Classification System - Web Frontend

A professional, hospital-suitable web interface for classifying safety events using AI-powered analysis with secure authentication.

## Features

### � Authentication & Security
- Secure login system to protect LLM resources
- Session-based authentication with Flask-Login
- Password hashing for secure credential storage
- Protected API endpoints requiring authentication
- Default credentials: `admin` / `hospital2024`
- See [AUTHENTICATION.md](AUTHENTICATION.md) for detailed security guide

### 🖊️ Text Input
- Multiple text input boxes (up to 5 incidents)
- Add/remove incident descriptions dynamically
- Batch classification of multiple events simultaneously
- Clean, accessible interface with real-time validation
- Immediate classification results

### 🎙️ Audio-to-Text
- Built-in speech recognition using Web Speech API
- Real-time transcription display
- Start/stop recording controls with visual feedback
- Recording timer to track duration
- Works in Chrome, Edge, and Safari browsers

### 📄 CSV/Excel Upload
- Batch processing of multiple incidents
- Drag-and-drop file upload interface
- Supports both CSV and XLSX formats
- Automatic column detection for incident descriptions
- Process hundreds of incidents at once
- Downloadable CSV template for easy data entry

### 📊 Results Display
- Clear, color-coded classification badges
- Detailed breakdown of each classification step
- Rationale explanation for each decision
- Export results to CSV format
- Professional hospital-grade UI design

## Installation

### Prerequisites
- Python 3.11+
- Docker (optional, for containerized deployment)
- GCP Service Account credentials

### Local Setup

1. **Install dependencies:**
```bash
cd src/frontend
pip install -r requirements.txt
```

2. **Set up Google Cloud credentials:**
Ensure your service account JSON file is available at:
```
../../secrets/llm-service-account.json
```

3. **Run the application:**
```bash
chmod +x run.sh
./run.sh
```

Or manually:
```bash
python app.py
```

4. **Access the application:**
Open your browser and navigate to:
```
http://localhost:8080
```

5. **Login:**
Use the default credentials:
- **Username:** `admin`
- **Password:** `hospital2024`

> ⚠️ **Security Note:** Change the default credentials before deploying to production! See [AUTHENTICATION.md](AUTHENTICATION.md) for details.

### Docker Setup

1. **Build and run with Docker:**
```bash
cd src/frontend
./docker-shell.sh
```

2. **Access the application:**
```
http://localhost:8080
```

## Usage

### Text Input Method
1. Click on "Text Input" button
2. Enter or paste the safety event description
3. Click "Classify Incident"
4. View the classification results

### Audio Input Method
1. Click on "Audio Input" button
2. Click "Start Recording" and allow microphone access
3. Speak the safety event description clearly
4. Click "Stop Recording" when finished
5. Review the transcription
6. Click "Classify Transcript" to process

**Note:** Audio-to-text requires a modern browser (Chrome, Edge, Safari) and microphone permissions.

### CSV Upload Method
1. Click on "Upload CSV" button
2. Drag and drop a CSV/XLSX file or click to browse
3. Select a file containing incident descriptions
4. Click "Process File"
5. View all classification results

**CSV Format:** The system automatically detects columns containing incident descriptions. Supported column names include "description", "incident", "event", "Brief Factual Description", etc.

## Classification Codes

- **NSE** (No Safety Event): No deviation from Generally Accepted Performance Standards (GAPS)
- **NME** (Near Miss Event): Deviation occurred but did not reach the patient
- **PSE** (Precursor Safety Event): Deviation reached the patient with no or minimal harm
- **SSE** (Serious Safety Event): Deviation reached the patient and caused moderate/severe harm or death

## API Endpoints

### POST /api/classify
Classify a single incident.

**Request:**
```json
{
  "description": "Incident description text"
}
```

**Response:**
```json
{
  "incident": "Incident description text",
  "gaps_deviation_check": "Yes",
  "reached_patient_check": "Yes",
  "harm_level_check": "No",
  "final_classification_code": "PSE",
  "rationale": "Deviation reached the patient with no or minimal harm.",
  "status": "success"
}
```

### POST /api/classify-batch
Process multiple incidents from a CSV/Excel file.

**Request:** Multipart form data with file upload

**Response:**
```json
{
  "results": [...],
  "count": 10
}
```

### POST /api/export
Export classification results as CSV.

**Request:**
```json
{
  "results": [...]
}
```

**Response:** CSV file download

## Browser Compatibility

- ✅ Chrome 80+ (Full support including audio)
- ✅ Edge 80+ (Full support including audio)
- ✅ Safari 14+ (Full support including audio)
- ⚠️ Firefox 75+ (Text and upload only, no audio-to-text)

## Security Considerations

- Maximum file upload size: 16MB
- Only CSV and XLSX files are accepted for upload
- All user inputs are sanitized before processing
- Service account credentials should be properly secured
- Recommended to run behind HTTPS in production

## Design Features

- **Professional Hospital UI**: Clean, accessible design suitable for clinical environments
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Color-coded Results**: Easy-to-read classification badges with intuitive colors
- **Real-time Feedback**: Loading indicators and status updates
- **Accessibility**: WCAG compliant with proper contrast ratios and semantic HTML

## Troubleshooting

### Audio recording not working
- Ensure microphone permissions are granted in browser settings
- Use a supported browser (Chrome, Edge, Safari)
- Check if microphone is properly connected and not in use by another application

### File upload fails
- Ensure file is in CSV or XLSX format
- Check file size (must be under 16MB)
- Verify file contains a column with incident descriptions

### Classification takes too long
- Large batch files may take several minutes to process
- Each incident requires multiple AI model calls
- Consider breaking large files into smaller batches

## Production Deployment

For production deployment:

1. Set `debug=False` in `app.py`
2. Use a production WSGI server (gunicorn, uWSGI)
3. Set up proper environment variable management
4. Enable HTTPS with valid SSL certificates
5. Configure proper CORS settings if needed
6. Set up monitoring and logging
7. Implement rate limiting for API endpoints

## Development

The application structure:
```
frontend/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── docker-shell.sh       # Development script
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── styles.css        # Styling
    └── script.js         # Frontend JavaScript
```

## License

For healthcare professional use only. Ensure compliance with relevant healthcare data regulations (HIPAA, etc.) when deploying.

## Support

For issues or questions, please contact your system administrator or refer to the project documentation.
