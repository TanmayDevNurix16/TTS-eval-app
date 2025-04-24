
# '''
#   For more samples please visit https://github.com/Azure-Samples/cognitive-services-speech-sdk
# '''
# from dotenv import load_dotenv
# import os
# import azure.cognitiveservices.speech as speechsdk
# load_dotenv()
# # Creates an instance of a speech config with specified subscription key and service region.
# speech_key = os.getenv("AZURE_SPEECH_KEY")
# service_region = "eastus2"

# speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# # Note: the voice setting will not overwrite the voice element in input SSML.
# # speech_config.speech_synthesis_voice_name = "en-US-BrandonMultilingualNeural"

# speech_config.speech_synthesis_voice_name = "hi-IN-SwaraNeural"

# text = "Hello नमस्ते, this is a mixed message! at 5:30pm"

# # use the default speaker as audio output.
# speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

# result = speech_synthesizer.speak_text_async(text).get()
# # Check result
# if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#     print("Speech synthesized for text [{}]".format(text))
# elif result.reason == speechsdk.ResultReason.Canceled:
#     cancellation_details = result.cancellation_details
#     print("Speech synthesis canceled: {}".format(cancellation_details.reason))
#     if cancellation_details.reason == speechsdk.CancellationReason.Error:
#         print("Error details: {}".format(cancellation_details.error_details))
                
                
