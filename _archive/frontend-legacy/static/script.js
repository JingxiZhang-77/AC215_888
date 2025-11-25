// Global state
let currentResults = [];
let mediaRecorder = null;
let audioChunks = [];
let recordingStartTime = null;
let recordingTimer = null;
let recognition = null;
let textInputCount = 1;
const MAX_TEXT_INPUTS = 5;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
    initializeSpeechRecognition();
    updateAddButtonState();
});

// ============ Template Download ============
function downloadTemplate() {
    // Download template from server
    window.location.href = '/api/download-template';
}

// ============ Input Method Switching ============
function showMethod(method) {
    // Hide all sections
    document.querySelectorAll('.input-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.method-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected section and activate button
    if (method === 'text') {
        document.getElementById('text-section').style.display = 'block';
        document.getElementById('text-btn').classList.add('active');
    } else if (method === 'audio') {
        document.getElementById('audio-section').style.display = 'block';
        document.getElementById('audio-btn').classList.add('active');
    } else if (method === 'upload') {
        document.getElementById('upload-section').style.display = 'block';
        document.getElementById('upload-btn').classList.add('active');
    }
    
    // Hide results when switching methods
    hideResults();
}

// ============ Text Input Classification ============
function addTextInput() {
    if (textInputCount >= MAX_TEXT_INPUTS) {
        return;
    }
    
    textInputCount++;
    const container = document.getElementById('text-inputs-container');
    
    const inputItem = document.createElement('div');
    inputItem.className = 'text-input-item';
    inputItem.setAttribute('data-index', textInputCount);
    
    inputItem.innerHTML = `
        <div class="input-header">
            <span class="input-number">Incident #${textInputCount}</span>
            <button class="remove-input-btn" onclick="removeTextInput(${textInputCount})">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z" fill="currentColor"/>
                </svg>
                Remove
            </button>
        </div>
        <textarea 
            class="incident-textarea" 
            placeholder="Please provide a detailed description of the safety event incident..."
            rows="5"
        ></textarea>
    `;
    
    container.appendChild(inputItem);
    updateAddButtonState();
}

function removeTextInput(index) {
    const item = document.querySelector(`.text-input-item[data-index="${index}"]`);
    if (item) {
        item.remove();
        textInputCount--;
        updateAddButtonState();
        renumberTextInputs();
    }
}

function renumberTextInputs() {
    const items = document.querySelectorAll('.text-input-item');
    items.forEach((item, index) => {
        const newIndex = index + 1;
        item.setAttribute('data-index', newIndex);
        const numberSpan = item.querySelector('.input-number');
        if (numberSpan) {
            numberSpan.textContent = `Incident #${newIndex}`;
        }
        const removeBtn = item.querySelector('.remove-input-btn');
        if (removeBtn) {
            removeBtn.setAttribute('onclick', `removeTextInput(${newIndex})`);
        }
    });
    textInputCount = items.length;
}

function updateAddButtonState() {
    const addBtn = document.getElementById('add-input-btn');
    if (addBtn) {
        if (textInputCount >= MAX_TEXT_INPUTS) {
            addBtn.disabled = true;
            addBtn.style.opacity = '0.5';
            addBtn.style.cursor = 'not-allowed';
        } else {
            addBtn.disabled = false;
            addBtn.style.opacity = '1';
            addBtn.style.cursor = 'pointer';
        }
    }
}

async function classifyMultipleIncidents() {
    const textareas = document.querySelectorAll('.incident-textarea');
    const descriptions = [];
    
    // Collect all non-empty descriptions
    textareas.forEach(textarea => {
        const text = textarea.value.trim();
        if (text) {
            descriptions.push(text);
        }
    });
    
    if (descriptions.length === 0) {
        alert('Please enter at least one incident description');
        return;
    }
    
    showLoading();
    
    try {
        const results = [];
        
        // Process each description
        for (let i = 0; i < descriptions.length; i++) {
            const response = await fetch('/api/classify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ description: descriptions[i] })
            });
            
            if (response.status === 403) {
                alert('Access denied. Only Doctors, Nurses, and Administrators can classify events.');
                hideLoading();
                return;
            }
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Classification failed for incident #${i + 1}`);
            }
            
            const result = await response.json();
            result.incident_number = i + 1;
            results.push(result);
        }
        
        currentResults = results;
        displayResults(currentResults);
        
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during classification: ' + error.message);
    } finally {
        hideLoading();
    }
}

// ============ Audio Input with Speech Recognition ============
function initializeSpeechRecognition() {
    // Check if browser supports speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        
        let finalTranscript = '';
        
        recognition.onresult = function(event) {
            let interimTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }
            
            document.getElementById('audio-transcript').value = finalTranscript + interimTranscript;
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            stopRecording();
        };
        
        recognition.onend = function() {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                // Restart if still recording
                recognition.start();
            }
        };
    }
}

function toggleRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        stopRecording();
    } else {
        startRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            // Could be used for backend transcription if needed
        };
        
        mediaRecorder.start();
        
        // Start speech recognition
        if (recognition) {
            recognition.start();
        }
        
        // Update UI
        document.getElementById('record-btn').classList.add('recording');
        document.getElementById('record-text').textContent = 'Stop Recording';
        document.getElementById('recording-status').style.display = 'flex';
        document.getElementById('audio-transcript-container').style.display = 'block';
        
        // Start timer
        recordingStartTime = Date.now();
        updateRecordingTimer();
        recordingTimer = setInterval(updateRecordingTimer, 1000);
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Could not access microphone. Please ensure you have granted microphone permissions.');
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
    
    if (recognition) {
        recognition.stop();
    }
    
    // Update UI
    document.getElementById('record-btn').classList.remove('recording');
    document.getElementById('record-text').textContent = 'Start Recording';
    document.getElementById('recording-status').style.display = 'none';
    
    // Stop timer
    if (recordingTimer) {
        clearInterval(recordingTimer);
        recordingTimer = null;
    }
}

function updateRecordingTimer() {
    if (recordingStartTime) {
        const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        document.getElementById('recording-time').textContent = 
            `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }
}

async function classifyAudioIncident() {
    const transcript = document.getElementById('audio-transcript').value.trim();
    
    if (!transcript) {
        alert('Please record an incident description first');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/classify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ description: transcript })
        });
        
        if (!response.ok) {
            throw new Error('Classification failed');
        }
        
        const result = await response.json();
        currentResults = [result];
        displayResults(currentResults);
        
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during classification. Please try again.');
    } finally {
        hideLoading();
    }
}

// ============ File Upload ============
function initializeFileUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    
    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // File selected
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });
}

function handleFileSelect(file) {
    const validTypes = ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'];
    
    if (!validTypes.includes(file.type) && !file.name.match(/\.(csv|xlsx)$/i)) {
        alert('Please select a CSV or XLSX file');
        return;
    }
    
    // Create a new DataTransfer to set the file
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    document.getElementById('file-input').files = dataTransfer.files;
    
    // Update UI
    document.getElementById('filename').textContent = file.name;
    document.getElementById('file-selected').style.display = 'block';
    document.getElementById('upload-area').style.display = 'none';
}

function resetFileUpload() {
    const fileInput = document.getElementById('file-input');
    fileInput.value = '';
    document.getElementById('file-selected').style.display = 'none';
    document.getElementById('upload-area').style.display = 'block';
}

async function processBatchFile() {
    const fileInput = document.getElementById('file-input');
    
    if (!fileInput.files.length) {
        alert('Please select a file first');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    // Disable buttons during processing
    const processBtn = event.target;
    const changeBtn = processBtn.parentElement.querySelector('button:last-child');
    processBtn.disabled = true;
    if (changeBtn) changeBtn.disabled = true;
    
    showLoading();
    
    try {
        const response = await fetch('/api/classify-batch', {
            method: 'POST',
            body: formData
        });
        
        if (response.status === 403) {
            alert('Access denied. Only Doctors, Nurses, and Administrators can classify events.');
            processBtn.disabled = false;
            if (changeBtn) changeBtn.disabled = false;
            hideLoading();
            return;
        }
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'File processing failed');
        }
        
        const data = await response.json();
        currentResults = data.results;
        displayResults(currentResults);
        
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while processing the file: ' + error.message);
        // Re-enable buttons on error
        processBtn.disabled = false;
        if (changeBtn) changeBtn.disabled = false;
    } finally {
        hideLoading();
    }
}

// ============ Display Results ============
function displayResults(results) {
    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = '';
    
    results.forEach((result, index) => {
        const resultElement = createResultElement(result, index + 1);
        resultsContainer.appendChild(resultElement);
    });
    
    document.getElementById('results-section').style.display = 'block';
    
    // Scroll to results
    document.getElementById('results-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function createResultElement(result, index) {
    const div = document.createElement('div');
    div.className = 'result-item';
    
    const classification = result.final_classification_code || 'Unknown';
    
    // Build rationale sections
    let rationaleHTML = '';
    
    // Add GAPS rationale if check was performed
    if (result.gaps_deviation_check && result.gaps_deviation_check !== 'N/A' && result.gaps_rationale) {
        rationaleHTML += `
            <div class="rationale-section">
                <strong>GAPS Deviation Analysis:</strong>
                <p>${escapeHtml(result.gaps_rationale)}</p>
            </div>
        `;
    }
    
    // Add Reached Patient rationale if check was performed
    if (result.reached_patient_check && result.reached_patient_check !== 'N/A' && result.reached_patient_rationale) {
        rationaleHTML += `
            <div class="rationale-section">
                <strong>Patient Impact Analysis:</strong>
                <p>${escapeHtml(result.reached_patient_rationale)}</p>
            </div>
        `;
    }
    
    // Add Harm Level rationale if check was performed
    if (result.harm_level_check && result.harm_level_check !== 'N/A' && result.harm_level_rationale) {
        rationaleHTML += `
            <div class="rationale-section">
                <strong>Harm Level Analysis:</strong>
                <p>${escapeHtml(result.harm_level_rationale)}</p>
            </div>
        `;
    }
    
    // Add final rationale
    if (result.final_rationale) {
        rationaleHTML += `
            <div class="rationale-section final-rationale">
                <strong>Final Classification:</strong>
                <p>${escapeHtml(result.final_rationale)}</p>
            </div>
        `;
    }
    
    div.innerHTML = `
        <div class="result-header">
            <span class="incident-number">Incident #${index}</span>
            <span class="classification-badge badge-${classification}">${classification}</span>
        </div>
        
        <div class="incident-description">
            <strong>Incident Description:</strong>
            ${escapeHtml(result.incident)}
        </div>
        
        <div class="checks-grid">
            <div class="check-item">
                <span class="check-label">GAPS Deviation?</span>
                <span class="check-value ${result.gaps_deviation_check?.toLowerCase()}">${result.gaps_deviation_check}</span>
            </div>
            <div class="check-item">
                <span class="check-label">Reached Patient?</span>
                <span class="check-value ${result.reached_patient_check?.toLowerCase()}">${result.reached_patient_check}</span>
            </div>
            <div class="check-item">
                <span class="check-label">Significant Harm?</span>
                <span class="check-value ${result.harm_level_check?.toLowerCase()}">${result.harm_level_check}</span>
            </div>
        </div>
        
        <div class="rationale">
            ${rationaleHTML}
        </div>
    `;
    
    return div;
}

// ============ Export Results ============
async function exportResults() {
    if (currentResults.length === 0) {
        alert('No results to export');
        return;
    }
    
    try {
        const response = await fetch('/api/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ results: currentResults })
        });
        
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `safety_event_results_${Date.now()}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while exporting results. Please try again.');
    }
}

// ============ UI Helpers ============
function showLoading() {
    document.getElementById('loading').style.display = 'block';
    hideResults();
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function hideResults() {
    document.getElementById('results-section').style.display = 'none';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============ Classification Legend ============
const CLASSIFICATION_INFO = {
    'NSE': {
        name: 'No Safety Event',
        description: 'No deviation from Generally Accepted Performance Standards (GAPS)'
    },
    'NME': {
        name: 'Near Miss Event',
        description: 'Deviation occurred but did not reach the patient'
    },
    'PSE': {
        name: 'Precursor Safety Event',
        description: 'Deviation reached the patient with no or minimal harm'
    },
    'SSE': {
        name: 'Serious Safety Event',
        description: 'Deviation reached the patient and caused moderate/severe harm or death'
    }
};
