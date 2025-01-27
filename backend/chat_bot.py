"""
Chat Bot Functions
"""
import os
from typing import List
import openai
from translate import Translator
import anthropic
from dotenv import load_dotenv

load_dotenv()
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")


def anthropic_response_generator(active_messages: List, api_key: str, model: str):
    """
    Replies to the prompt using Anthropic's claude 3.5 sonnet engine.
    """
    client = anthropic.Anthropic(api_key=api_key)

    if not active_messages:
        raise ValueError("Please provide a prompt.")

    try:
        response = client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=1,
            system=SYSTEM_PROMPT,
            messages=active_messages,
            stream=True
        )
        print(response)
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e

def openai_response_generator(active_messages: List, api_key: str, model: str):
    """
    Replies to the prompt using OpenAI's GPT-3 engine.
    """
    try:
        # Initialize OpenAI API
        openai.api_key = api_key
        if not active_messages:
            raise ValueError("Please provide a prompt.")

        # Generate response
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system",
                 "content": SYSTEM_PROMPT},
                *active_messages,
            ],
            stream=True
        )
        for chunk in response:
            chunk_message = chunk.choices[0].delta.content
            if chunk_message:
                yield chunk_message
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e

def translation_generator(message: str):
    """
    Translates a message from Swahili to English.
    """
    translator = Translator(from_lang="sw", to_lang="en")
    translation = translator.translate(message)
    return translation

def openai_transcribe_audio(audio_file, api_key: str):
    """
    Transcribes an audio file to text.
    """
    openai.api_key = api_key
    transcription = openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
        )
    return transcription.text
