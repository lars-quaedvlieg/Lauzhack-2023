from dotenv import load_dotenv
load_dotenv()
import os
from elevenlabs import set_api_key
set_api_key(os.getenv("ELEVENLABS_API_KEY"))

from elevenlabs import clone, generate, play, voices, Voice, VoiceSettings


class Voice():

    def __init__(self):

        self.voice = None

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


class ClonedVoice(Voice):

    def __init__(self, name):

        super().__init__()
        self.name = name
        self.voice = self._get_voice_if_exists()

    def _get_voice_if_exists(self):

        cloned_voices = [v for v in voices() if v.category=='cloned' and v.name==self.name]
        if not cloned_voices:
            print('No existing cloned voice with this name found.')
            return None
        print('An existing cloned voice with this name was found. No need to re-clone.')
        return cloned_voices[0]

    def clone_voice(self, files, description=''):

        assert self.voice is None, "Cloned voice already exists. Re-cloning not allowed."
        self.voice = clone(
            name=self.name,
            description=description,
            files=files,
        )


class GenericVoice(Voice):

    def __init__(self, age_group=None, gender=None):

        super().__init__()
        self.age_group = age_group
        self.gender = gender
        self.voice = self._get_voice()


    def _get_voice(self):

        if self.age_group is not None and self.gender is not None:
            profile_voices = [v for v in voices() if 'age' in v.labels and (v.labels['age'] == self.age_group and v.labels['gender'] == self.gender)]
            if profile_voices:
                return profile_voices[0]

        # default to voice 'Charlie' if no suitable voice for specific profile
        return [v for v in voices() if v.name=='Charlie'][0]


def speak(name: str, text: str) -> None:
    if name == "generic":
        voice = GenericVoice()
    else:
        voice = ClonedVoice(name)
    voice.play_audio(text)


def create_cloned_voice(name, audio_dir, description=''):
    new_voice = ClonedVoice(name)
    new_voice.clone_voice([os.path.join(audio_dir, f) for f in os.listdir(audio_dir)], description)
    return new_voice
