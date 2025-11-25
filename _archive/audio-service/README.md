# Audio-to-Text Service

## Overview
This service provides audio-to-text transcription capabilities for the Safety Event Classification System using Google Cloud Speech-to-Text API.

## Features
- Audio file transcription using Google Cloud Speech-to-Text
- Medical dictation model for better accuracy with medical terminology
- Support for various audio formats (WAV, MP3, etc.)
- Automatic audio format conversion
- Punctuation and formatting

## Setup

### Prerequisites
- Docker
- Google Cloud service account with Speech-to-Text API enabled
- Service account key file in `../../secrets/llm-service-account.json`

### Running the Service

```bash
cd src/audio-service
./docker-shell.sh
```

## Usage

### Command Line
```bash
python audio_transcriber.py <path_to_audio_file>
```

### Python API
```python
from audio_transcriber import transcribe_audio_file

# Transcribe an audio file
transcript = transcribe_audio_file("path/to/audio.wav")
print(transcript)
```

### As a Module
```python
from audio_transcriber import AudioTranscriber

transcriber = AudioTranscriber()
transcript = transcriber.transcribe_file("path/to/audio.mp3")
```

## Technical Details

### Audio Requirements
- The service automatically converts audio to:
  - Format: WAV
  - Sample Rate: 16kHz
  - Channels: Mono
  - Bit Depth: 16-bit

### Speech-to-Text Configuration
- Model: `medical_dictation` (optimized for medical terminology)
- Language: English (en-US) by default
- Features:
  - Automatic punctuation
  - Enhanced model for better accuracy

## Dependencies
- `google-cloud-speech` - Google Cloud Speech-to-Text API client
- `pydub` - Audio manipulation library
- `ffmpeg` - Audio codec support (installed in Docker image)

## Environment Variables
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account key
- `GCP_PROJECT` - Google Cloud Project ID
- `GCP_LOCATION` - Google Cloud region
