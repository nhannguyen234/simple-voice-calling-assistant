import os
from dotenv import load_dotenv

# Reload .env variables
load_dotenv(override=True)

class Settings:
    OPENAI_API_KEY: str = str(os.getenv("OPENAI_API_KEY",""))
    MAX_TOKENS: int = 200
    MAX_RETRIES: int = 3

    AUDIO_OUTPUT_PATH: str = "audio_files"

    ELEVENLABS_API_KEY: str = str(os.getenv("ELEVENLABS_API_KEY",""))
    ELEVENLABS_VOICE_ID: str = "SAz9YHcvj6GT2YYXdXww" # River voice

    HUMAN_PYAUDIO_CHANNELS: int = 1
    HUMAN_PYAUDIO_RATE = 44100
    HUMAN_PYAUDIO_CHUNK = 1024  # ~0.023s of audio
    HUMAN_PYAUDIO_IDLE_TIME_SECONDS = 10
    HUMAN_PYAUDIO_SILENCE_TIME_SECONDS = 1
    HUMAN_PYAUDIO_SILENCE_THRESHOLD = 500  # This is RMS threshold method to detect noise in specific environment

    RINGTONE_FILE_PATH: str = "src/ringtones/ringtone-001.mp3"

settings = Settings()