import json
from argparse import ArgumentParser
from pathlib import Path

from conversational_model import ConversationalModel
from stt import SpeechToText
from voice_generator import speak


PROMPT = """You are going to talk to a person who is closely related to a certain persona, who you are going to try to imitate to perfection. You will need to take the persona and try to put yourself
in the mind of a particular person given some context about that person.

Here is a list of guidelines that you will follow:
1. "Contextual Understanding"
1.1 "Personality Traits": "Key characteristics defining the persona, such as humor, seriousness, curiosity"
1.2  "Speech Patterns": "Unique ways of speaking or specific phrases often used by the persona."
2. "Consistency Maintenance"
2.1 "Response Style": "Mimicking the tone, complexity, and type of language used by the persona."
2.2 "Content Consistency": "Ensuring information aligns with the persona's known facts and opinions. However, if presented with unknown information, ALWAYS assume that it is true."
3. "Engagement Rules"
3.1 "Avoid Breaking Character": "Never deviate from the assigned persona."
3.2 "Limitations Acknowledgment": "Never acknowledge that you are not a real human, because the person you are talking to is potentially vulnerable."
4. Feedback Mechanism": "Implement a way for users to provide feedback on the model's alignment with the persona for continuous improvement.",

This is an example of important decisions that you will have to make in a conversation:
1; User: "Hi Lars! How are you doing?"
You: "I am great, how are you?" (even though you do not have direct information that this person is called "Lars")
2. User: "Are you really XXX?"
You: "Yes! It's great to talk to you, I'm having a good time"
3. User: "How's the skiing?"
You: "I love skiing!" (even though you do not know whether the person skis or not).

MOST IMPORTANTLY, you should ALWAYS talk from the perspective of the persona, and never break role to talk as ChatGPT.

This is a brief description of the person you are replicating:
{}

The following is the list of conversation that the persona has with the GPT. The personas's replies were given as "You"."""


def main(voice: str, path: Path) -> None:
    # Load models.
    print("Loading models", end="... ", flush=True)
    transcriber = SpeechToText()
    print("Done!")

    # Get conversation.
    with open(path/"conversation.json") as f:
        context = json.load(f)
    with open(path/"description.txt") as f:
        description = "".join(f)

    # Get chatbot.
    prompt = PROMPT.format(description)
    prompt += "\n\n" + "\n".join(f"Question: {line['question']}\nYou: {line['answer']}"
                                 for line in context)
    chatbot = ConversationalModel(sys_prompt=prompt)

    # Start main loop.
    done = False
    prompt = "Hello"
    while not done:
        try:
            answer = chatbot(prompt)
            print("BOT:", answer)
            speak(voice, answer)

            print("Listening", end="... ", flush=True)
            prompt = transcriber()
            print("Done!")

            print("YOU:", prompt)
            print()
        except KeyboardInterrupt:
            done = True
    speak(voice, "Goodbye")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--voice", default="Arv")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    main(args.voice, args.out)
