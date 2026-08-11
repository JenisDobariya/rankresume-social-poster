import asyncio
import os
import sys
from datetime import datetime
import traceback

from topic_selector import select_topic, load_history, save_history
from image_gen import run_image_pipeline
from caption_gen import generate_caption
from telegram_sender import send_to_telegram

async def run_daily_pipeline():
    print("--- Starting RankResume.pro Daily Content Pipeline ---")
    
    try:
        # Step 1: Select Topic
        print("Selecting topic...")
        topic = await asyncio.to_thread(select_topic)
        print(f"Selected Topic: {topic}")
        
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Step 2 & 3: Run Image Gen and Caption Gen concurrently
        print("Generating image and caption concurrently...")
        image_task = asyncio.create_task(asyncio.to_thread(run_image_pipeline, topic, date_str))
        caption_task = asyncio.create_task(asyncio.to_thread(generate_caption, topic))
        
        # Wait for both tasks to complete
        image_path, caption = await asyncio.gather(image_task, caption_task)
        
        print(f"Image generated at: {image_path}")
        print(f"Caption generated (length: {len(caption)} chars)")
        
        # Step 4: Save History
        print("Saving to history...")
        history = load_history()
        history.append({
            "date": date_str,
            "topic": topic,
            "image_path": image_path,
            "caption": caption,
            "status": "pending_telegram"
        })
        save_history(history)
        
        # Step 5: Send to Telegram
        print("Sending to Telegram...")
        await send_to_telegram(image_path, caption)
        
        # Update history status
        history[-1]["status"] = "sent"
        save_history(history)
        
        print("--- Pipeline completed successfully ---")
        
    except Exception as e:
        print(f"Pipeline failed: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_daily_pipeline())
