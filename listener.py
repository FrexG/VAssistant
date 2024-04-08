import os
import ffmpy
import pyttsx3
import asyncio
import wave
import pyaudio
import numpy as np
import multiprocessing
from pydub import AudioSegment
from gtts import gTTS
from PyQt5.QtCore import QObject, pyqtSignal
import speech_recognition as sr
from googletrans import Translator
from colorama import init, Fore, Style

from gemini import Gemini
from asr import Transcribe

# colorama
init(autoreset=True)


class TTS(QObject):
    process_complete = pyqtSignal()

    def __init__(self, text) -> None:
        super().__init__()
        self.text = text
        self.engine = pyttsx3.Engine()

    def run(self):
        self.tts_google()

    def tts_pyttsx3(self):
        try:
            # self.engine.say(self.text)
            self.engine.save_to_file(self.text, "temp.wav")
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error on TTS: {e}")
        finally:
            self.process_complete.emit()

    def tts_google(self):
        print("TTS Called ... ")
        try:
            tts = gTTS(text=self.text)
            tts.save("response.wav")
        except Exception as e:
            print(f"Error TTS: {e}")
        audio_duration = AudioSegment.from_file("response.wav").duration_seconds
        if os.path.exists("response.wav"):
            self.merge_video_audio(
                "./vids/extended_vid.mp4", "response.wav", "output.mp4", audio_duration
            )
            print("Done merger")
            self.process_complete.emit()
        # os.system("ffplay response.mp3")
        return

    def merge_video_audio(self, video_input, audio_input, output_file, duration):
        options = ["-map", "0:v", "-map", "1:a", "-c:v", "copy", "-shortest", "-y"]
        ff = ffmpy.FFmpeg(
            inputs={video_input: None, audio_input: None},
            outputs={output_file: options},
        )
        ff.run()
        return


class AudioListener:
    def __init__(self, lang="amh"):
        self.lang = lang
        self.listener = sr.Recognizer()
        # self.transcriber = Transcribe(lang=lang)
        # self.translator = Translator()
        self.talk = True
        self.listen = True

    def listen_prompt(self):
        instruction = ""
        try:
            with sr.Microphone() as src:
                print("LISTENING ...")
                self.speech = self.listener.listen(src)
                print("Instruction received ...")
                instruction += self.listener.recognize_google(self.speech)
                instruction = instruction.lower()
        except Exception as e:
            print(f"Exception occured: ", e)
            exit(1)

        print(Fore.BLUE + f"You:>")
        print(instruction)

        return instruction

    def mms_transcribe_prompt(self):
        src_sample_rate = self.speech.sample_rate
        audio_data = self.speech.get_wav_data()
        data_s16 = np.frombuffer(audio_data, dtype=np.float32, offset=0)

        with wave.open("temp.wav", "w") as record:
            record.setnchannels(1)
            record.setsampwidth(self.speech.sample_width)
            record.setframerate(self.speech.sample_rate)
            record.writeframes(self.speech.frame_data)

        recored_audio = AudioSegment.from_file("temp.wav")

        print(f"{recored_audio.frame_rate=}")
        print(f"{recored_audio.channels=}")

        waveform = recored_audio.get_array_of_samples()

        src_sample_rate = recored_audio.frame_rate
        transcription = self.transcriber(waveform, src_sample_rate)

        if transcription:
            translation = self.translator.translate(transcription, dest="en")

        print(Fore.BLUE + "You:")
        print(translation)
        return translation

    async def record_audio(
        self,
        chunk=1024,
        format=pyaudio.paInt16,
        channel=1,
        rate=16_000,
        record_seconds=5,
    ):
        """
        Records audio from the microphone and return numpy array
        Args:
            chunk: size of audio data to read per chunk
            format: audio format
            channels: number of audio channels (mono)
            rate: sampling rate (defualts to mms)
            record_seconds: duration of recording in seconds
        """
        p = pyaudio.PyAudio()
        # Open audio stream for recording
        stream = p.open(
            format=format,
            channels=channel,
            rate=rate,
            input=True,
            frames_per_buffer=chunk,
        )
        frames = []
        print("Listening ... ")
        for _ in range(0, int(rate / chunk * record_seconds)):
            data = stream.read(chunk)
            frames.append(data)

        # stop and close the stream
        stream.stop_stream()
        stream.close()
        # close pyaudio
        p.terminate()
        # Combine the recorded chunks into a single byte array
        audio_data = b"".join(frames)
        audio_array = np.frombuffer(audio_data, dtype=np.float32)

        print(f"{audio_array=}")

        transcription = self.transcriber(audio_array, rate)

        print(f"{transcription=}")

        # return audio_array
