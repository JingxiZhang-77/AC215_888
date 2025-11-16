"""
Audio-to-Text Transcription Service
Converts audio files to text using Google Cloud Speech-to-Text API
"""

import os
import tempfile
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment
import io

# GCP configuration
GCP_PROJECT = os.environ.get("GCP_PROJECT", "apcomp215-group88")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "us-central1")


class AudioTranscriber:
    """Handle audio transcription using Google Cloud Speech-to-Text"""
    
    def __init__(self):
        """Initialize the Speech client"""
        self.client = speech.SpeechClient()
    
    def convert_audio_to_wav(self, audio_file_path: str) -> bytes:
        """
        Convert audio file to WAV format suitable for Speech API
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            WAV audio data as bytes
        """
        try:
            # Load audio file
            audio = AudioSegment.from_file(audio_file_path)
            
            # Convert to mono, 16kHz, 16-bit WAV
            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(16000)
            audio = audio.set_sample_width(2)  # 16-bit
            
            # Export to bytes
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            
            return wav_io.read()
            
        except Exception as e:
            raise Exception(f"Error converting audio file: {str(e)}")
    
    def transcribe_audio(self, audio_content: bytes, language_code: str = "en-US") -> str:
        """
        Transcribe audio content to text
        
        Args:
            audio_content: Audio data in bytes (WAV format)
            language_code: Language code for transcription (default: en-US)
            
        Returns:
            Transcribed text
        """
        try:
            audio = speech.RecognitionAudio(content=audio_content)
            
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language_code,
                enable_automatic_punctuation=True,
                model="medical_dictation",  # Optimized for medical terminology
                use_enhanced=True,
            )
            
            # Perform transcription
            response = self.client.recognize(config=config, audio=audio)
            
            # Combine all transcripts
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript + " "
            
            return transcript.strip()
            
        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")
    
    def transcribe_file(self, audio_file_path: str, language_code: str = "en-US") -> str:
        """
        Transcribe an audio file to text
        
        Args:
            audio_file_path: Path to audio file
            language_code: Language code (default: en-US)
            
        Returns:
            Transcribed text
        """
        # Convert audio to appropriate format
        wav_content = self.convert_audio_to_wav(audio_file_path)
        
        # Transcribe
        return self.transcribe_audio(wav_content, language_code)


def transcribe_audio_file(audio_file_path: str) -> str:
    """
    Convenience function to transcribe an audio file
    
    Args:
        audio_file_path: Path to the audio file
        
    Returns:
        Transcribed text
    """
    transcriber = AudioTranscriber()
    return transcriber.transcribe_file(audio_file_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Transcribe audio file to text")
    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument("--language", default="en-US", help="Language code (default: en-US)")
    
    args = parser.parse_args()
    
    try:
        print(f"Transcribing audio file: {args.audio_file}")
        transcript = transcribe_audio_file(args.audio_file)
        print(f"\nTranscript:\n{transcript}")
    except Exception as e:
        print(f"Error: {e}")
