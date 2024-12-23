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
- Just start by typing or using voice. A
- Use `/mozilla` command for fine-tuned respones from Mozilla docs.
- **/help**: Provides a list of available commands and their descriptions.

## License

This project is licensed under the [Apache License 2.0](LICENSE).

---

## Acknowledgments

- [telebot](https://github.com/eternnoir/pyTelegramBotAPI): For providing the Telegram API wrapper.  
- [OpenAI, Whisper, DALL-E](https://platform.openai.com/): For the AI language model integration.