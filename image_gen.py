import os
import json
import random
import urllib.parse
from datetime import datetime
from groq import Groq
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

COLOR_PALETTES = [
    { # Brand Primary (Dark Mode + Electric Blue)
        "bg_color": "#0a0a0a",
        "primary_text": "#ffffff",
        "accent_color": "#3b82f6", # Website button blue
        "footer_bg": "#111111",
        "footer_text": "#ffffff",
        "footer_accent": "#9ca3af"
    },
    { # Brand Secondary (Dark Mode + Indigo/Purple)
        "bg_color": "#050505",
        "primary_text": "#ffffff",
        "accent_color": "#6366f1", # Website "Smarter" text purple
        "footer_bg": "#0a0a0a",
        "footer_text": "#f3f4f6",
        "footer_accent": "#9ca3af"
    },
    { # High Contrast Dark (Dark Grey + Sky Blue)
        "bg_color": "#171717",
        "primary_text": "#ffffff",
        "accent_color": "#38bdf8",
        "footer_bg": "#262626",
        "footer_text": "#ffffff",
        "footer_accent": "#a3a3a3"
    },
    { # Clean Light Mode (White + Brand Blue)
        "bg_color": "#ffffff",
        "primary_text": "#0a0a0a",
        "accent_color": "#2563eb",
        "footer_bg": "#f3f4f6",
        "footer_text": "#111827",
        "footer_accent": "#4b5563"
    }
]

TEMPLATES = [
    "layout_1_bubble.html",
    "layout_2_stats.html",
    "layout_3_checklist.html",
    "layout_4_photo.html"
]

def get_edition_number() -> int:
    try:
        with open("history.json", "r") as f:
            history = json.load(f)
            return len(history) + 1
    except (FileNotFoundError, json.JSONDecodeError):
        return 1

def generate_infographic_content(topic: str) -> dict:
    """Uses Groq to generate structured JSON for the infographic based on the topic."""
    import random
    tones = [
        "Data-driven & Shocking (use hard numbers and percentages)",
        "Direct & Actionable (no fluff, step-by-step instructions)",
        "Myth-busting (challenging conventional wisdom)",
        "Inspirational & Success-focused (focusing on landing the dream job)"
    ]
    selected_tone = random.choice(tones)

    prompt = f"""
    You are an expert copywriter and UI/UX designer for RankResume.pro.
    I need structured content for a highly professional social media infographic about: "{topic}"
    
    Requirements:
    - Target Tone for Copy: {selected_tone}
    - Return ONLY a valid JSON object.
    - Make the copy extremely compelling and specific.
    - For icons, provide ONLY the FontAwesome v6 solid icon class name (e.g., "fa-solid fa-magnifying-glass", "fa-solid fa-check").
    
    The JSON object must have exactly these keys:
    - "headline": The main bold headline. Short and punchy. STRICT MAXIMUM 5 WORDS.
    - "subheadline": A slightly longer explanation below the headline. STRICT MAXIMUM 12 WORDS.
    - "highlight_text": A short, impactful piece of text (e.g., a quote, a massive statistic, or a strong hook). STRICT MAXIMUM 6 WORDS. Use <br> for line breaks to make it look like a poem or haiku if it's a quote.
    - "bullet_1_title": Short title (max 3 words).
    - "bullet_1_text": Short description (max 5 words).
    - "bullet_1_icon": FontAwesome solid class name.
    - "bullet_2_title": ...
    - "bullet_2_text": ...
    - "bullet_2_icon": ...
    - "bullet_3_title": ...
    - "bullet_3_text": ...
    - "bullet_3_icon": ...
    - "bullet_4_title": ...
    - "bullet_4_text": ...
    - "bullet_4_icon": ...
    """

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=4000,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content.strip()
    return json.loads(content)

def get_bg_image_url(topic: str) -> str:
    """Generates a dynamic background image URL using Pollinations."""
    bg_prompt = f"aesthetic dark corporate office background beautiful lighting high quality photography {topic}"
    encoded_prompt = urllib.parse.quote(bg_prompt)
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1350&nologo=true"

def render_html_to_image(data: dict, output_path: str, force_template: str = None):
    """Renders a randomly selected Jinja2 template with a random theme, and uses Playwright to save it as a PNG."""
    env = Environment(loader=FileSystemLoader("templates"))
    
    # Select random template and theme
    selected_template = force_template if force_template else random.choice(TEMPLATES)
    selected_theme = random.choice(COLOR_PALETTES)
    
    template = env.get_template(selected_template)
    
    # Set up viewport and extra data based on template
    if selected_template == "layout_4_photo.html":
        viewport = {"width": 1080, "height": 1350}
        # Fetch an image from pollination.
        data["bg_image_url"] = get_bg_image_url(data.get("headline", "corporate career"))
    else:
        viewport = {"width": 1200, "height": 630}
    
    # Add template variables
    data["edition_number"] = get_edition_number()
    data["theme"] = selected_theme
    
    html_out = template.render(data)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport=viewport)
        
        # Wait until networkidle ensures external background images load before screenshot
        page.set_content(html_out, wait_until="networkidle")
        
        # In case networkidle finishes too early for a heavy remote image, a short wait ensures it paints.
        page.wait_for_timeout(2000) 
        
        page.screenshot(path=output_path)
        browser.close()
        
    print(f"Infographic successfully generated using {selected_template} at: {output_path}")
    return output_path

def run_image_pipeline(topic: str, date_str: str) -> str:
    """Main function called by pipeline.py"""
    print("Generating JSON content via Groq...")
    data = generate_infographic_content(topic)
    
    output_path = os.path.join("output", "images", f"{date_str}.png")
    print("Rendering HTML and capturing screenshot via Playwright...")
    render_html_to_image(data, output_path)
    
    return output_path

if __name__ == "__main__":
    # Test execution
    topic = "How to optimize your resume for ATS systems"
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # For testing, we force layout_4_photo.html so we can verify it works.
    print("Generating JSON content via Groq...")
    data = generate_infographic_content(topic)
    output_path = os.path.join("output", "images", f"{date_str}_test_photo.png")
    render_html_to_image(data, output_path, force_template="layout_4_photo.html")
