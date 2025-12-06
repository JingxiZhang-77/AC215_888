# Safety Event Classification System - Frontend Overview

## 🏥 Hospital-Grade Web Application

A professional, accessible web interface for classifying safety events using AI-powered analysis.

---

## 📁 Project Structure

```
src/frontend/
├── app.py                      # Flask backend application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-shell.sh            # Docker development script
├── run.sh                     # Local development script
├── README.md                  # Complete documentation
├── QUICKSTART.md              # Quick start guide
├── sample_incidents.csv       # Example CSV file
│
├── templates/
│   └── index.html             # Main UI template
│
└── static/
    ├── styles.css             # Professional hospital styling
    └── script.js              # Frontend functionality
```

---

## ✨ Key Features

### 1. **Three Input Methods**
   - ✍️ Direct text entry
   - 🎙️ Audio-to-text with speech recognition
   - 📄 CSV/Excel batch upload

### 2. **Professional UI Design**
   - Clean, hospital-suitable interface
   - Accessible color scheme (WCAG compliant)
   - Responsive design (mobile-friendly)
   - Real-time feedback and loading indicators

### 3. **Advanced Functionality**
   - Real-time speech-to-text transcription
   - Drag-and-drop file upload
   - Batch processing of multiple incidents
   - Export results to CSV
   - Color-coded classification badges

### 4. **Classification System**
   - **NSE**: No Safety Event (Green)
   - **NME**: Near Miss Event (Yellow)
   - **PSE**: Precursor Safety Event (Orange)
   - **SSE**: Serious Safety Event (Red)

---

## 🎨 UI Design Highlights

### Color Scheme
- Primary: #0066cc (Professional blue)
- Success: #28a745 (Safe green)
- Warning: #ffc107 (Attention yellow)
- Danger: #dc3545 (Critical red)
- Background: #f5f7fa (Soft neutral)

### Typography
- System fonts for optimal readability
- Clear hierarchical structure
- Appropriate contrast ratios

### Components
- Card-based layout
- Interactive buttons with hover effects
- Smooth animations and transitions
- Visual feedback for all actions

---

## 🔧 Technical Stack

### Backend
- **Flask**: Web framework
- **Pandas**: Data processing
- **Google GenAI**: LLM integration

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with flexbox/grid
- **JavaScript**: Interactive functionality
- **Web Speech API**: Audio-to-text conversion

### Deployment
- **Docker**: Containerization
- **Gunicorn-ready**: Production deployment

---

## 🚀 Quick Start Commands

### Local Development
```bash
cd src/frontend
./run.sh
```

### Docker Development
```bash
cd src/frontend
./docker-shell.sh
```

### Access Application
```
http://localhost:8080
```

---

## 📊 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Main application UI |
| `/api/classify` | POST | Classify single incident |
| `/api/classify-batch` | POST | Process CSV file |
| `/api/export` | POST | Export results to CSV |
| `/health` | GET | Health check |

---

## 🎯 User Workflows

### Single Incident (Text)
1. Select "Text Input"
2. Enter description
3. Click "Classify"
4. View results
5. Export if needed

### Voice Input
1. Select "Audio Input"
2. Start recording
3. Speak description
4. Stop recording
5. Review transcript
6. Classify
7. View results

### Batch Processing
1. Select "Upload CSV"
2. Drop file or browse
3. Click "Process File"
4. View all results
5. Export combined results

---

## 🔒 Security Features

- File type validation (CSV/XLSX only)
- File size limits (16MB max)
- Input sanitization
- Secure credential management
- HTTPS-ready configuration

---

## 📱 Browser Compatibility

| Browser | Text Input | Audio Input | File Upload |
|---------|-----------|-------------|-------------|
| Chrome 80+ | ✅ | ✅ | ✅ |
| Edge 80+ | ✅ | ✅ | ✅ |
| Safari 14+ | ✅ | ✅ | ✅ |
| Firefox 75+ | ✅ | ❌ | ✅ |

---

## 🎓 Usage Tips

1. **Text Input**: Fastest for single incidents
2. **Audio Input**: Best for hands-free documentation
3. **CSV Upload**: Efficient for bulk processing
4. **Export Feature**: Keep records for compliance
5. **Clear Descriptions**: More detail = better classification

---

## 📈 Performance

- Single incident: ~3-5 seconds
- Batch processing: ~3-5 seconds per incident
- Audio transcription: Real-time
- File upload: Instant (under 16MB)

---

## 🎨 Design Philosophy

1. **Professional**: Clinical-grade appearance
2. **Accessible**: WCAG 2.1 AA compliant
3. **Intuitive**: Minimal learning curve
4. **Efficient**: Fast workflows
5. **Reliable**: Clear error messaging

---

## 🔮 Future Enhancements

Potential additions:
- Multi-language support
- Advanced filtering/search
- Historical trend analysis
- PDF report generation
- User authentication
- Audit logging
- Integration with EHR systems

---

## 📞 Support

- See `README.md` for full documentation
- See `QUICKSTART.md` for quick setup
- Check `sample_incidents.csv` for examples

---

**Built for Healthcare Professionals** 🏥

*Ensuring patient safety through intelligent incident classification*
