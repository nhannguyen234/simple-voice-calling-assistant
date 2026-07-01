import os
import pyaudio
import wave
import audioop
import time
import threading
from uuid import uuid4
from io import BytesIO
from collections import defaultdict
from pydub import AudioSegment
from langchain_core.messages import HumanMessage

from src.utils.helper_functions import play_ringtone, write_audio_to_wav
from src.ai_agents.text_workflows import assistant_bot
from src.elevenlab.elevenlab_functions import (
    elevenlabs_text_to_speech_stream,
    elevenlabs_data_speech_to_text
)
from src.core.logger import logger
from src.core.config import settings
from src.utils.utils import handle_errors

state = defaultdict(dict)
human_voice_data_frames = defaultdict(list)
stop_flag = False

def listen_for_stop():
    global stop_flag
    while True:
        user_input = input("Type 'stop' when you want to stop immediately: ")
        if user_input.lower() == "stop":
            stop_flag = True
            print("Stop detected!")

threading.Thread(target=listen_for_stop, daemon=True).start()

@handle_errors()
async def voice_box_processing(
        call_id: str,
        human_voice_data: bytes
):
    """This function is to return assistant voice audio file with wav format"""
    transcription = await elevenlabs_data_speech_to_text(audio_data=human_voice_data)
    logger.info(f"Human transcripts: {transcription}")
    # Get the whole message to text workflows
    human_text_message = transcription.text
    # Process text messages
    config = {
        "configurable": {"thread_id": call_id}
    }
    assistant_text_response = await assistant_bot.ainvoke(
        {
            "thread_id": call_id,
            "messages": [HumanMessage(content=human_text_message)]
        },
        config=config
    )
    logger.info("Finish processing text")
    # Process text to speech
    assistant_voice_data = await elevenlabs_text_to_speech_stream(
        transcription=assistant_text_response["messages"][-1].content
    )
    logger.info("Finish processing text to speech")
    return assistant_voice_data

@handle_errors()
async def local_voice_call(
    call_id: str = str(uuid4()),
    first_message: str = "Thank you for calling Jacobs Plumbing. How can I assist you today?",
    has_ringtone: bool = True,
    audio_saved_folder: str = settings.AUDIO_OUTPUT_PATH,
    chunk = settings.HUMAN_PYAUDIO_CHUNK,
    rate = settings.HUMAN_PYAUDIO_RATE,
    silence_threshold = settings.HUMAN_PYAUDIO_SILENCE_THRESHOLD,
    silence_time_seconds = settings.HUMAN_PYAUDIO_SILENCE_TIME_SECONDS,
    idle_time_seconds = settings.HUMAN_PYAUDIO_IDLE_TIME_SECONDS,
    channels = settings.HUMAN_PYAUDIO_CHANNELS,
):
    """This function is to test voice call locally"""
    # Ringtone in 5 seconds
    global human_voice_data_frames, state
    conversation_pcm = b'\x00' * chunk
    
    if has_ringtone:
        logger.info("Calling...")
        start_time = time.time()
        while time.time() - start_time < 2:
            play_ringtone()
    
    format = pyaudio.paInt16
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=format, 
        channels=channels,
        rate=rate, 
        input=True,
        frames_per_buffer=chunk)
    
    if first_message != '':
        first_message_stream = await elevenlabs_text_to_speech_stream(
            transcription=first_message
        )
        # process mp3 to wav
        first_message_stream.seek(0) # this is mandatory before decoding mp3
        first_message_audio_segment = AudioSegment.from_mp3(first_message_stream)
        first_message_audio_segment = first_message_audio_segment.set_channels(channels)\
                                                                 .set_frame_rate(rate)\
                                                                 .set_sample_width(audio.get_sample_size(format))
        conversation_pcm += first_message_audio_segment.raw_data

    silent_chunks = 0
    
    while True:
        # Start talking
        human_voice_data = stream.read(chunk, exception_on_overflow=False)
        human_voice_data_frames[call_id].append(human_voice_data)
        # Check for noise detection with silence_threshold
        rms = audioop.rms(human_voice_data, 2)  # 2 bytes per sample
        if rms < silence_threshold:
            silent_chunks += 1
        else:
            state[call_id]["role"] = "human" # to flag for the last state is human or ai   
            silent_chunks = 0  # Reset if human speaks
        
        # Process assistant response
        if silent_chunks * chunk / rate >= silence_time_seconds and state[call_id].get("role") == 'human':
            human_pcm = write_audio_to_wav(bytes_data_list=human_voice_data_frames[call_id])
            print(1)
            conversation_pcm+=human_pcm.getvalue()
            # Assign the state flag
            state[call_id]["role"] = "ai"
            assistant_voice_stream = await voice_box_processing(
                call_id=call_id,
                human_voice_data=human_pcm
            )
            # process mp3 to wav
            assistant_voice_stream.seek(0) # this is mandatory before decoding mp3
            assistant_voice_segment = AudioSegment.from_mp3(assistant_voice_stream)
            assistant_voice_segment = assistant_voice_segment.set_channels(channels)\
                                                            .set_frame_rate(rate)\
                                                            .set_sample_width(audio.get_sample_size(format))
            conversation_pcm += assistant_voice_segment.raw_data
            # reset human_voice_data_frames and silent chunks
            human_voice_data_frames[call_id] = []
            silent_chunks = 0
            logger.info("Process assistant response finished")

        if stop_flag:
            logger.info("The call has been stopped")
            break
        # Check if we've been silent long enough
        if silent_chunks * chunk / rate >= idle_time_seconds and state[call_id].get("role")=='ai':
            logger.warning("Silence detected. Stopping recording.")
            break
    
    logger.info("Finish conversation")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the record to WAV
    saved_folder = os.path.join(audio_saved_folder,call_id)
    if not os.path.exists(saved_folder):
        os.mkdir(saved_folder)

    wf = wave.open(os.path.join(saved_folder,f"conversation.wav"), 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(conversation_pcm)
    wf.close()