from threading import Condition

import numpy as np
import sounddevice as sd
from matplotlib import pyplot as plt
from transformers import WhisperProcessor, WhisperForConditionalGeneration


class SpeechToText:
    def __init__(self, fs: int = 16000, silence_threshold: float = 0.01,
                 max_silence_dur: int = 2, min_dur: int = 3):
        self.fs = fs
        self.silence_threshold = silence_threshold
        self.max_silence_dur = max_silence_dur
        self.min_dur = min_dur

        self.processor = WhisperProcessor.from_pretrained("openai/whisper-base")
        self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base")

    def plot_noise(self, dur: int = 5) -> None:
        print('Generating noise information')
        buffer = np.array([])  # Buffer to store audio data
        mean_noises = np.array([])
        def callback(indata, frames, time, status):
            nonlocal buffer
            nonlocal mean_noises

            buffer = np.append(buffer, indata.copy())

            mean_noise = np.mean(np.abs(buffer[-self.max_silence_dur * 1000:]))
            mean_noises = np.append(mean_noises, mean_noise.copy())

        with sd.InputStream(callback=callback, samplerate=self.fs, channels=1):
            sd.sleep(dur*1000)

        plt.plot(mean_noises)
        plt.show()

        print(f'Mean noise: {np.mean(mean_noises)}')

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
            if np.mean(np.abs(buffer[-self.max_silence_dur * 1000:])) < self.silence_threshold:
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
                           return_tensors="pt").input_features
        return self.processor.batch_decode(self.model.generate(x),
                                           skip_special_tokens=True)[0].strip()

    def __call__(self) -> str:
        return self.transcribe(self.record())
