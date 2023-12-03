from threading import Condition

import numpy as np
import sounddevice as sd
import torch
from matplotlib import pyplot as plt
from transformers import WhisperProcessor, WhisperForConditionalGeneration


class SpeechToText:
    def __init__(self, size: str = "small", fs: int = 16000,
                 silence_threshold: float = 0.01, max_silence_dur: int = 2, min_dur: int = 3):
        self.fs = fs
        self.silence_threshold = silence_threshold
        self.max_silence_dur = max_silence_dur
        self.min_dur = min_dur

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
        self.processor = WhisperProcessor.from_pretrained(f"openai/whisper-{size}")
        self.model = WhisperForConditionalGeneration.from_pretrained(f"openai/whisper-{size}").to(dtype=self.dtype, device=self.device)

    def plot_noise(self, dur: int = 5) -> None:
        print('Generating noise information')
        buffer = np.array([])  # Buffer to store audio data
        max_noises = np.array([])
        def callback(indata, frames, time, status):
            nonlocal buffer
            nonlocal max_noises

            buffer = np.append(buffer, indata.copy())

            max_noise = np.max(np.abs(buffer[-self.max_silence_dur * 1000:]))
            max_noises = np.append(max_noises, max_noise.copy())

        with sd.InputStream(callback=callback, samplerate=self.fs, channels=1):
            sd.sleep(dur*1000)

        plt.plot(max_noises)
        plt.show()

        print(f'Max noise: {np.mean(max_noises)}')

    def record(self) -> np.ndarray:
        buffer = np.array([])  # Buffer to store audio data
        terminated = False
        cv = Condition()

        def callback(indata, frames, time, status):
            nonlocal terminated
            nonlocal buffer

            # print(np.mean(np.abs(buffer[-max_silence_dur * 1000:])))
            buffer = np.append(buffer, indata.copy())

            # Detect silence
            maxmimum_noise = np.max(np.abs(buffer[-self.max_silence_dur * 1000:]))
            if maxmimum_noise < self.silence_threshold:
                # If silence is detected, check the duration
                if len(buffer) / self.fs > self.min_dur:
                    with cv:
                        terminated = True
                        cv.notify()

        with sd.InputStream(callback=callback, samplerate=self.fs, channels=1):
            with cv:
                while not terminated:
                    cv.wait()

        return buffer[:, None]

    def transcribe(self, audio: np.ndarray) -> str:
        x = self.processor(audio[:, 0], sampling_rate=self.fs,
                           return_tensors="pt").input_features.to(dtype=self.dtype, device=self.device)
        return self.processor.batch_decode(self.model.generate(x),
                                           skip_special_tokens=True)[0].strip()

    def __call__(self) -> str:
        return self.transcribe(self.record())
