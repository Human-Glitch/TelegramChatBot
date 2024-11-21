import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
load_dotenv()

import replicate
from openai import OpenAI
import pandas as pd
import numpy as np

from questions import answer_question
from functions import functions, run_function
import json
import requests

CODE_PROMPT = """
Here are two input:output examples for code generation. Please use these and follow the styling for future requests that you think are pertinent to the request.
Make sure All HTML is generated with the JSX flavoring.
// SAMPLE 1
// A Blue Box with 3 yellow cirles inside of it that have a red outline
<div style={{   backgroundColor: 'blue',
  padding: '20px',
  display: 'flex',
  justifyContent: 'space-around',
  alignItems: 'center',
  width: '300px',
  height: '100px', }}>
  <div style={{     backgroundColor: 'yellow',
    borderRadius: '50%',
    width: '50px',
    height: '50px',
    border: '2px solid red'
  }}></div>
  <div style={{     backgroundColor: 'yellow',
    borderRadius: '50%',
    width: '50px',
    height: '50px',
    border: '2px solid red'
  }}></div>
  <div style={{     backgroundColor: 'yellow',
    borderRadius: '50%',
    width: '50px',
    height: '50px',
    border: '2px solid red'
  }}></div>
</div>
"""

openai = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
tg_bot_token = os.environ['TG_BOT_TOKEN']

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the CSV file
csv_path = os.path.join(current_dir, "processed", "embeddings.csv")
df = pd.read_csv(csv_path, index_col=0)
df["embeddings"] = df["embeddings"].apply(eval).apply(np.array)

message_history = []

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

def generate_prompt(messages):
  return "\n".join(f"[INST] {message['text']} [/INST]"
                   if message['isUser'] else message['text']
                   for message in messages)
  
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_history.append({"isUser": True, "text": update.message.text})

    prompt = generate_prompt(message_history)

    input = {
        "top_p": 1,
        "prompt": prompt,
        "temperature": 0.5,
        "max_new_tokens": 500,
        "min_new_tokens": -1
    }
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Let me think...")

    human_readable_output = ""

    for event in replicate.stream(
        "meta/llama-2-70b-chat",
        input=input
    ): human_readable_output += event.data
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=human_readable_output[:-2])
  
    message_history.append({"isUser": False, "text": human_readable_output})
        
async def transcribe_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # Make sure we have a voice file to transcribe
  voice_id = update.message.voice.file_id
  if voice_id:
        file = await context.bot.get_file(voice_id)
        await file.download_to_drive(f"voice_note_{voice_id}.ogg")
        await update.message.reply_text("Voice note downloaded, transcribing now")
        audio_file = open(f"voice_note_{voice_id}.ogg", "rb")
        transcript = openai.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
        await update.message.reply_text(
            f"Transcript finished:\n {transcript.text}"
        )

async def mozilla(update: Update, context: ContextTypes.DEFAULT_TYPE):
  answer = answer_question(df, question=update.message.text, debug=True)
  await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
  
async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
  response = openai.images.generate(prompt=update.message.text,
                                    model="dall-e-3",
                                    n=1,
                                    size="1024x1024")
  image_url = response.data[0].url
  image_response = requests.get(image_url)
  await context.bot.send_photo(chat_id=update.effective_chat.id,
                               photo=image_response.content)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I'm a bot, please talk to me!")

if __name__ == '__main__':
  application = ApplicationBuilder().token(tg_bot_token).build()

  start_handler = CommandHandler('start', start)
  chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chat)
  mozilla_handler = CommandHandler('mozilla', mozilla)
  image_handler = CommandHandler('image', image)
  voice_handler = MessageHandler(filters.VOICE, transcribe_message)
  
  application.add_handler(start_handler)
  application.add_handler(chat_handler)
  application.add_handler(mozilla_handler)
  application.add_handler(image_handler)
  application.add_handler(voice_handler)

  application.run_polling()