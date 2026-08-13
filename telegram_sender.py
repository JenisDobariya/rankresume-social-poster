import os
from telegram import Bot
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def send_to_telegram(image_path: str, caption: str):
    """Sends the generated image and caption to the configured Telegram chat."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found in environment.")
        
    print(f"Sending to Telegram chat: {chat_id}...")
    
    # Telegram captions have a strict 1024 character limit for photos
    if len(caption) > 1024:
        print(f"Warning: Caption is {len(caption)} chars, truncating to 1024 to fit Telegram limits.")
        caption = caption[:1021] + "..."
    
    # Send photo using async with python-telegram-bot v20+
    async with Bot(token=bot_token) as bot:
        with open(image_path, "rb") as photo:
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption
            )
    print("Successfully sent to Telegram.")

if __name__ == "__main__":
    # Test execution (requires an actual image path and env vars)
    pass
