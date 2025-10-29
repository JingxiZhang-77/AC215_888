# Safety Event Classification System - Testing Guide

## 🧪 Comprehensive Testing Documentation

This guide covers all testing scenarios for the Safety Event Classification System frontend.

---

## 📋 Table of Contents

1. [Pre-Testing Setup](#pre-testing-setup)
2. [Unit Tests](#unit-tests)
3. [Integration Tests](#integration-tests)
4. [UI/UX Tests](#uiux-tests)
5. [Browser Compatibility Tests](#browser-compatibility-tests)
6. [Performance Tests](#performance-tests)
7. [Security Tests](#security-tests)
8. [Accessibility Tests](#accessibility-tests)
9. [Sample Test Cases](#sample-test-cases)

---

## 🔧 Pre-Testing Setup

### 1. Start the Application

```bash
cd src/frontend
./run.sh
```

Wait for: `Running on http://0.0.0.0:8080`

### 2. Verify Health Check

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{"status": "healthy"}
```

### 3. Open in Browser

Navigate to: `http://localhost:8080`

---

## 🔬 Unit Tests

### Test 1: Text Input Classification

**Objective**: Verify single incident classification via text input

**Steps**:
1. Click "Text Input" button
2. Enter test incident:
   ```
   Nurse administered 10mg of Morphine instead of prescribed 5mg to patient in Room 305. 
   Patient experienced drowsiness but recovered without complications.
   ```
3. Click "Classify Incident"

**Expected Result**:
- Loading indicator appears
- Classification result displays
- Result shows: PSE (Precursor Safety Event)
- Rationale: "Deviation reached the patient with no or minimal harm."
- All three checks visible:
  - GAPS Deviation: Yes
  - Reached Patient: Yes
  - Significant Harm: No

**Pass Criteria**: ✅ Classification matches expected, all fields populated

---

### Test 2: Empty Text Input Validation

**Objective**: Verify input validation

**Steps**:
1. Click "Text Input" button
2. Leave textarea empty
3. Click "Classify Incident"

**Expected Result**:
- Alert: "Please enter an incident description"
- No API call made
- No results displayed

**Pass Criteria**: ✅ Validation prevents empty submissions

---

### Test 3: Audio Recording Start/Stop

**Objective**: Verify audio recording functionality

**Steps**:
1. Click "Audio Input" button
2. Click "Start Recording"
3. Allow microphone permissions
4. Wait 5 seconds
5. Click "Stop Recording"

**Expected Result**:
- Recording status shows "Recording..."
- Timer counts up (0:01, 0:02, 0:03...)
- Recording button changes to "Stop Recording"
- After stopping, transcript area appears
- Timer stops

**Pass Criteria**: ✅ Recording controls work correctly, UI updates appropriately

---

### Test 4: Audio Transcription

**Objective**: Verify speech-to-text transcription

**Steps**:
1. Click "Audio Input" button
2. Click "Start Recording"
3. Speak clearly: "A patient received the wrong medication but the error was caught before administration"
4. Click "Stop Recording"
5. Review transcript

**Expected Result**:
- Transcript appears in text area
- Text closely matches spoken words
- "Classify Transcript" button enabled

**Pass Criteria**: ✅ Transcription accuracy >80%

---

### Test 5: CSV File Upload

**Objective**: Verify file upload and batch processing

**Steps**:
1. Click "Upload CSV" button
2. Upload `sample_incidents.csv`
3. Click "Process File"

**Expected Result**:
- File name displays
- Loading indicator appears
- Multiple results display (5 incidents)
- Each result has classification
- Export button appears

**Pass Criteria**: ✅ All 5 incidents processed and classified correctly

---

### Test 6: Invalid File Upload

**Objective**: Verify file type validation

**Steps**:
1. Click "Upload CSV" button
2. Try uploading a .txt or .pdf file

**Expected Result**:
- Error message: "Invalid file type. Please upload CSV or XLSX file"
- No processing occurs

**Pass Criteria**: ✅ Invalid files rejected with clear error message

---

### Test 7: Drag and Drop Upload

**Objective**: Verify drag-and-drop functionality

**Steps**:
1. Click "Upload CSV" button
2. Drag `sample_incidents.csv` from desktop
3. Drop onto upload area
4. Click "Process File"

**Expected Result**:
- Drop zone highlights during drag
- File accepted on drop
- File name displays
- Processing succeeds

**Pass Criteria**: ✅ Drag-and-drop works smoothly

---

### Test 8: Export Results to CSV

**Objective**: Verify CSV export functionality

**Steps**:
1. Complete any classification (text, audio, or upload)
2. Click "Export to CSV" button

**Expected Result**:
- CSV file downloads automatically
- Filename: `safety_event_results_[timestamp].csv`
- File contains all result columns
- Data matches displayed results

**Pass Criteria**: ✅ Export file created with correct data

---

## 🔗 Integration Tests

### Test 9: API - Single Classification

**Objective**: Test API endpoint directly

**Command**:
```bash
curl -X POST http://localhost:8080/api/classify \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Wrong patient almost received blood transfusion - error caught during final ID verification check at bedside."
  }'
```

**Expected Response**:
```json
{
  "incident": "Wrong patient almost received blood transfusion...",
  "gaps_deviation_check": "Yes",
  "reached_patient_check": "No",
  "harm_level_check": "N/A",
  "final_classification_code": "NME",
  "rationale": "Deviation occurred but did not reach the patient.",
  "status": "success"
}
```

**Pass Criteria**: ✅ API returns correct classification structure

---

### Test 10: API - Batch Classification

**Objective**: Test batch processing endpoint

**Command**:
```bash
curl -X POST http://localhost:8080/api/classify-batch \
  -F "file=@sample_incidents.csv"
```

**Expected Response**:
```json
{
  "results": [...],
  "count": 5
}
```

**Pass Criteria**: ✅ All incidents processed, count matches

---

### Test 11: API - Error Handling

**Objective**: Verify API error responses

**Command**:
```bash
curl -X POST http://localhost:8080/api/classify \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response**:
```json
{
  "error": "No description provided"
}
```

**Status Code**: 400

**Pass Criteria**: ✅ Appropriate error message and status code

---

## 🎨 UI/UX Tests

### Test 12: Method Switching

**Objective**: Verify smooth transitions between input methods

**Steps**:
1. Start on Text Input
2. Click "Audio Input"
3. Click "Upload CSV"
4. Click back to "Text Input"

**Expected Result**:
- Only active method visible
- Button styling updates (active class)
- Previous inputs not lost unless intentional
- Smooth transitions

**Pass Criteria**: ✅ Clean method switching without glitches

---

### Test 13: Responsive Design - Mobile

**Objective**: Test mobile responsiveness

**Steps**:
1. Open browser DevTools (F12)
2. Toggle device toolbar
3. Select iPhone 12 Pro
4. Test all three input methods

**Expected Result**:
- Layout adapts to mobile screen
- Buttons stack vertically if needed
- Text remains readable
- No horizontal scrolling
- Touch targets adequate size

**Pass Criteria**: ✅ Fully functional on mobile viewport

---

### Test 14: Responsive Design - Tablet

**Objective**: Test tablet responsiveness

**Steps**:
1. Open browser DevTools
2. Select iPad Pro
3. Test all features

**Expected Result**:
- Layout optimized for tablet
- Touch-friendly interface
- All features accessible

**Pass Criteria**: ✅ Fully functional on tablet viewport

---

### Test 15: Loading States

**Objective**: Verify loading indicators

**Steps**:
1. Submit any classification
2. Observe loading animation
3. Wait for results

**Expected Result**:
- Spinner appears immediately
- "Processing incident(s)..." message shows
- Previous results hidden
- Loading disappears when complete

**Pass Criteria**: ✅ Clear feedback during processing

---

### Test 16: Results Display

**Objective**: Verify results formatting

**Steps**:
1. Process multiple incidents via CSV
2. Review results display

**Expected Result**:
- Each incident clearly separated
- Classification badges color-coded correctly:
  - NSE: Green background
  - NME: Yellow background
  - PSE: Orange background
  - SSE: Red background
- All fields populated
- Readable font sizes
- Proper spacing

**Pass Criteria**: ✅ Results clear and professional

---

## 🌐 Browser Compatibility Tests

### Test 17: Chrome (Latest)

**Test All Features**:
- ✅ Text input
- ✅ Audio recording
- ✅ File upload
- ✅ Export

**Pass Criteria**: All features work

---

### Test 18: Safari (Latest)

**Test All Features**:
- ✅ Text input
- ✅ Audio recording
- ✅ File upload
- ✅ Export

**Pass Criteria**: All features work

---

### Test 19: Firefox (Latest)

**Test All Features**:
- ✅ Text input
- ⚠️ Audio recording (expected to not work)
- ✅ File upload
- ✅ Export

**Pass Criteria**: Text and upload work; audio gracefully unsupported

---

### Test 20: Edge (Latest)

**Test All Features**:
- ✅ Text input
- ✅ Audio recording
- ✅ File upload
- ✅ Export

**Pass Criteria**: All features work

---

## ⚡ Performance Tests

### Test 21: Single Classification Speed

**Objective**: Measure response time

**Steps**:
1. Enter short incident description
2. Time from click to result display

**Expected Result**:
- Response time: 3-5 seconds
- UI remains responsive

**Pass Criteria**: ✅ Results within 10 seconds

---

### Test 22: Batch Processing Performance

**Objective**: Test large file processing

**Steps**:
1. Create CSV with 50 incidents
2. Upload and process
3. Monitor time and performance

**Expected Result**:
- Processing: ~3-5 seconds per incident
- Total time: 2.5-4 minutes for 50 incidents
- No browser freezing
- Progress indication clear

**Pass Criteria**: ✅ Completes without errors or crashes

---

### Test 23: File Size Limits

**Objective**: Verify file size restrictions

**Steps**:
1. Try uploading file >16MB

**Expected Result**:
- Error message displayed
- Upload rejected
- No server crash

**Pass Criteria**: ✅ Large files rejected gracefully

---

### Test 24: Concurrent Users Simulation

**Objective**: Test multiple simultaneous requests

**Steps**:
1. Open application in 3 different browsers
2. Submit classifications simultaneously

**Expected Result**:
- All requests complete successfully
- No interference between sessions
- Results correct for each

**Pass Criteria**: ✅ Handles concurrent users

---

## 🔒 Security Tests

### Test 25: XSS Prevention

**Objective**: Verify input sanitization

**Steps**:
1. Enter text with HTML/script tags:
   ```html
   <script>alert('XSS')</script> Test incident
   ```
2. Submit classification

**Expected Result**:
- No script execution
- Text displayed safely escaped
- No alerts popup

**Pass Criteria**: ✅ XSS attempts blocked

---

### Test 26: File Type Validation

**Objective**: Verify only allowed file types accepted

**Steps**:
1. Try uploading .exe, .js, .html files
2. Rename .txt to .csv and upload

**Expected Result**:
- Executable files rejected
- Only genuine CSV/XLSX accepted

**Pass Criteria**: ✅ File validation robust

---

### Test 27: SQL Injection Prevention

**Objective**: Test against SQL injection (if applicable)

**Steps**:
1. Enter text with SQL syntax:
   ```sql
   '; DROP TABLE incidents; --
   ```
2. Submit classification

**Expected Result**:
- Treated as plain text
- No database errors
- Classification proceeds normally

**Pass Criteria**: ✅ SQL injection prevented

---

## ♿ Accessibility Tests

### Test 28: Keyboard Navigation

**Objective**: Verify full keyboard accessibility

**Steps**:
1. Use only Tab, Shift+Tab, Enter, Space
2. Navigate through all UI elements
3. Complete a classification

**Expected Result**:
- All interactive elements reachable
- Focus indicators visible
- Enter/Space activates buttons
- Logical tab order

**Pass Criteria**: ✅ Fully keyboard accessible

---

### Test 29: Screen Reader Compatibility

**Objective**: Test with screen reader (NVDA/VoiceOver)

**Steps**:
1. Enable screen reader
2. Navigate through application
3. Perform classification

**Expected Result**:
- All elements announced properly
- Form labels read correctly
- Results understandable
- Navigation clear

**Pass Criteria**: ✅ Screen reader friendly

---

### Test 30: Color Contrast

**Objective**: Verify WCAG compliance

**Steps**:
1. Use browser DevTools Lighthouse
2. Run accessibility audit

**Expected Result**:
- Contrast ratio ≥4.5:1 for normal text
- Contrast ratio ≥3:1 for large text
- All text passes WCAG AA

**Pass Criteria**: ✅ Meets WCAG 2.1 AA standards

---

## 📝 Sample Test Cases

### NSE Classification Test

**Input**:
```
Staff member washed hands before patient contact following standard protocol. 
No issues observed.
```

**Expected**: NSE (No Safety Event)

---

### NME Classification Test

**Input**:
```
Pharmacy dispensed wrong medication - gave Amoxicillin instead of prescribed 
Augmentin. Error caught by nurse before administration.
```

**Expected**: NME (Near Miss Event)

---

### PSE Classification Test

**Input**:
```
Patient fell while attempting to use bathroom unassisted. Sustained minor 
bruising on left hip, no fractures detected.
```

**Expected**: PSE (Precursor Safety Event)

---

### SSE Classification Test

**Input**:
```
Surgical instrument left inside patient during procedure. Discovered on 
post-op X-ray. Patient required second surgery for removal and experienced 
infection requiring extended hospital stay.
```

**Expected**: SSE (Serious Safety Event)

---

## 🐛 Known Issues / Limitations

1. **Audio Input**:
   - Not supported in Firefox
   - Requires HTTPS in production
   - Accuracy varies with audio quality

2. **Large Files**:
   - Processing >100 incidents may be slow
   - Consider batch size recommendations

3. **Browser Caching**:
   - May need hard refresh (Ctrl+Shift+R) after updates

---

## ✅ Test Checklist

### Basic Functionality
- [ ] Text input classification
- [ ] Audio recording and transcription
- [ ] CSV file upload
- [ ] Results display
- [ ] Export to CSV

### Error Handling
- [ ] Empty input validation
- [ ] Invalid file type rejection
- [ ] Network error handling
- [ ] API error responses

### UI/UX
- [ ] Method switching
- [ ] Loading indicators
- [ ] Responsive design (mobile/tablet)
- [ ] Button states and feedback

### Browser Compatibility
- [ ] Chrome
- [ ] Safari
- [ ] Firefox
- [ ] Edge

### Performance
- [ ] Single classification speed
- [ ] Batch processing
- [ ] File size limits
- [ ] Concurrent users

### Security
- [ ] XSS prevention
- [ ] File validation
- [ ] Input sanitization

### Accessibility
- [ ] Keyboard navigation
- [ ] Screen reader compatibility
- [ ] Color contrast

---

## 📊 Testing Report Template

```
Test Session: [Date]
Tester: [Name]
Browser: [Browser + Version]
OS: [Operating System]

Tests Passed: __/30
Tests Failed: __/30
Critical Issues: __
Minor Issues: __

Critical Issues Found:
1. [Description]

Minor Issues Found:
1. [Description]

Recommendations:
- [Recommendation 1]
- [Recommendation 2]

Overall Status: ✅ PASS / ❌ FAIL
```

---

## 🚀 Continuous Testing

### Automated Testing (Future)

Consider implementing:
- Selenium for UI automation
- pytest for backend testing
- Jest for JavaScript testing
- Lighthouse CI for performance
- Pa11y for accessibility

### Manual Testing Schedule

- **Before Each Release**: Full test suite
- **Weekly**: Core functionality tests (1-8)
- **Monthly**: Full regression testing
- **Quarterly**: Accessibility audit

---

## 📞 Reporting Issues

If you find bugs during testing:

1. **Document**:
   - Steps to reproduce
   - Expected vs actual behavior
   - Browser/OS details
   - Screenshots if applicable

2. **Report**:
   - Create GitHub issue
   - Tag with priority (Critical/High/Medium/Low)
   - Include test number if applicable

3. **Verify Fix**:
   - Retest after fix deployed
   - Confirm issue resolved
   - Update test documentation

---

**Happy Testing! 🧪**

*Ensuring quality and reliability for healthcare professionals*
