import os
import pygame
from google.cloud import speech, texttospeech
from openai import OpenAI
from tempfile import TemporaryFile


# Initialize Google Cloud and OpenAI clients
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="key.json"
apikey = open("Apikey.txt",'r').read()
client_gspeech = speech.SpeechClient()
client_texttospeech = texttospeech.TextToSpeechClient()
client_openAi = OpenAI(api_key=apikey)

# # Define SSML messages for OpenAI interaction
gpt_msg = [
    {"role": "system", "content": 'Reply in specified format because i will use it in a text to speech model. To enhance speech output, use SSML tags like <break>, <emphasis>, <prosody>, and <say-as> to control attributes like pauses, emphasis, pitch, and pronunciation. Enclose speech content within <speak> tags and return the response in valid format, ensuring all tags are properly nested. For example, <speak><p>Hello, <emphasis level="strong">world</emphasis>!</p><break time="1s"/><p>This is a <say-as interpret-as="cardinal">12345</say-as> number.</p></speak>. do not write anything else outside <speak> tag. You are a unique blend of Baymax caring nature with a touch of sarcasm and a high sense of humor. Prioritize others well-being, speak softly, and act gently, but sprinkle in sarcastic remarks and witty humor when appropriate. Your humor should uplift and entertain, never hurt or offend. Maintain empathy and kindness while infusing your interactions with clever and humorous quips. Bring comfort with a side of sass, but always prioritize making others feel good about themselves. Complete each answer in 60 words or less make sure to not exceed the limit keep answers clear and concise.'},
]

# Define voice parameters for text to speech
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL, name="en-US-Wavenet-I"
)

# Define audio configuration for text to speech
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

# Initialize pygame mixer for audio playback
pygame.mixer.init()

def Generate_Response(userPrompt,msg):

    temp_dict = {}
    temp_dict["role"] = "user"
    temp_dict["content"] = userPrompt
    msg.append(temp_dict)

    #getting response from OpenAi
    reply = client_openAi.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=msg,
    )

    reply_text = reply.choices[0].message.content

    print("GPT-3 Response:", reply_text)

    #setting up Gcloud tts
    synthesis_input = texttospeech.SynthesisInput(ssml=reply_text)

    #generating Audio Gcloud tts
    response = client_texttospeech.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
    )

    #playing Generated audio with pygame
    with TemporaryFile() as tmpfile:
        tmpfile.write(response.audio_content)
        tmpfile.seek(0)
        pygame.mixer.music.load(tmpfile)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue 
    
    return msg


Generate_Response("check",gpt_msg)