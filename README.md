![logo](logo.png)

## Inspiration

Legacy LM aims to provide a unique solution to address the universal need to preserve personal connections and comfort loved ones during bereavement.

## What it does

Legacy LM enables users to create personalised AI models through conversational data input, capturing their speaking style, typical expressions, and voice nuances. These models can simulate casual chats, serving as a comforting presence for loved ones after the user's passing.

## How we built it

The tool works in 2 stages:
First, building a persona by having a conversation/answering questions (GPT to generate questions, text-to-speech to ask questions, speech-to-text to register responses). The audio + content is then used to personalise a GPT
Second, having a casual chat with the generated persona (speech-to-text to register the user’s conversation, GPT with persona to generate response, text-to-speech to give responses with the mimicked voice)

## Challenges we ran into

Figuring out API calls
Working out how to have a fluent conversation with the chatbot (e.g. how long to wait to respond etc.)
Slow model generation since we need real-time conversations

## What we learned

Require high-quality recordings to have good voice-mimicking
Many models are inherently biased (e.g. text-to-speech models were quite good overall but added a slight American accent to most voices)

## Accomplishments that we're proud of

Implementing a working end-to-end prototype that
 performs quite well considering the time we had
Empowering users to leave behind a digital legacy, aiding in the bereavement process for their loved ones.

## What's next for Legacy LM

Refining the voice mimicry and persona adoption
Building it out into a user-friendly tool
Improving conversation latency to sound more fluent
Expand into other use cases of personalised GPTs (e.g. personal memoirs)

## Built With

Python, Hugging Face, OpenAI, ElevenLabs
