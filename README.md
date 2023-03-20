# ai-support-bot
Discord support bot for Reservoir using GPT-4

## Setup
1. Create a discord bot with permission to read and send messages, as well as Message Content intent enabled (see below for reference):
<img width="1443" alt="Screen Shot 2023-03-19 at 5 43 44 PM" src="https://user-images.githubusercontent.com/1606986/226221585-99a2d5bd-40ea-4b4a-a18f-f47e83f6dc0e.png">

2. Create a `.env` file with the required API keys:

  ```
  OPENAI_KEY=[YOUR_OPEN_AI_API_KEY] 
  DISCORD_TOKEN=[YOUR_DISCORD_BOT_TOKEN]
  ```
3. `pip install -r requirements.txt`

## Usage
`python ai.py`
