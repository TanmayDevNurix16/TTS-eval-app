
from google.cloud import texttospeech
import os
import pandas as pd
import time
import csv

def synthesize_speech(text, output_filename, credentials_path):
    """Synthesizes speech from the input string of text and returns the time taken."""
    # Start timing
    start_time = time.time()
    
    # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    
    # Initialize the client
    client = texttospeech.TextToSpeechClient()
    
    # Set the text input to be synthesized
    input_text = texttospeech.SynthesisInput(text=text)
    
    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-IN",
        name="en-IN-Neural2-D", #Or another voice from the list
    )
    
    # Select the type of audio file to return
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    # Perform the text-to-speech request
    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )
    
    # The response's audio_content is binary
    with open(output_filename, "wb") as out:
        out.write(response.audio_content)
        
    # Calculate time taken
    end_time = time.time()
    time_taken = end_time - start_time
    
    print(f'Audio content written to file "{output_filename}"')
    print(f'Time taken to generate audio: {time_taken:.2f} seconds')
    
    return time_taken

synthesize_speech("Hello, how are you?","output.mp3","/Users/admin/Documents/tts-eval/google-creds.json")