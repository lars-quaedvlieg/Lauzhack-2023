from dotenv import load_dotenv
load_dotenv()
import os
from elevenlabs import set_api_key
set_api_key(os.getenv("ELEVENLABS_API_KEY"))

from elevenlabs import clone, generate, play, voices, Voice, VoiceSettings

class ClonedVoice():

    def __init__(self, name):

        self.name = name
        self.voice = self._get_voice_if_exists()

    def _get_voice_if_exists(self):

        cloned_voices = [v for v in voices() if v.category=='cloned' and v.name==self.name]
        if not cloned_voices:
            print('No existing cloned voice with this name found.')
            return None
        print('An existing cloned voice with this name was found. No need to re-clone.')
        return cloned_voices[0]

    def clone_voice(self, files, description):

        assert self.voice is None, "Cloned voice already exists. Re-cloning not allowed."
        self.voice = clone(
            name=self.name,
            description=description,
            files=files,
        )

    def play_audio(self, text, settings_config = None):
        '''
        Generates audio from text using the cloned voice.
        :param text: text to be converted to audio
        :param play_audio: if True, plays the audio
        :param settings_config: Dictionary with keys: stability, similarity_boost, style, use_speaker_boost        
        '''

        assert self.voice is not None, "Voice not yet cloned"

        if settings_config is None:
            voice = self.voice
        else:
            voice = Voice(
                voice_id=self.voice.voice_id,
                settings=VoiceSettings(**settings_config)
            )
        audio = generate(text=text, voice=voice)

        play(audio)
