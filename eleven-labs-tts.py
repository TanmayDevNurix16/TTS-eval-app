
import os
import pandas as pd
import time
import os
import json
import requests

from dotenv import load_dotenv
load_dotenv()
import csv
def generate_speech(api_key, text, language, output_file):
    """
    Generate speech using ElevenLabs API for a given language.

    :param api_key: ElevenLabs API key
    :param text: Text to convert to speech
    :param language: Language for the speech
    :param output_file: Output audio file path
    :return: Dictionary with audio details and performance metrics
    """
    start_time = time.time()

    base_url = "https://api.elevenlabs.io/v1"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    # Fetch voices list
    response = requests.get(f"{base_url}/voices", headers=headers)
    voices = response.json().get('voices', [])
    # with open("voices.json", "w") as f:
    #     json.dump(voices, f)
    # print(voices)
    # Find a voice matching the specified language
    selected_voice = None
    if language.lower() == "english":
        # Select the first available English voice
        selected_voice = voices[0]["voice_id"] if voices else None
    else:
        # Try to match language in voice name
        for voice in voices:
            if language.lower() in voice.get("name", "").lower():
                selected_voice = voice["voice_id"]
                break
    # selected_voice = "90ipbRoKi4CpHXvKVtl0"    
    selected_voice = "mfMM3ijQgz8QtMeKifko"            
    if not selected_voice:
        return {"status": "error", "message": f"No voice found for language: {language}"}

    # Prepare the payload
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    # Make API request
    tts_response = requests.post(
        f"{base_url}/text-to-speech/{selected_voice}",
        json=payload,
        headers=headers
    )

    if tts_response.status_code != 200:
        return {"status": "error", "message": "Failed to generate speech"}

    # Save the audio file
    with open(output_file, "wb") as f:
        f.write(tts_response.content)

    total_time = time.time() - start_time
    file_size = os.path.getsize(output_file)

    return {
        "status": "success",
        "output_file": output_file,
        "voice_id": selected_voice,
        "text_length": len(text),
        "audio_file_size": file_size,
        "generation_time": total_time
    }

if __name__ == "__main__":
    print(generate_speech( os.getenv("ELEVENLABS_API_KEY"),"I will meet you कल शाम को at the cafe.","Hindi", "output.mp3"))