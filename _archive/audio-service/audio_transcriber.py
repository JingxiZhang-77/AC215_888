"""
Audio-to-Text Transcription Service with Multi-Language Support

Converts audio files to text using Google Cloud Speech-to-Text API.
Supports English, Mandarin, Cantonese, French, and Spanish.
Includes automatic translation to English for non-English audio.

Author: AC215_888 Team
Date: January 2025
"""

import os
import tempfile
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import translate_v2 as translate
from pydub import AudioSegment
import io
import sys

# GCP configuration
GCP_PROJECT = os.environ.get("GCP_PROJECT", "apcomp215-group88")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "us-central1")

# Supported languages (restricted to 5)
SUPPORTED_LANGUAGES = {
    "en-US": {"name": "English", "needs_translation": False},
    "zh-CN": {"name": "Mandarin (Simplified)", "needs_translation": True},
    "zh-HK": {"name": "Cantonese", "needs_translation": True},
    "fr-FR": {"name": "French", "needs_translation": True},
    "es-ES": {"name": "Spanish", "needs_translation": True}
}


class AudioTranscriber:
    """
    Handle audio transcription using Google Cloud Speech-to-Text
    with multi-language support and automatic translation.
    """
    
    def __init__(self):
        """Initialize the Speech and Translation clients"""
        self.speech_client = speech.SpeechClient()
        self.translate_client = translate.Client()
    
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
    
    def validate_language(self, language_code: str) -> None:
        """
        Validate language code is supported
        
        Args:
            language_code: Language code to validate
            
        Raises:
            ValueError: If language not supported
        """
        if language_code not in SUPPORTED_LANGUAGES:
            supported = ", ".join(SUPPORTED_LANGUAGES.keys())
            raise ValueError(
                f"Language '{language_code}' not supported. "
                f"Supported languages: {supported}"
            )
    
    def transcribe_audio(self, audio_content: bytes, language_code: str = "en-US") -> tuple:
        """
        Transcribe audio content to text
        
        Args:
            audio_content: Audio data in bytes (WAV format)
            language_code: Language code for transcription (default: en-US)
            
        Returns:
            Tuple of (transcribed text, confidence score)
        """
        try:
            # Validate language
            self.validate_language(language_code)
            
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
            response = self.speech_client.recognize(config=config, audio=audio)
            
            # Combine all transcripts and calculate confidence
            transcript_parts = []
            confidences = []
            
            for result in response.results:
                if result.alternatives:
                    alt = result.alternatives[0]
                    transcript_parts.append(alt.transcript)
                    confidences.append(alt.confidence)
            
            transcript = " ".join(transcript_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return transcript, avg_confidence
            
        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")
    
    def translate_to_english(self, text: str, source_language: str) -> str:
        """
        Translate text to English using Google Translate
        
        Args:
            text: Text to translate
            source_language: Source language code (e.g., 'zh-CN')
            
        Returns:
            Translated English text
        """
        try:
            # Extract language code without region (zh-CN -> zh)
            source_lang = source_language.split('-')[0]
            
            result = self.translate_client.translate(
                text,
                source_language=source_lang,
                target_language='en'
            )
            
            return result['translatedText']
            
        except Exception as e:
            raise Exception(f"Error translating text: {str(e)}")
    
    def transcribe_file(
        self, 
        audio_file_path: str, 
        language_code: str = "en-US",
        auto_translate: bool = True
    ) -> dict:
        """
        Transcribe an audio file to text with optional translation
        
        Args:
            audio_file_path: Path to audio file
            language_code: Language code (default: en-US)
            auto_translate: Automatically translate non-English to English
            
        Returns:
            Dictionary with transcription results:
            {
                "transcript": str,
                "original_language": str,
                "was_translated": bool,
                "confidence": float,
                "original_transcript": str (if translated)
            }
        """
        # Validate language
        self.validate_language(language_code)
        lang_info = SUPPORTED_LANGUAGES[language_code]
        
        # Convert audio to appropriate format
        wav_content = self.convert_audio_to_wav(audio_file_path)
        
        # Transcribe
        transcript, confidence = self.transcribe_audio(wav_content, language_code)
        
        # Prepare result
        result = {
            "transcript": transcript,
            "original_language": lang_info["name"],
            "original_language_code": language_code,
            "was_translated": False,
            "confidence": confidence
        }
        
        # Translate if needed
        if lang_info["needs_translation"] and auto_translate and transcript:
            print(f"Non-English transcript detected, translating to English...")
            result["original_transcript"] = transcript
            result["transcript"] = self.translate_to_english(transcript, language_code)
            result["was_translated"] = True
        
        return result


def transcribe_audio_file(
    audio_file_path: str, 
    language_code: str = "en-US",
    auto_translate: bool = True
) -> dict:
    """
    Convenience function to transcribe an audio file
    
    Args:
        audio_file_path: Path to the audio file
        language_code: Language of the audio
        auto_translate: Automatically translate to English
        
    Returns:
        Dictionary with transcription results
    """
    transcriber = AudioTranscriber()
    return transcriber.transcribe_file(audio_file_path, language_code, auto_translate)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Transcribe audio file to text with optional translation"
    )
    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument(
        "--language", 
        default="en-US",
        choices=list(SUPPORTED_LANGUAGES.keys()),
        help=f"Language code. Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}"
    )
    parser.add_argument(
        "--no-translate",
        action="store_true",
        help="Disable automatic translation to English"
    )
    
    args = parser.parse_args()
    
    try:
        print(f"\n{'='*60}")
        print(f"Transcribing: {args.audio_file}")
        print(f"Language: {SUPPORTED_LANGUAGES[args.language]['name']}")
        print(f"Auto-translate: {not args.no_translate}")
        print(f"{'='*60}\n")
        
        result = transcribe_audio_file(
            args.audio_file,
            args.language,
            auto_translate=not args.no_translate
        )
        
        print("TRANSCRIPTION RESULT")
        print(f"{'='*60}")
        
        if result["was_translated"]:
            print(f"\nOriginal ({result['original_language']}):")
            print(result['original_transcript'])
            print(f"\nTranslated (English):")
        else:
            print(f"\nTranscript ({result['original_language']}):")
        
        print(result['transcript'])
        print(f"\nConfidence: {result['confidence']:.2%}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
