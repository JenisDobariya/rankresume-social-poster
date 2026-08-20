import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def generate_caption(topic: str) -> str:
    """Uses Groq to generate a simple, jargon-free caption with hashtags at the end."""
    prompt = f"""
    You are an expert social media copywriter for RankResume.pro, a platform helping job seekers land their dream jobs with ATS-friendly resumes.
    Write an engaging, highly readable social media caption for the topic: "{topic}"
    
    Requirements:
    - MUST BE STRICTLY UNDER 800 CHARACTERS total length.
    - Start with a highly creative and engaging Hook. VARY the type of hook for every post (e.g., a bold contrarian claim, a relatable struggle, a surprising fact, a rhetorical question, or a pattern interrupt). DO NOT always start with a percentage or a number. Be smart, unpredictable, and attention-grabbing.
    - DO NOT start with "I" or a brand mention.
    - Structure: [Hook] -> [Line Break] -> [Insight/Body with 2-3 bullet points] -> [Line Break] -> [CTA] -> [Line Break] -> [Hashtags].
    - Be highly specific. Use concrete details and stats in the form of bullet points to explain the insight.
    - The CTA MUST explicitly include the exact website URL "rankresume.pro". Be highly creative and vary the CTA phrasing for every post (e.g., "Build your winning resume at rankresume.pro", "Scan your CV today on rankresume.pro", "Get hired faster with rankresume.pro"). Do NOT just copy the same phrase every time.
    - No corporate jargon (e.g., leverage, synergy, holistic approach).
    - Leave an empty blank line before placing 3-5 relevant hashtags strictly at the VERY END of the caption.
    - Return ONLY the caption text.
    """

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )
    
    caption = response.choices[0].message.content.strip()
    return caption

if __name__ == "__main__":
    topic = "How to optimize your resume for ATS systems"
    print(generate_caption(topic))
