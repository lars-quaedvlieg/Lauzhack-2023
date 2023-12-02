import os
import json
from datetime import datetime
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv
from scipy.io import wavfile
import numpy as np
import sounddevice as sd
from openai import OpenAI
from transformers import WhisperProcessor, WhisperForConditionalGeneration


def record_audio(fs, silence_threshold, max_silence_dur, min_dur):
    buffer = np.array([])  # Buffer to store audio data
    terminated = False
    cv = Condition()

    def callback(indata, frames, time, status):
        nonlocal terminated
        nonlocal buffer

        print(np.mean(np.abs(buffer[-max_silence_dur * 1000:])))
        buffer = np.append(buffer, indata.copy())

        # Detect silence
        if np.mean(np.abs(buffer[-max_silence_dur * 1000:])) < silence_threshold:
            # If silence is detected, check the duration
            if len(buffer) / fs > min_dur:
                with cv:
                    terminated = True
                    cv.notify()

    with sd.InputStream(callback=callback, samplerate=fs, channels=1):
        with cv:
            while not terminated:
                cv.wait()

    return buffer


class ConversationalModel:
    def __init__(self, sys_prompt: Optional[str] = None):
        self.sys_prompt = sys_prompt
        self.messages = []
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def __call__(self, txt: str) -> str:
        self.messages.append({"role": "user", "content": txt})
        msgs = []
        if self.sys_prompt is not None:
            msgs.append({"role": "system", "content": self.sys_prompt})
        msgs += self.messages
        response = self.client.chat.completions.create(model="gpt-3.5-turbo",
                                                       messages=msgs)
        txt = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": txt})
        return txt


def record_audio(fs: int = 16000, silence_threshold: float = 1e-4, max_silence_duration: int = 2,
                 min_duration: int = 3) -> np.ndarray:
    audio = record_audio(fs=fs, silence_threshold=silence_threshold, max_silence_dur=max_silence_duration,
                         min_dur=min_duration)
    return audio


def main():
    # Config.
    print("Loading models", end="... ", flush=True)
    fs = 16000

    processor = WhisperProcessor.from_pretrained("openai/whisper-base")
    transcriber = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base")
    questioner = ConversationalModel()
    prompt = ("You are tasked to ask me many questions to get to know me. "
              "You might follow up each of my answers to get more details. "
              "You may ask only one question at a time. "
              "You should not prepend any question with any meaningless information.")
    audios = []
    questions = []
    print("Done!")

    # Main loop.
    print("Starting Q&A. Ctrl+C when you want to terminate.")
    done = False
    while not done:
        try:
            print("Getting question", end="... ", flush=True)
            question = questioner(prompt)
            print("Done!")

            print(f"> {question}")
            print("Now, start speaking", end="... ", flush=True)
            audio = record_audio(fs)
            audios.append(audio[:, 0])
            print("Done!")

            print("Transcribing", end="... ", flush=True)
            x = processor(audio[:, 0], sampling_rate=fs, return_tensors="pt").input_features
            prompt = processor.batch_decode(transcriber.generate(x), skip_special_tokens=True)[0].strip()
            print("Done!")
            print("Transcription:", prompt)
            print()
            questions.append({"question": question, "answer": prompt})
        except KeyboardInterrupt:
            done = True
            print()
            print("Terminating Q&A")
            print()

    # Save outputs.
    print("Saving outputs", end="... ", flush=True)
    i = 1
    while (path := Path("outs")/f"out{i}").exists():
        i += 1
    path.mkdir()
    now = datetime.now()
    data = {"date": now.isoformat()}
    with open(path/"meta.json", "w+") as f:
        json.dump(data, f, indent=4)
    with open(path/"conversation.json", "w+") as f:
        json.dump(questions, f)
    for i, audio in enumerate(audios):
        (path/"recordings").mkdir(exist_ok=True)
        wavfile.write(path/"recordings"/f"recording{i + 1}.wav", fs, audio)
    print("Done!")



if __name__ == "__main__":
    load_dotenv()
    main()
