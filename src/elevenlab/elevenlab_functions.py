from src.core.config import settings
from io import BytesIO
from typing import IO

from pydub import AudioSegment
from elevenlabs.client import AsyncElevenLabs
from elevenlabs import VoiceSettings, play

async_elevenlabs = AsyncElevenLabs(
    api_key=settings.ELEVENLABS_API_KEY
)

async def elevenlabs_speech_to_text(
        audio_file_path: str
):
    with open(audio_file_path, 'rb') as file:
        audio_byte = file.read()
    
    audio_data = BytesIO(audio_byte)
    transcription = await async_elevenlabs.speech_to_text.convert(
        file=audio_data,
        model_id="scribe_v1",
        language_code="eng",
        diarize=True
    )
    return transcription

async def elevenlabs_text_to_speech(
        transcription: str,
        audio_file_saved_path: str
) -> None:
    
    with open(audio_file_saved_path, "wb") as file:    
        async for voice in async_elevenlabs.text_to_speech.convert(
            text=transcription,
            voice_id=settings.ELEVENLABS_VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        ):
            audio_buffer = BytesIO(voice)
            file.write(audio_buffer.getvalue())

async def elevenlabs_data_speech_to_text(
        audio_data: IO[bytes]
):
    chunk = await async_elevenlabs.speech_to_text.convert(
        file=audio_data,
        model_id="scribe_v1",
        language_code="eng",
        diarize=True
    )
    return chunk

async def elevenlabs_text_to_speech_stream(
        transcription: str
):
    """This function is to stream the audio and save data in memory for further use"""
    response = async_elevenlabs.text_to_speech.convert(
            text=transcription,
            voice_id=settings.ELEVENLABS_VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
                speed=1.0,
            )
        )
   
    # process for audio streaming
    audio_stream = BytesIO()
    async for chunk in response:
        if chunk:
            audio_stream.write(chunk)
    audio_stream.seek(0) # reset to the beginning
    play(audio_stream) # play audio
    
    return audio_stream