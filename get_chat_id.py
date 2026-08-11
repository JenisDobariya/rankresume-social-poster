import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("TELEGRAM_BOT_TOKEN")

if not token or "your_" in token:
    print("Bot token not found or invalid in .env")
else:
    print(f"Checking updates for bot token...")
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    response = requests.get(url).json()
    
    if not response.get("ok"):
        print(f"Error calling Telegram API: {response}")
    else:
        results = response.get("result", [])
        if not results:
            print("No messages found! Please send a message (like 'Hello') to your bot on Telegram right now, then run this script again.")
        else:
            print("Found recent messages:")
            for msg in results:
                if "message" in msg:
                    chat = msg["message"]["chat"]
                    text = msg["message"].get("text", "")
                    print(f"  -> YOUR CORRECT CHAT ID IS: {chat['id']}")
                    print(f"  -> Message they sent: {text.encode('ascii', 'ignore').decode()}")
                    print("-" * 40)
