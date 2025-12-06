"""
Audio Transcription and Translation Service

Multi-language audio transcription with automatic translation to English.
Supports: English, Mandarin, Cantonese, French, Spanish

Author: AC215_888 Team
Date: January 2025
"""

import os
import io
import tempfile
from typing import Tuple, Dict, Any
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import translate_v2 as translate
from google.api_core import exceptions as google_exceptions
from pydub import AudioSegment
import sys

from utils.logger import logger
from utils.config import settings


# Language configuration
SUPPORTED_LANGUAGES = {
    "en-US": {"name": "English", "needs_translation": False},
    "zh-CN": {"name": "Mandarin (Simplified)", "needs_translation": True},
    "zh-HK": {"name": "Cantonese", "needs_translation": True},
    "fr-FR": {"name": "French", "needs_translation": True},
    "es-ES": {"name": "Spanish", "needs_translation": True},
}


class AudioService:
    """
    Service for audio transcription and translation

    Handles multi-language audio input with automatic translation to English
    for downstream classification.
    """

    def __init__(self):
        """Initialize Speech and Translation clients"""
        # Set quota project for Google Cloud APIs
        gcp_project = os.getenv("GCP_PROJECT", "apcomp215-group88")
        os.environ["GOOGLE_CLOUD_QUOTA_PROJECT"] = gcp_project

        self.speech_client = speech.SpeechClient()
        self.translate_client = translate.Client()
        logger.info(f"Audio service initialized with quota project: {gcp_project}")

    def validate_language(self, language_code: str) -> str:
        """
        Validate and normalize language code

        Args:
            language_code: Input language code

        Returns:
            Validated language code

        Raises:
            ValueError: If language not supported
        """
        if language_code not in SUPPORTED_LANGUAGES:
            supported = ", ".join(SUPPORTED_LANGUAGES.keys())
            raise ValueError(f"Language '{language_code}' not supported. " f"Supported languages: {supported}")
        return language_code

    def convert_audio_to_wav(self, audio_file_path: str) -> Tuple[bytes, float]:
        """
        Convert audio file to WAV format suitable for Speech API

        Args:
            audio_file_path: Path to the audio file

        Returns:
            Tuple of (WAV audio bytes, duration in seconds)
        """
        try:
            logger.info(f"Converting audio file: {audio_file_path}")

            # Load audio file (supports mp3, wav, m4a, flac, ogg, etc.)
            audio = AudioSegment.from_file(audio_file_path)

            # Get duration
            duration_seconds = len(audio) / 1000.0

            # Convert to mono, 16kHz, 16-bit WAV (optimal for Speech API)
            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(16000)
            audio = audio.set_sample_width(2)  # 16-bit

            # Export to bytes
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)

            logger.info(f"Audio converted successfully. Duration: {duration_seconds:.2f}s")
            return wav_io.read(), duration_seconds

        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            raise Exception(f"Error converting audio file: {str(e)}")

    def transcribe_audio(self, audio_content: bytes, language_code: str = "en-US") -> Tuple[str, float]:
        """
        Transcribe audio content to text

        Args:
            audio_content: Audio data in bytes (WAV format)
            language_code: Language code for transcription

        Returns:
            Tuple of (transcribed text, confidence score)
        """
        try:
            logger.info(f"Transcribing audio in {language_code}")

            audio = speech.RecognitionAudio(content=audio_content)

            # Select appropriate model based on language
            # medical_dictation model only supports English
            if language_code.startswith("en"):
                model = "medical_dictation"  # Optimized for medical terminology
                use_enhanced = True
            else:
                model = "default"  # Standard model supports all languages
                use_enhanced = False

            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language_code,
                enable_automatic_punctuation=True,
                model=model,
                use_enhanced=use_enhanced,
            )

            logger.info(f"Using model: {model} for language: {language_code}")

            # Perform transcription
            response = self.speech_client.recognize(config=config, audio=audio)

            # Combine all transcripts and calculate average confidence
            transcript_parts = []
            confidences = []

            for result in response.results:
                if result.alternatives:
                    alt = result.alternatives[0]
                    transcript_parts.append(alt.transcript)
                    confidences.append(alt.confidence)

            transcript = " ".join(transcript_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            logger.info(f"Transcription complete. Confidence: {avg_confidence:.2f}")
            return transcript, avg_confidence

        except google_exceptions.Forbidden as e:
            logger.error(f"Speech API forbidden: {e}")
            raise Exception(
                f"Error transcribing audio: 403 Cloud Speech-to-Text API has not been used in project "
                f"{os.getenv('GCP_PROJECT', 'apcomp215-group88')} before or it is disabled. "
                f"Enable it by visiting https://console.developers.google.com/apis/api/speech.googleapis.com/overview?project="
                f"{os.getenv('GCP_PROJECT', 'apcomp215-group88')} then retry. "
                f"If you enabled this API recently, wait a few minutes for the action to propagate to our systems and retry."
            )
        except Exception as e:
            logger.error(f"Transcription error: {e}")
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
            source_lang = source_language.split("-")[0]

            logger.info(f"Translating from {source_lang} to English")

            result = self.translate_client.translate(text, source_language=source_lang, target_language="en")

            translated_text = result["translatedText"]
            logger.info("Translation complete")

            return translated_text

        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise Exception(f"Error translating text: {str(e)}")

    def transcribe_and_translate(
        self, audio_file_path: str, language_code: str = "en-US", auto_translate: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe audio file and optionally translate to English

        Args:
            audio_file_path: Path to audio file
            language_code: Language of the audio
            auto_translate: Automatically translate non-English to English

        Returns:
            Dictionary with transcription results:
            {
                "transcript": str,
                "original_language": str,
                "was_translated": bool,
                "confidence": float,
                "duration_seconds": float,
                "original_transcript": str (if translated)
            }
        """
        # Validate language
        language_code = self.validate_language(language_code)
        lang_info = SUPPORTED_LANGUAGES[language_code]

        # Convert audio to WAV format
        wav_content, duration = self.convert_audio_to_wav(audio_file_path)

        # Transcribe audio
        transcript, confidence = self.transcribe_audio(wav_content, language_code)

        # Prepare result
        result = {
            "transcript": transcript,
            "original_language": lang_info["name"],
            "original_language_code": language_code,
            "was_translated": False,
            "confidence": confidence,
            "duration_seconds": duration,
        }

        # Translate if needed and requested
        if lang_info["needs_translation"] and auto_translate and transcript:
            logger.info("Non-English transcript detected, translating to English")
            result["original_transcript"] = transcript
            result["transcript"] = self.translate_to_english(transcript, language_code)
            result["was_translated"] = True
            logger.info("Translation complete")

        return result

    def transcribe_file(self, audio_file_path: str, language_code: str = "en-US") -> str:
        """
        Simple transcription without translation (backward compatibility)

        Args:
            audio_file_path: Path to audio file
            language_code: Language code

        Returns:
            Transcribed text
        """
        wav_content, _ = self.convert_audio_to_wav(audio_file_path)
        transcript, _ = self.transcribe_audio(wav_content, language_code)
        return transcript


# Global service instance
audio_service = AudioService()


def transcribe_audio_file(
    audio_file_path: str, language_code: str = "en-US", auto_translate: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to transcribe and translate an audio file

    Args:
        audio_file_path: Path to the audio file
        language_code: Language of the audio
        auto_translate: Automatically translate to English

    Returns:
        Transcription result dictionary
    """
    return audio_service.transcribe_and_translate(audio_file_path, language_code, auto_translate)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Transcribe audio file to text with optional translation")
    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument(
        "--language",
        default="en-US",
        choices=list(SUPPORTED_LANGUAGES.keys()),
        help=f"Language code. Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}",
    )
    parser.add_argument("--no-translate", action="store_true", help="Disable automatic translation to English")

    args = parser.parse_args()

    try:
        print(f"\nTranscribing: {args.audio_file}")
        print(f"Language: {SUPPORTED_LANGUAGES[args.language]['name']}")
        print(f"Auto-translate: {not args.no_translate}\n")

        result = transcribe_audio_file(args.audio_file, args.language, auto_translate=not args.no_translate)

        print("=" * 60)
        print("TRANSCRIPTION RESULT")
        print("=" * 60)

        if result["was_translated"]:
            print(f"\nOriginal ({result['original_language']}):")
            print(result["original_transcript"])
            print(f"\nTranslated (English):")
        else:
            print(f"\nTranscript ({result['original_language']}):")

        print(result["transcript"])
        print(f"\nConfidence: {result['confidence']:.2%}")
        print(f"Duration: {result['duration_seconds']:.2f} seconds")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
