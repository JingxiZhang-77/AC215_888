# Quick Start Guide - Safety Event Classification Frontend

## 🚀 Get Started in 3 Steps

### Step 1: Navigate to Frontend Directory
```bash
cd src/frontend
```

### Step 2: Run the Application
```bash
./run.sh
```

### Step 3: Open Your Browser
Navigate to: **http://localhost:8080**

---

## 📝 Using the Application

### Option 1: Text Input (Fastest)
1. Click **"Text Input"** button
2. Type or paste incident description
3. Click **"Classify Incident"**

### Option 2: Voice Input (Hands-free)
1. Click **"Audio Input"** button
2. Click **"Start Recording"**
3. Speak incident description
4. Click **"Stop Recording"**
5. Click **"Classify Transcript"**

### Option 3: Batch Upload (Multiple Incidents)
1. Click **"Upload CSV"** button
2. Drag & drop your CSV/Excel file
3. Click **"Process File"**

---

## 📊 Sample Test

Try this sample incident:
```
Nurse administered 10mg of Morphine instead of prescribed 5mg 
to patient in Room 305. Patient experienced drowsiness but 
recovered without complications.
```

Expected Result: **PSE** (Precursor Safety Event)

---

## 📄 CSV File Format

Your CSV should have a column with incident descriptions:

```csv
Brief Factual Description
"Incident description 1..."
"Incident description 2..."
```

A sample file is included: `sample_incidents.csv`

---

## 🔧 Troubleshooting

**Port already in use?**
```bash
# Find process using port 8080
lsof -ti:8080 | xargs kill -9
```

**Module import errors?**
```bash
pip install -r requirements.txt
```

**Audio not working?**
- Use Chrome, Edge, or Safari browser
- Allow microphone permissions when prompted

---

## 🛑 Stopping the Server

Press **Ctrl + C** in the terminal

---

## 📚 Full Documentation

See `README.md` for complete documentation including:
- API endpoints
- Docker deployment
- Production setup
- Advanced features

---

## 💡 Tips

- Use text input for fastest results
- Voice input works best in quiet environments
- CSV upload can process 100+ incidents at once
- Export results to CSV for record keeping

---

**Need Help?** Check the main README.md or contact support.
