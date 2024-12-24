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

from openai import OpenAI
import pandas as pd
import numpy as np
import time

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

assistant = openai.beta.assistants.create(
    name="Telegram Bot",
    instructions=CODE_PROMPT,
    tools=[
      {"type": "code_interpreter"},
      {"type": "function", "function": functions[0]},
      {"type": "function", "function": functions[1]},
    ],
    model="gpt-4o",
)

THREAD = openai.beta.threads.create()

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
        
async def transcribe_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Safety Check
    voice_id = update.message.voice.file_id
    if voice_id:
        file = await context.bot.get_file(voice_id)
        
        await file.download_to_drive(f"voice_note_{voice_id}.ogg")
        await update.message.reply_text("Voice note downloaded, transcribing now")
        
        audio_file = open(f"voice_note_{voice_id}.ogg", "rb")
        transcript = openai.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        
        message = openai.beta.threads.messages.create(
            thread_id=THREAD.id, role="user", 
            content=transcript.text
        )
        
        run = openai.beta.threads.runs.create(
            thread_id=THREAD.id, 
            assistant_id=assistant.id
        )
        
        await update.message.reply_text(
            f"Transcript finished:\n {transcript.text}\n processing request"
        )
        run = wait_on_run(run, THREAD)
        
        # if we did a function call, run the function and update the thread's state
        if run.status == "requires_action":
            print(run.required_action.submit_tool_outputs.tool_calls)
            
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            response = run_function(name, args)
            
            if name in ("svg_to_png_bytes"):
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=response
                )
            if name in ("generate_image"):
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id, 
                    photo=response.content
                )
                
                run = openai.beta.threads.runs.cancel(
                    thread_id=THREAD.id, 
                    run_id=run.id
                )
                
                run = wait_on_run(run, THREAD)
                return
              
            run = openai.beta.threads.runs.submit_tool_outputs(
                thread_id=THREAD.id,
                run_id=run.id,
                tool_outputs=[
                    {"tool_call_id": tool_call.id, "output": json.dumps(str(response))}
                ],
            )
            
            run = wait_on_run(run, THREAD)
            
        # Retrieve the message object
        messages = openai.beta.threads.messages.list(
            thread_id=THREAD.id, 
            order="asc", 
            after=message.id
        )
        
        # Extract the message content
        message_content = messages.data[0].content[0].text
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=message_content.value
        )

async def mozilla(update: Update, context: ContextTypes.DEFAULT_TYPE):
  answer = answer_question(df, question=update.message.text, debug=True)
  await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
  
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I'm a bot, please talk to me!")
  
def wait_on_run(run, thread):
    while run.status in ("queued", "in_progress"):
        print(run.status)
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run
  
async def assistant_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = openai.beta.threads.messages.create(
        thread_id=THREAD.id, role="user", content=update.message.text
    )
    run = openai.beta.threads.runs.create(
        thread_id=THREAD.id, assistant_id=assistant.id
    )
    run = wait_on_run(run, THREAD)
    
    # if we did a function call, run the function and update the thread's state
    if run.status == "requires_action":
        print(run.required_action.submit_tool_outputs.tool_calls)
        
        tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        response = run_function(name, args)
        
        if name in ("generate_image"):
          run = openai.beta.threads.runs.cancel(thread_id=THREAD.id, run_id=run.id)
          run = wait_on_run(run, THREAD)
          await context.bot.send_photo(
              chat_id=update.effective_chat.id, photo=response.content
          )
          return
        
        if name in ("svg_to_png_bytes"):
            await context.bot.send_photo(
                chat_id=update.effective_chat.id, 
                photo=response
            )
            
        run = openai.beta.threads.runs.submit_tool_outputs(
            thread_id=THREAD.id,
            run_id=run.id,
            tool_outputs=[
                {"tool_call_id": tool_call.id, "output": json.dumps(str(response))}
            ],
        )
        
        run = wait_on_run(run, THREAD)
        
    # Retrieve the message object
    messages = openai.beta.threads.messages.list(
        thread_id=THREAD.id, 
        order="asc", 
        after=message.id
    )
    
    # Extract the message content
    message_content = messages.data[0].content[0].text
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=message_content.value
    )

if __name__ == '__main__':
  application = ApplicationBuilder().token(tg_bot_token).build()

  start_handler = CommandHandler('start', start)
  chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), assistant_chat)
  mozilla_handler = CommandHandler('mozilla', mozilla)
  voice_handler = MessageHandler(filters.VOICE, transcribe_message)
  
  application.add_handler(start_handler)
  application.add_handler(chat_handler)
  application.add_handler(mozilla_handler)
  application.add_handler(voice_handler)

  application.run_polling()