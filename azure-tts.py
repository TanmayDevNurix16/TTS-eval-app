# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Replace with your Azure Speech resource key and region
# subscription_key = os.getenv("AZURE_SPEECH_KEY")
# region = "eastus2"  # e.g., "eastus", "westeurope"

# # Step 1: Get an access token
# def get_access_token(subscription_key, region):
#     fetch_token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
#     headers = {
#         'Ocp-Apim-Subscription-Key': subscription_key,
#         'Content-type': 'application/x-www-form-urlencoded',
#         'Content-Length': '0'
#     }
#     response = requests.post(fetch_token_url, headers=headers)
#     response.raise_for_status()
#     return response.text

# # Step 2: Convert text to speech
# def text_to_speech(access_token, region, text, output_file):
#     tts_url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
#     headers = {
#         'Authorization': f'Bearer {access_token}',
#         'Content-Type': 'application/ssml+xml',
#         'X-Microsoft-OutputFormat': 'audio-16khz-32kbitrate-mono-mp3',  # Choose your format
#         'User-Agent': 'azure-tts-sample'
#     }
#     # Choose voice and language; see docs for full list
#     ssml = f"""
#     <speak version='1.0' xml:lang='en-IN'>
#         <voice xml:lang='en-IN' xml:gender='Female' name='en-IN-NeerjaNeural'>
#             {text}
#         </voice>
#     </speak>
#     """
#     response = requests.post(tts_url, headers=headers, data=ssml.encode('utf-8'))
#     response.raise_for_status()
#     with open(output_file, 'wb') as audio:
#         audio.write(response.content)
#     print(f"Audio saved to {output_file}")

# if __name__ == "__main__":
#     text = "Hello नमस्ते, this is a mixed message! at 5:30pm"
#     output_file = "output.mp3"
#     token = get_access_token(subscription_key, region)
#     text_to_speech(token, region, text, output_file)


import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Replace with your Azure Speech resource key and region
subscription_key = os.getenv("AZURE_SPEECH_KEY")
region = "eastus2"  # e.g., "eastus", "westeurope"

# Step 1: Get an access token
def get_access_token(subscription_key, region):
    fetch_token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-type': 'application/x-www-form-urlencoded',
        'Content-Length': '0'
    }
    response = requests.post(fetch_token_url, headers=headers)
    response.raise_for_status()
    return response.text

# Step 2: Convert text to speech
def text_to_speech(access_token, region, text, output_file):
    tts_url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-32kbitrate-mono-mp3',  # Choose your format
        'User-Agent': 'azure-tts-sample'
    }
    
    # We'll use an Indian voice that can handle both English and Hindi
    # Using explicit voice selection with mstts:express-as style
    ssml = f"""
    <speak version='1.0' xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang='en-IN'>
        <voice name='hi-IN-SwaraNeural'>
            {process_mixed_text(text)}
        </voice>
    </speak>
    """
    
    response = requests.post(tts_url, headers=headers, data=ssml.encode('utf-8'))
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return
        
    with open(output_file, 'wb') as audio:
        audio.write(response.content)
    print(f"Audio saved to {output_file}")

def process_mixed_text(text):
    """
    Process mixed text to properly tag Hindi/Devanagari portions with the correct language.
    This is a simple implementation that assumes Devanagari characters can be detected.
    """
    import re
    
    # More robust way of detecting Devanagari text blocks
    # This regex will match continuous blocks of Devanagari script
    devanagari_pattern = re.compile(r'[\u0900-\u097F\u0981-\u09FF]+')
    
    # Start with the text as is
    processed_text = text
    
    # Find all Devanagari segments and replace them with properly tagged versions
    for match in devanagari_pattern.finditer(text):
        devanagari_text = match.group(0)
        # Create properly tagged version for Hindi
        tagged_text = f'<lang xml:lang="hi-IN">{devanagari_text}</lang>'
        # Replace in the original text
        # We need to escape the Devanagari text for regex replacement
        processed_text = processed_text.replace(devanagari_text, tagged_text)
    
    return processed_text

if __name__ == "__main__":
    text = "Hello नमस्ते, this is a mixed message! at 5:30pm"
    output_file = "output.mp3"
    
    try:
        token = get_access_token(subscription_key, region)
        text_to_speech(token, region, text, output_file)
        
        # Print the SSML for debugging purposes
        print("\nGenerated SSML for debugging:")
        ssml = f"""
        <speak version='1.0' xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang='en-IN'>
            <voice name='hi-IN-SwaraNeural'>
                {process_mixed_text(text)}
            </voice>
        </speak>
        """
        print(ssml)
    except Exception as e:
        print(f"An error occurred: {e}")