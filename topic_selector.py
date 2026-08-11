import json
import os
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

HISTORY_FILE = "history.json"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_history(history_data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history_data, f, indent=4)

def select_topic():
    history = load_history()
    used_topics = [item.get("topic", "") for item in history]
    
    prompt = f"""
    You are an expert social media manager for RankResume.pro, a platform for ATS-friendly resumes and job hunting.
    I need a fresh, engaging topic for a daily social media post.
    
    Previous topics already used: {used_topics}
    
    Requirements:
    - Pick a completely new topic or a unique sub-angle related to: improving ATS scores, resume building tips and tricks, job hunting strategies, or how specific top companies (e.g., Google, Amazon, fast-growing startups) hire.
    - The topic must be highly engaging and designed to attract job seekers.
    - Return ONLY the topic in a single line, nothing else. No quotes, no explanations.
    """

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=50
    )
    
    new_topic = response.choices[0].message.content.strip()
    # Strip any potential quotes just in case
    new_topic = new_topic.strip('"').strip("'")
    return new_topic

if __name__ == "__main__":
    print(select_topic())
