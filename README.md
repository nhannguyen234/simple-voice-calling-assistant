# Project Overview
This is the simple project for virtual assistant developed from scratch using OpenAI for text conversation and ElevenLabs for TTS and STT.
# Prerequisites: 
python>=3.11
# Instruction and Information:
- Install `ffmpeg` for decoding mp3 file data to raw data - this is mandatory
  - Windows: follow the instruction [Window Installation](https://www.geeksforgeeks.org/installation-guide/how-to-install-ffmpeg-on-windows/)
  - MacOS: `brew install ffmpeg`
  - Ubuntu/Linux: `sudo apt install ffmpeg`
- Install `portaudio` for pyaudio
  - Windows: `python -m pip install pyaudio` -> no need to install portaudio
  - MacOS: `brew install portaudio`
  - Ubuntu/Linux: `sudo apt install python3-pyaudio`
- Install dependencies packages by using `pip install -r requirements.txt`
- Create a file `.env` and update your OPENAI API KEY in `.env` with variable `OPENAI_API_KEY = "your-key"` and `ELEVENLABS_API_KEY = "your-key"`
- Run `python main_test.py` for test script

# Limitation:
- Not yet handle latency for TTS and STT 
- Not yet implement websocket for webcall
- Not yet implement real phone call
