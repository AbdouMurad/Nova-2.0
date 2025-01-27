import pyaudio
import keyboard
import time
import wave


import os
import pygame

#text to speech
from dotenv import load_dotenv
import io
from google.cloud import texttospeech
###

class AudioDevice:
    def __init__(self):
        load_dotenv()
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
        self.client = texttospeech.TextToSpeechClient()
        self.voice = texttospeech.VoiceSelectionParams(
            language_code = "en-US",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        self.audio_config = texttospeech.AudioConfig(audio_encoding = texttospeech.AudioEncoding.MP3)
        pygame.init()
        pygame.mixer.init()
    def Speak(self,text):
        text_input = texttospeech.SynthesisInput(text =text)
        response = self.client.synthesize_speech(
            input = text_input, voice = self.voice, audio_config=self.audio_config
        )
        audio_stream = io.BytesIO(response.audio_content)
        audio_stream.seek(0)  # Reset the stream to the beginning
            # Load the audio with pygame and play it
        pygame.mixer.music.load(audio_stream, "mp3")
        pygame.mixer.music.play()

        # Wait until the audio has finished playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def Record(self):
        chunk = 1024
        format = pyaudio.paInt16
        channels = 2
        rate = 44100
        Output_Filename = "UserAudio.wav"
        
        p = pyaudio.PyAudio() 

        stream = p.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

        frames = []
        print("Press SPACE to start recording")
        keyboard.wait('space')
        print("Recording... Press SPACE to stop.")
        time.sleep(0.2)

        while True:
            try:
                data = stream.read(chunk)  
                frames.append(data)
            except KeyboardInterrupt:
                break
            if keyboard.is_pressed('space'):
                print("stopping recording") 
                time.sleep(0.2)
                break   

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(Output_Filename, 'wb')  
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()