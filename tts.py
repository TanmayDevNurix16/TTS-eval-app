import os
import time
from dotenv import load_dotenv
from google.cloud import texttospeech
import boto3
import requests
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import argparse

# Load environment variables
load_dotenv()

def create_directory_structure(base_dir="audios"):
    """Create the directory structure for audio outputs"""
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return base_dir

def create_audio_subdirectory(base_dir, index):
    """Create a subdirectory for each line's audio files"""
    subdir = os.path.join(base_dir, f"audios_{index}")
    if not os.path.exists(subdir):
        os.makedirs(subdir)
    return subdir

def generate_elevenlabs_audio(text, output_file):
    """Generate audio using ElevenLabs"""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    base_url = "https://api.elevenlabs.io/v1"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    selected_voice = "mfMM3ijQgz8QtMeKifko"  # Using a predefined voice ID

    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        tts_response = requests.post(
            f"{base_url}/text-to-speech/{selected_voice}",
            json=payload,
            headers=headers
        )

        if tts_response.status_code == 200:
            with open(output_file, "wb") as f:
                f.write(tts_response.content)
            return True
    except Exception as e:
        print(f"ElevenLabs TTS error: {str(e)}")
    return False

def generate_google_audio(text, output_file):
    """Generate audio using Google Cloud TTS"""
    try:
        credentials_path = os.path.join(os.getcwd(), "google-creds.json")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        client = texttospeech.TextToSpeechClient()
        input_text = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-IN",
            name="en-IN-Neural2-D",
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = client.synthesize_speech(
            request={"input": input_text, "voice": voice, "audio_config": audio_config}
        )
        
        with open(output_file, "wb") as out:
            out.write(response.audio_content)
        return True
    except Exception as e:
        print(f"Google TTS error: {str(e)}")
        return False

def generate_aws_audio(text, output_file):
    """Generate audio using AWS Polly"""
    try:
        polly_client = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name='us-east-1'
        ).client('polly')

        response = polly_client.synthesize_speech(
            Engine="neural",
            Text=text,
            OutputFormat="mp3",
            VoiceId="Kajal"
        )

        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                with open(output_file, "wb") as file:
                    file.write(stream.read())
            return True
    except Exception as e:
        print(f"AWS Polly error: {str(e)}")
    return False

def generate_azure_audio(text, output_file):
    """Generate audio using Azure TTS"""
    try:
        subscription_key = os.getenv("AZURE_SPEECH_KEY")
        region = "eastus2"

        # Get access token
        fetch_token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Content-type': 'application/x-www-form-urlencoded',
            'Content-Length': '0'
        }
        response = requests.post(fetch_token_url, headers=headers)
        access_token = response.text

        # Generate speech
        tts_url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-16khz-32kbitrate-mono-mp3',
            'User-Agent': 'azure-tts-sample'
        }

        ssml = f"""
        <speak version='1.0' xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang='en-IN'>
            <voice name='hi-IN-SwaraNeural'>
                {text}
            </voice>
        </speak>
        """

        response = requests.post(tts_url, headers=headers, data=ssml.encode('utf-8'))
        
        if response.status_code == 200:
            with open(output_file, 'wb') as audio:
                audio.write(response.content)
            return True
    except Exception as e:
        print(f"Azure TTS error: {str(e)}")
    return False

def process_text_file(input_file="text.txt", start_line=1):
    """Process each line in the text file and generate audio using all services
    
    Args:
        input_file (str): Path to the input text file
        start_line (int): Line number to start processing from (1-based indexing)
    """
    base_dir = create_directory_structure()
    
    with open(input_file, 'r', encoding='utf-8') as file:
        # Skip lines before start_line
        for i, line in enumerate(file, 1):
            if i < start_line:
                continue
                
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            print(f"\nProcessing line {i}: {line[:50]}...")
            subdir = create_audio_subdirectory(base_dir, i)
            
            # Generate audio using each service
            services = {
                "elevenlabs": (generate_elevenlabs_audio, "audio1.mp3"),
                "google": (generate_google_audio, "audio2.mp3"),
                "aws": (generate_aws_audio, "audio3.mp3"),
                "azure": (generate_azure_audio, "audio4.mp3")
            }
            
            for service_name, (generator_func, filename) in services.items():
                output_file = os.path.join(subdir, filename)
                print(f"Generating {service_name} audio...")
                success = generator_func(line, output_file)
                if success:
                    print(f"Successfully generated {service_name} audio")
                else:
                    print(f"Failed to generate {service_name} audio")
                
                # Add a small delay between API calls
                time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate audio files from text using multiple TTS services')
    parser.add_argument('--start-line', type=int, default=1, help='Line number to start processing from (1-based indexing)')
    parser.add_argument('--input-file', type=str, default='text.txt', help='Input text file path')
    
    args = parser.parse_args()
    process_text_file(args.input_file, args.start_line) 