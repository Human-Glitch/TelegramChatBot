# TelegramChatBot

**TelegramChatBot** is a Python-based chatbot that integrates with the Telegram messaging platform and OpenAI's API to provide intelligent conversational responses. Supports multi-modal responses for text, voice, and images.
Uses the following in the backend:
1. OpenAI assistant for general responses and code interpreter.
2. Whisper for Voice to Text. 
3. Uses DALL-E for image generation. 

---

## Features

- **Telegram Integration**: Utilizes the [telebot](https://github.com/eternnoir/pyTelegramBotAPI) library to interact with Telegram's API.  
- **OpenAI Integration**: Connects to OpenAI's API to generate context-aware responses for text, images, and voice.
- **Fine-tuned Responses**: Enhanced search for Mozilla documentation related answers.

---

## Demo
Ask questions and get intelligent responses.


<img width="1063" alt="image" src="https://github.com/user-attachments/assets/125c0cf1-8959-4738-9dd2-5295a7b53826" />

---
Use function calling to ask chat to render SVG images to the screen.

<img width="1065" alt="image" src="https://github.com/user-attachments/assets/4ebcf919-0ccc-4660-b1bd-3370eff2190a" />

---

Ask chat for fine-tuned responses from Mozilla documentation.

<img width="1046" alt="image" src="https://github.com/user-attachments/assets/06bc99ae-05cd-4eb3-8939-f2452eccec70" />

---
Ask chat to generate python code and execute it.

<img width="1059" alt="image" src="https://github.com/user-attachments/assets/334ca52c-ba27-45ab-b194-003d01d68cd1" />

---

Ask chat to generate images via text or voice commands.

<img width="1055" alt="image" src="https://github.com/user-attachments/assets/18126005-0ecc-45b0-b6aa-ec10c2603363" />

---

## Prerequisites

- **Python 3.8 or higher**: Ensure Python is installed on your system.  
- **Poetry**: A tool for dependency management and packaging in Python.  
- **Telegram Bot Token**: Obtain from [BotFather](https://t.me/BotFather) on Telegram.  
- **OpenAI API Key**: Acquire from [OpenAI](https://platform.openai.com/).

---

## Installation

1. **Clone the Repository**  
   ```bash
   git clone <REPOSITORY_URL>
   ```
   
2. **Install Poetry**  
   Follow the official installation guide at [Poetry's Documentation](https://python-poetry.org/docs/#installation) to install Poetry on your system.

3. **Install Dependencies**  
   Navigate to the project directory and run:
   ```bash
   poetry install
   ```
   This will create a virtual environment and install all necessary dependencies specified in the `pyproject.toml` file.

4. **Configure Environment Variables**  
   Create a `.env` file in the project root and add your credentials:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   ```
   Replace `your_telegram_bot_token` and `your_openai_api_key` with your actual credentials.

---

## Usage

1. **Run the Bot**  
   ```bash
   poetry run python3 main.py
   ```

2. **Interact on Telegram**  
   Start a chat with your bot on Telegram and use the `/start` command to begin.

---

## Commands
- Just start by typing or using voice.
- Use `/mozilla` command for fine-tuned respones from Mozilla docs.
- **/help**: Provides a list of available commands and their descriptions.

## License

This project is licensed under the [Apache License 2.0](LICENSE).

---

## Acknowledgments

- [telebot](https://github.com/eternnoir/pyTelegramBotAPI): For providing the Telegram API wrapper.  
- [OpenAI, Whisper, DALL-E](https://platform.openai.com/): For the AI language model integration.
- Instructors: Noah Hein, Swyx for course `Level Up From Software Engineer to AI Engineer`
