"""
Create ImgGo Pattern for Resume Parsing
Extract structured data from resume/CV images
"""

import os
import requests
import json

API_KEY = os.getenv("IMGGO_API_KEY")
BASE_URL = "https://img-go.com/api"

def create_resume_pattern():
    """Create pattern for resume/CV parsing"""

    if not API_KEY:
        print("X Error: IMGGO_API_KEY not set")
        return None

    url = f"{BASE_URL}/patterns"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Pattern for resume parsing - using plain text format
    # Based on ImgGo API: format must be json, yaml, xml, csv, or text
    # text format requires plain_text_schema with # headings
    payload = {
        "name": "Resume Parsing - Plain Text",
        "instructions": "Extract all text from the resume/CV including: candidate name, contact information (email, phone, location, LinkedIn), professional summary, work experience with job titles and companies, education, skills, certifications, and languages.",
        "format": "text",
        "plain_text_schema": "# Candidate Information\nName: [name]\nEmail: [email]\nPhone: [phone]\nLocation: [location]\n\n# Professional Summary\n[summary]\n\n# Work Experience\n[experience]\n\n# Education\n[education]\n\n# Skills\n[skills]"
    }

    print("=" * 60)
    print("CREATING RESUME PARSING PATTERN")
    print("=" * 60)
    print()
    print(f"Name: {payload['name']}")
    print(f"Format: {payload['format']}")
    print()

    try:
        response = requests.post(url, headers=headers, json=payload)

        print(f"Response Status: {response.status_code}")
        if response.status_code != 201:
            print(f"Response: {response.text}")

        response.raise_for_status()

        data = response.json()
        pattern_id = data.get("data", {}).get("id")

        print("V Pattern created successfully!")
        print()
        print(f"Pattern ID: {pattern_id}")
        print()
        print("Add to .env:")
        print(f"RESUME_PATTERN_ID={pattern_id}")
        print()

        with open("pattern_id.txt", "w") as f:
            f.write(pattern_id)
        print("V Saved to pattern_id.txt")

        return pattern_id

    except Exception as e:
        print(f"X Error: {e}")
        return None


if __name__ == "__main__":
    create_resume_pattern()
