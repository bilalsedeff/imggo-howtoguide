"""
Resume Parsing - Python Integration Example
Extract structured data from resume images and integrate with ATS systems
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List

sys.path.append(str(Path(__file__).parent.parent.parent.parent / "examples" / "common"))

from imggo_client import ImgGoClient


def process_resume(image_path: str) -> str:
    """Process resume image and extract text"""
    client = ImgGoClient()

    PATTERN_ID = os.getenv("RESUME_PATTERN_ID", "pat_resume_text")

    print(f"\nProcessing resume: {Path(image_path).name}")

    result = client.process_image(
        image_path=image_path,
        pattern_id=PATTERN_ID
    )

    return result  # Plain text string


def parse_resume_text(text: str) -> dict:
    """Parse resume text into structured data"""
    resume = {
        'candidate_name': None,
        'email': None,
        'phone': None,
        'location': None,
        'linkedin': None,
        'summary': None,
        'skills': [],
        'experience': [],
        'education': [],
        'certifications': [],
        'languages': []
    }

    # Extract email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_match:
        resume['email'] = email_match.group(0)

    # Extract phone (simplified - supports various formats)
    phone_patterns = [
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\+\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    ]
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            resume['phone'] = phone_match.group(0)
            break

    # Extract LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
    if linkedin_match:
        resume['linkedin'] = 'https://' + linkedin_match.group(0)

    # Extract name (usually first line or after specific keywords)
    lines = text.split('\n')
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if line and not re.search(r'@|linkedin|github|http', line, re.IGNORECASE):
            # Likely candidate name
            if len(line.split()) <= 4 and len(line) > 5:
                resume['candidate_name'] = line
                break

    # Extract skills
    skills_section_match = re.search(r'(?:Skills|Technical Skills|Core Competencies):?\s*([^\n]+(?:\n(?!Experience|Education|Certifications)[^\n]+)*)', text, re.IGNORECASE | re.MULTILINE)
    if skills_section_match:
        skills_text = skills_section_match.group(1)
        # Split by common delimiters
        skills = re.split(r'[,;•\|]', skills_text)
        resume['skills'] = [skill.strip() for skill in skills if skill.strip()]

    # Extract experience (simplified)
    experience_match = re.search(r'(?:Experience|Work Experience|Employment):?\s*(.+?)(?=Education|Certifications|Skills|\Z)', text, re.IGNORECASE | re.DOTALL)
    if experience_match:
        experience_text = experience_match.group(1)
        # Try to parse job entries (company, title, dates)
        job_patterns = [
            r'([A-Z][\w\s&,.-]+)\s+[-–]\s+([A-Z][\w\s&,.-]+)\s+\(?(\d{4}\s*-\s*(?:\d{4}|Present))\)?',
        ]
        for pattern in job_patterns:
            for match in re.finditer(pattern, experience_text):
                resume['experience'].append({
                    'title': match.group(1).strip(),
                    'company': match.group(2).strip(),
                    'dates': match.group(3).strip()
                })

    # Extract education
    education_match = re.search(r'(?:Education):?\s*(.+?)(?=Experience|Certifications|Skills|\Z)', text, re.IGNORECASE | re.DOTALL)
    if education_match:
        education_text = education_match.group(1)
        # Look for degrees
        degree_keywords = ['Bachelor', 'Master', 'PhD', 'Associate', 'B.S.', 'M.S.', 'B.A.', 'M.A.']
        for keyword in degree_keywords:
            if keyword in education_text:
                # Extract degree info
                degree_match = re.search(rf'{keyword}[^\n]+', education_text)
                if degree_match:
                    resume['education'].append(degree_match.group(0).strip())

    return resume


def score_resume(resume: dict, job_requirements: List[str]) -> dict:
    """Score resume against job requirements"""
    scoring = {
        'overall_score': 0,
        'skill_matches': [],
        'skill_gaps': [],
        'experience_years': 0,
        'education_level': 0
    }

    # Check skill matches
    candidate_skills = [skill.lower() for skill in resume.get('skills', [])]

    for req_skill in job_requirements:
        if any(req_skill.lower() in candidate_skill for candidate_skill in candidate_skills):
            scoring['skill_matches'].append(req_skill)
        else:
            scoring['skill_gaps'].append(req_skill)

    # Calculate skill match score (0-100)
    if job_requirements:
        skill_score = (len(scoring['skill_matches']) / len(job_requirements)) * 100
    else:
        skill_score = 0

    # Estimate years of experience (simplified)
    experience = resume.get('experience', [])
    for job in experience:
        dates = job.get('dates', '')
        if '-' in dates:
            parts = dates.split('-')
            if len(parts) == 2:
                try:
                    end_year = 2024 if 'Present' in parts[1] else int(re.search(r'\d{4}', parts[1]).group())
                    start_year = int(re.search(r'\d{4}', parts[0]).group())
                    scoring['experience_years'] += end_year - start_year
                except:
                    pass

    # Calculate experience score
    experience_score = min(scoring['experience_years'] * 10, 100)

    # Check education level
    education = resume.get('education', [])
    education_text = ' '.join(education).lower()

    if 'phd' in education_text or 'doctorate' in education_text:
        scoring['education_level'] = 100
    elif 'master' in education_text or 'm.s.' in education_text or 'm.a.' in education_text:
        scoring['education_level'] = 80
    elif 'bachelor' in education_text or 'b.s.' in education_text or 'b.a.' in education_text:
        scoring['education_level'] = 60
    elif 'associate' in education_text:
        scoring['education_level'] = 40
    else:
        scoring['education_level'] = 20

    # Calculate overall score (weighted average)
    scoring['overall_score'] = int(
        (skill_score * 0.5) +
        (experience_score * 0.3) +
        (scoring['education_level'] * 0.2)
    )

    return scoring


def save_to_ats(resume: dict, scoring: dict) -> bool:
    """Save resume to Applicant Tracking System"""
    print("\n" + "="*60)
    print("SAVING TO ATS")
    print("="*60)

    # In production, integrate with ATS (Greenhouse, Lever, Workday, etc.)
    ats_payload = {
        'candidate': {
            'name': resume.get('candidate_name'),
            'email': resume.get('candidate_name'),
            'phone': resume.get('phone'),
            'linkedin': resume.get('linkedin')
        },
        'profile': {
            'skills': resume.get('skills', []),
            'experience_years': scoring.get('experience_years'),
            'education': resume.get('education', [])
        },
        'scoring': {
            'overall_score': scoring.get('overall_score'),
            'skill_matches': scoring.get('skill_matches', []),
            'skill_gaps': scoring.get('skill_gaps', [])
        },
        'status': 'new_application'
    }

    print("ATS Payload:")
    print(json.dumps(ats_payload, indent=2))

    # Simulate API call
    # response = requests.post('https://ats-system.example.com/api/candidates', json=ats_payload)

    print("\n✓ Resume saved to ATS (simulated)")
    return True


def generate_candidate_summary(resume: dict, scoring: dict) -> str:
    """Generate recruiter summary"""
    lines = []

    lines.append("CANDIDATE SUMMARY")
    lines.append("=" * 60)
    lines.append(f"Name: {resume.get('candidate_name', 'N/A')}")
    lines.append(f"Email: {resume.get('email', 'N/A')}")
    lines.append(f"Phone: {resume.get('phone', 'N/A')}")

    if resume.get('linkedin'):
        lines.append(f"LinkedIn: {resume['linkedin']}")

    lines.append("")
    lines.append(f"Overall Score: {scoring['overall_score']}/100")
    lines.append(f"Experience: ~{scoring['experience_years']} years")

    lines.append("")
    lines.append(f"SKILLS ({len(resume.get('skills', []))} total):")
    for skill in resume.get('skills', [])[:10]:
        lines.append(f"  • {skill}")

    if scoring.get('skill_matches'):
        lines.append("")
        lines.append(f"MATCHING SKILLS ({len(scoring['skill_matches'])}):")
        for skill in scoring['skill_matches']:
            lines.append(f"  ✓ {skill}")

    if scoring.get('skill_gaps'):
        lines.append("")
        lines.append(f"SKILL GAPS ({len(scoring['skill_gaps'])}):")
        for skill in scoring['skill_gaps']:
            lines.append(f"  - {skill}")

    lines.append("")
    lines.append(f"EDUCATION:")
    for edu in resume.get('education', []):
        lines.append(f"  {edu}")

    lines.append("")
    lines.append("RECOMMENDATION:")
    if scoring['overall_score'] >= 80:
        lines.append("  ✓ STRONG CANDIDATE - Schedule interview")
    elif scoring['overall_score'] >= 60:
        lines.append("  ⚠ POTENTIAL FIT - Review in detail")
    else:
        lines.append("  ✗ NOT A MATCH - Consider for other roles")

    return "\n".join(lines)


def main():
    print("="*60)
    print("RESUME PARSING - PYTHON EXAMPLE")
    print("="*60)

    if not os.getenv("IMGGO_API_KEY"):
        print("\n✗ Error: IMGGO_API_KEY not set")
        sys.exit(1)

    test_image = Path(__file__).parent.parent.parent.parent / "test-images" / "resume1.jpg"

    if not test_image.exists():
        print(f"\n⚠ Test image not found: {test_image}")
        print("Using placeholder for demonstration")
        sys.exit(1)

    try:
        # Process resume
        resume_text = process_resume(str(test_image))

        # Save raw text
        output_file = "resume_raw.txt"
        with open(output_file, 'w') as f:
            f.write(resume_text)
        print(f"\n✓ Saved raw text to {output_file}")

        # Parse resume
        resume = parse_resume_text(resume_text)

        # Save parsed JSON
        json_file = "resume_parsed.json"
        with open(json_file, 'w') as f:
            json.dump(resume, f, indent=2)
        print(f"✓ Saved parsed data to {json_file}")

        print("\n" + "="*60)
        print("PARSED RESUME DATA")
        print("="*60)
        print(f"Name: {resume.get('candidate_name')}")
        print(f"Email: {resume.get('email')}")
        print(f"Phone: {resume.get('phone')}")
        print(f"LinkedIn: {resume.get('linkedin')}")
        print(f"\nSkills ({len(resume.get('skills', []))}):")
        for skill in resume.get('skills', [])[:10]:
            print(f"  • {skill}")

        # Score against job requirements
        job_requirements = [
            'Python', 'JavaScript', 'React', 'Node.js',
            'REST API', 'SQL', 'Git', 'Agile'
        ]

        print(f"\nScoring against job requirements...")
        scoring = score_resume(resume, job_requirements)

        print("\n" + "="*60)
        print("CANDIDATE SCORING")
        print("="*60)
        print(f"Overall Score: {scoring['overall_score']}/100")
        print(f"Experience: ~{scoring['experience_years']} years")

        print(f"\nSkill Matches ({len(scoring['skill_matches'])}/{len(job_requirements)}):")
        for skill in scoring['skill_matches']:
            print(f"  ✓ {skill}")

        if scoring['skill_gaps']:
            print(f"\nSkill Gaps ({len(scoring['skill_gaps'])}):")
            for skill in scoring['skill_gaps']:
                print(f"  - {skill}")

        # Generate summary
        summary = generate_candidate_summary(resume, scoring)
        print("\n" + summary)

        # Save to ATS
        save_to_ats(resume, scoring)

        # Save summary
        summary_file = "candidate_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(summary)
        print(f"\n✓ Saved candidate summary to {summary_file}")

        print("\n✓ Resume parsing completed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
