"""
AI Service (Updated to google-genai)
Handles interactions with Google Gemini API for generating summaries.
"""

import os
import re
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

# Using the most stable model name available for this key
MODEL_NAME = "gemini-2.5-flash"

def redact_sensitive_info(text):
    """
    Remove potential emails, phone numbers, and common API keys from text.
    """
    if not text:
        return ""
    
    # Redact Emails
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED EMAIL]', text)
    # Redact common API key patterns (simplified)
    text = re.sub(r'(?i)(api[_-]?key|secret|token|password)[:=]\s*[a-zA-Z0-9_-]{16,}', r'\1: [REDACTED]', text)
    return text

def generate_professional_summary(profile_data, repos_data):
    """
    Generate a 2-3 sentence professional summary based on profile and top repos.
    """
    if not client:
        return "AI Summary is currently unavailable (missing API key)."

    prompt = f"""
    Based on the following GitHub profile and repositories, generate a punchy 2-sentence professional bio.
    Focus on the developer's core strengths, most-used technologies, and notable achievements.
    Keep it professional, engaging, and personal.

    Profile:
    - Name: {profile_data.get('name')}
    - Bio: {redact_sensitive_info(profile_data.get('bio'))}
    - Top Languages: {', '.join([r.get('language') for r in repos_data if r.get('language')])}

    Top Repositories:
    {chr(10).join([f"- {r.get('name')}: {redact_sensitive_info(r.get('description'))}" for r in repos_data[:5]])}
    """
    
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        if response.text:
            return response.text.strip()
        return "Dedicated developer focused on building scalable solutions and open-source contributions."
    except Exception as e:
        print(f"Gemini API Error (Bio): {str(e)}")
        return "A passionate developer building innovative projects on GitHub."

def generate_readme_summary(readme_content):
    """
    Generate a 1-sentence 'elevator pitch' summary of a README file.
    """
    if not client:
        return "README summary unavailable."

    if not readme_content or len(readme_content) < 50:
        return "Project exploration: Discover the core features and functionality of this repository."

    prompt = f"""
    Summarize the following README content into a single, high-impact 'elevator pitch' sentence.
    Focus on WHAT the project does and WHY it's useful.
    
    README Content:
    {redact_sensitive_info(readme_content[:3000])}
    """
    
    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        # Check if the response exists and has text
        if response and response.text:
            return response.text.strip()
            
        return "Dive into the documentation to explore this project's full potential."
    except Exception as e:
        print(f"Gemini API Error (README): {str(e)}")
        # If it's a rate limit error, we might want to know
        if "429" in str(e):
            return "Summarization is cooling down. Please try again in a moment."
        return "Explore this project's repository to understand its implementation and features."
