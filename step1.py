import json
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
import torch
from dotenv import load_dotenv
from scipy.io import wavfile
from datasets import load_dataset

from conversational_model import ConversationalModel
from stt import SpeechToText
from voice_generator import create_cloned_voice, speak


def main(verbose: bool, voice: str, dry_run: bool) -> None:
    def debug(*args, **kwargs) -> None:
        if verbose:
            print(*args, **kwargs)

    # Config.
    print("Loading models", end="... ", flush=True)
    questioner = ConversationalModel()
    transcriber = SpeechToText(silence_threshold=0.0015)

    transcriber.plot_noise()

    prompt = ("You are tasked to ask me diverse questions to get to know me. "
              "You might follow up each of my answers to get more details but don't focus too much in a single topic. "
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
            debug("Getting question", end="... ", flush=True)
            question = questioner(prompt)
            debug("Done!")
            print(f"Q: {question}")

            debug("Generating audio", end="... ", flush=True)
            speak("generic", question)
            debug("Done!")

            print("Listening", end="... ", flush=True)
            audio = transcriber.record()
            audios.append(audio[:, 0])
            print("Done!")

            debug("Transcribing", end="... ", flush=True)
            prompt = transcriber.transcribe(audio)
            debug("Done!")

            print("A:", prompt)
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
        wavfile.write(path/"recordings"/f"recording{i + 1}.wav", transcriber.fs, audio)
    print("Done!")

    # Create clone voice.
    speak("generic", "Thank you for the conversation. Now tell me a brief description about you")
    description = transcriber()
    if dry_run:
        print("Not submitting voices, running dry mode!")
    else:
        print("Pushing voice")
        create_cloned_voice(voice, path/"recordings", description)


if __name__ == "__main__":
    load_dotenv()
    parser = ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--voice", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(args.verbose, args.voice, args.dry_run)
