from dotenv import load_dotenv
load_dotenv()
import os
from elevenlabs import set_api_key
set_api_key(os.getenv("ELEVENLABS_API_KEY"))

from elevenlabs import clone, generate, play

class ClonedVoice():

    def __init__(self, name, descrption):

        self.name = name
        self.description = description
        self.voice = None

    def clone_voice(self, files):

        self.voice = clone(
            name=self.name,
            description=self.description,
            files=files,
        )

    def generate_audio(self, text, play_audio=True):

        assert
        audio = generate(text=text, voice=self.voice)
        if play_audio:
            play(audio)
        return audio
