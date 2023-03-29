import pyaudio
import numpy as np
import openai
import wave
import os
import bpy

def get_api_key():
    preferences = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences
    return preferences.api_key

def get_audio_path():
    preferences = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences
    return preferences.audio_path

def transcribe_audio():
    openai.api_key = get_api_key()
    audio_file = get_audio_path()
    RATE = 16000
    CHUNK = int(RATE / 10)  # 100ms chunks
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    WAVE_OUTPUT_FILENAME = audio_file

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Start speaking...")

    frames = []
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        # Stop recording if silence is detected or after a certain number of frames
        if len(frames) > 50 and np.mean(np.abs(np.frombuffer(b''.join(frames[-50:]), dtype=np.int16))) < 300:
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the audio data to a WAV file
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # Call the Whisper API using the correct method
    with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

    # Remove the local WAV file after transcription
    os.remove(WAVE_OUTPUT_FILENAME)

    return transcript["text"]