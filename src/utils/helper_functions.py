import pyaudio
import wave
import audioop
import time
import os

from uuid import uuid4
from pydub import AudioSegment
from io import BytesIO
from src.core.config import settings
from src.core.logger import logger

def write_audio_to_wav(
        bytes_data_list: list[bytes],
        rate = settings.HUMAN_PYAUDIO_RATE,
        channels = settings.HUMAN_PYAUDIO_CHANNELS,
):
    format = pyaudio.paInt16
    audio = pyaudio.PyAudio()
    wav_buffer = BytesIO()
    wf = wave.open(wav_buffer, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(bytes_data_list))
    wf.close()
    return wav_buffer

def audio_record_saving(
        call_id: str = str(uuid4()),
        role: str = "human",
        audio_saved_folder: str = settings.AUDIO_OUTPUT_PATH,
        chunk = settings.HUMAN_PYAUDIO_CHUNK,
        rate = settings.HUMAN_PYAUDIO_RATE,
        silence_threshold = settings.HUMAN_PYAUDIO_SILENCE_THRESHOLD,
        idle_time_seconds = settings.HUMAN_PYAUDIO_IDLE_TIME_SECONDS,
        channels = settings.HUMAN_PYAUDIO_CHANNELS
):
    """This function use pyaudio to record voice from local machine"""
    format = pyaudio.paInt16
    
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=format, 
        channels=channels,
        rate=rate, 
        input=True,
        frames_per_buffer=chunk)

    logger.info("Recording... Human speaks into the mic.")
    frames = []
    silent_chunks = 0

    while True:
        data = stream.read(chunk)
        frames.append(data)

        # Check for noise detection with silence_threshold
        rms = audioop.rms(data, 2)  # 2 bytes per sample
        if rms < silence_threshold:
            silent_chunks += 1
        else:
            silent_chunks = 0  # Reset if noise detected

        # Check if we've been silent long enough
        if silent_chunks * chunk / rate >= idle_time_seconds:
            logger.warning("Silence detected. Stopping recording.")
            break

    logger.info("Finished human speaking")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save to WAV
    saved_folder = os.path.join(audio_saved_folder,call_id)
    if not os.path.exists(saved_folder):
        os.mkdir(saved_folder)

    wf = wave.open(os.path.join(saved_folder,f"{role}.wav"), 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

def play_ringtone(file_path: str = settings.RINGTONE_FILE_PATH):
    """This function only support mp3 files"""
    sound = AudioSegment.from_mp3(file_path)
    raw_data = sound.raw_data

    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=audio.get_format_from_width(sound.sample_width),
        channels=sound.channels,
        rate=sound.frame_rate,
        output=True
    )

    # Play raw audio
    stream.write(raw_data)

    # Cleanup
    stream.stop_stream()
    stream.close()
    audio.terminate()
