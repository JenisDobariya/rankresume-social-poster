import os
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# We will use FLUX.1-schnell or SDXL on Hugging Face API
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

def generate_image_prompt(topic: str) -> str:
    """Uses Groq to generate a detailed image prompt based on the topic."""
    prompt = f"""
    You are an expert prompt engineer for AI image generators.
    I need a visual representation for a social media post about: "{topic}"
    The brand is RankResume.pro (ATS-friendly resumes and career growth).
    
    Requirements:
    - Describe a highly aesthetic, clean, modern, professional, corporate yet approachable scene related to resumes or career growth.
    - Include details like lighting, color palette, and composition.
    - The image MUST prominently display a short text headline (MAX 6-8 words) related to the topic: "{topic}". 
    - The image MUST also display the text "rankresume.pro" at the bottom.
    - CRITICAL TEXT RULE: When specifying text, you MUST format it as: `with the exact text "YOUR_TEXT"`. (e.g. `with the exact text "Beat ATS Systems" and at the bottom the text "rankresume.pro"`)
    - Return ONLY the exact image generation prompt, nothing else.
    """

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    
    image_prompt = response.choices[0].message.content.strip()
    return image_prompt

def generate_and_save_image(image_prompt: str, output_path: str) -> str:
    """Calls Hugging Face Inference API to generate the image and saves it."""
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN not found in environment variables.")

    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": image_prompt}
    
    print(f"Generating image with prompt: {image_prompt}")
    
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        image_data = response.content
        print("Image generated successfully via Hugging Face.")
    except requests.exceptions.RequestException as e:
        print(f"Hugging Face API failed ({e}). Falling back to Pollinations.ai...")
        
        # Fallback to Pollinations.ai
        # Format the prompt for the URL
        import urllib.parse
        encoded_prompt = urllib.parse.quote(image_prompt)
        pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true&model=flux"
        
        try:
            fb_response = requests.get(pollinations_url, timeout=60)
            fb_response.raise_for_status()
            image_data = fb_response.content
            print("Image generated successfully via Pollinations.ai.")
        except requests.exceptions.RequestException as fb_e:
            raise Exception(f"Both Hugging Face and Pollinations fallback failed. Last error: {fb_e}")
            
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_data)
        
    add_watermark(output_path)
    return output_path

def add_watermark(image_path: str, text: str = "rankresume.pro"):
    """Overlays the website URL on the image for guaranteed branding."""
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        try:
            # Use Arial if available (standard on Windows)
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()
            
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        width, height = img.size
        x = (width - text_width) / 2
        y = height - text_height - 30 # 30px padding from bottom
        
        # Draw black outline for better contrast
        outline_color = (0, 0, 0, 200)
        for offset in [(1,1), (-1,-1), (1,-1), (-1,1), (0,2), (0,-2), (2,0), (-2,0)]:
            draw.text((x+offset[0], y+offset[1]), text, font=font, fill=outline_color)
            
        # Draw white text
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        img.save(image_path)
        print(f"Added watermark '{text}' to {image_path}")
    except Exception as e:
        print(f"Warning: Failed to add watermark: {e}")

def run_image_pipeline(topic: str, date_str: str) -> str:
    """Branch A: Generate prompt and then image."""
    image_prompt = generate_image_prompt(topic)
    output_path = os.path.join("output", "images", f"{date_str}.png")
    generate_and_save_image(image_prompt, output_path)
    return output_path

if __name__ == "__main__":
    # Test execution
    topic = "How to optimize your resume for ATS systems"
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print(run_image_pipeline(topic, date_str))
