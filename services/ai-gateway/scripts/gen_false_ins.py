# ruff: noqa
import os

os.system('pip install gTTS')
from gtts import gTTS

texts = ['Hello doctor.', 'I need help.', 'I have medical insurance.']
for i, text in enumerate(texts):
    tts = gTTS(text, lang='en')
    tts.save(f'/app/debug/false_ins_{i}.mp3')
    os.system(f'ffmpeg -i /app/debug/false_ins_{i}.mp3 -ar 16000 -ac 1 /app/debug/false_ins_{i}.wav -y')

