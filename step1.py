import os
from typing import Optional

import numpy as np
import sounddevice as sd
from openai import OpenAI
from transformers import WhisperProcessor, WhisperForConditionalGeneration


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


def record_audio(fs: int = 16000) -> np.ndarray:
    audio = sd.rec(int(5*fs), samplerate=fs, channels=1)
    sd.wait()
    return audio


def main():
    # Config.
    fs = 16000
    duration = 5
    processor = WhisperProcessor.from_pretrained("openai/whisper-base")
    transcriber = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base")
    questioner = ConversationalModel()
    prompt = ("You are tasked to ask me many questions to get to know me. "
              "You might follow up each of my answers to get more details. "
              "You may ask only one question at a time. "
              "You should not prepend any question with any meaningless information.")

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
            print("Done!")

            print("Transcribing", end="... ", flush=True)
            x = processor(audio[:, 0], sampling_rate=fs, return_tensors="pt").input_features
            prompt = processor.batch_decode(transcriber.generate(x), skip_special_tokens=True)[0].strip()
            print("Done!")
            print("Transcription:", prompt)
            print()
        except KeyboardInterrupt:
            done = True
            print()
            print("Terminating Q&A")


if __name__ == "__main__":
    main()
