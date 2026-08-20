import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def generate_caption(topic: str) -> str:
    import random
    styles = [
        "Storytelling / Pattern Interrupt: Share a relatable narrative or case study about struggling with the topic, then reveal the fix. Use a hook like 'I sent 47 applications. 2 got responses. Then I fixed one thing.'",
        "Controversial / Myth Busting: State the common belief about the topic, tear it down with specific reasons, and provide the counter-intuitive truth. Use a hook like 'Most people do X. The ones who get hired do Y.'",
        "Data-Driven / Analytical: Present shocking stats, break down the technical reasons behind it, and give actionable steps. Use a hook like '75% of resumes never reach a human. Here is why.'",
        "Tough Love / Direct: No fluff, straight to the harsh realities of the job market, followed by immediate, practical advice to fix it. Use a hook like 'Your resume is getting rejected before anyone reads it.'"
    ]
    selected_style = random.choice(styles)
    
    prompt = f"""
    You are an expert social media copywriter for RankResume.pro, a platform helping job seekers land their dream jobs with ATS-friendly resumes.
    Write an engaging, highly readable social media caption for the topic: "{topic}"
    
    Requirements:
    - Target Style for this post: {selected_style}
    - MUST BE STRICTLY UNDER 800 CHARACTERS total length.
    - Start with a highly creative and engaging Hook based on the requested Target Style.
    - DO NOT start with "I" unless it's for a Storytelling post. DO NOT start with a brand mention.
    - Structure: [Hook] -> [Line Break] -> [Insight/Body with 2-3 short, punchy bullet points] -> [Line Break] -> [CTA] -> [Line Break] -> [Hashtags].
    - Be highly specific. Use concrete details and stats.
    - The CTA MUST explicitly include the exact website URL "rankresume.pro" (e.g., "Build your winning resume at rankresume.pro"). Do NOT just copy the same phrase every time.
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
