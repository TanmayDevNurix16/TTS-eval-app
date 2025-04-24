import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import html
from typing import Dict, Optional

class PollyTTS:
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, region_name: str = 'us-east-1'):
        """Initialize Polly client with AWS credentials."""
        self.polly_client = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        ).client('polly')

    def text_to_ssml(self, text: str, language: str = "en-US") -> str:
        """
        Convert plain text to SSML format with language support.
        
        Args:
            text (str): Input text
            language (str): Language code (e.g., "en-US", "hi-IN")
        """
        # Escape special characters
        escaped_text = html.escape(text)
        
        # Basic SSML template with language support
        ssml = f"""
        <speak>
            <lang xml:lang="{language}">
                {escaped_text}
            </lang>
        </speak>
        """
        return ssml.strip()

    def generate_speech(
        self,
        text: str,
        output_file: str,
        voice_id: str = "Joanna",
        language: str = "en-US",
        engine: str = "neural",
        speech_rate: str = "medium"
    ) -> Dict:
        """
        Generate speech from text using Amazon Polly.
        
        Args:
            text (str): Input text
            output_file (str): Path to save the audio file
            voice_id (str): Polly voice ID
            language (str): Language code
            engine (str): Either "neural" or "standard"
            speech_rate (str): Speech rate (slow, medium, fast)
        """
        try:
            # Convert text to SSML
            ssml_text = self.text_to_ssml(text, language)

            # Add speech rate control to SSML if needed
            if speech_rate != "medium":
                ssml_text = ssml_text.replace("<speak>", 
                    f'<speak><prosody rate="{speech_rate}">')
                ssml_text = ssml_text.replace("</speak>", 
                    "</prosody></speak>")

            # Request speech synthesis
            response = self.polly_client.synthesize_speech(
                Engine=engine,
                Text=ssml_text,
                TextType="ssml",
                OutputFormat="mp3",
                VoiceId=voice_id
            )

            # Save the audio file
            if "AudioStream" in response:
                with closing(response["AudioStream"]) as stream:
                    with open(output_file, "wb") as file:
                        file.write(stream.read())
                
                return {
                    "status": "success",
                    "output_file": output_file,
                    "voice_id": voice_id,
                    "text_length": len(text),
                    "file_size": os.path.getsize(output_file)
                }

        except (BotoCoreError, ClientError) as error:
            return {
                "status": "error",
                "message": str(error)
            }

def get_available_voices(polly_client) -> Dict:
    """Get all available voices from Amazon Polly."""
    try:
        response = polly_client.describe_voices()
        return {
            "status": "success",
            "voices": response["Voices"]
        }
    except (BotoCoreError, ClientError) as error:
        return {
            "status": "error",
            "message": str(error)
        }

# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    # Initialize TTS with AWS credentials
    tts = PollyTTS(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    # Example for English text
    # english_result = tts.generate_speech(
    #     text="Hello, this is a test message!",
    #     output_file="english_output.mp3",
    #     voice_id="Joanna",
    #     language="en-US"
    # )
    # print("English TTS Result:", english_result)

    # # Example for Hindi text
    # hindi_result = tts.generate_speech(
    #     text="नमस्ते, यह एक परीक्षण संदेश है!",
    #     output_file="hindi_output.mp3",
    #     voice_id="Kajal",  # Use an appropriate Hindi voice
    #     language="hi-IN"
    # )
    # print("Hindi TTS Result:", hindi_result)

    # Example for mixed text
    mixed_result = tts.generate_speech(
        text="Hello नमस्ते, this is a mixed message! at 5:30pm",
        output_file="output.mp3",
        voice_id="Kajal",  # Use a voice that supports both languages
        language="en-IN"  # Primary language
    )
    print("Mixed TTS Result:", mixed_result)