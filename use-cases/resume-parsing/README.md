# Resume/CV Parsing Automation

Automate candidate data extraction from resume images with direct upload and JSON output for applicant tracking systems (ATS).

## Business Problem

Recruiters and HR teams face resume screening challenges:

- **Volume overload**: 250+ applications per job posting average
- **Manual data entry**: 5-10 minutes per resume to extract details
- **Inconsistent formats**: Resumes in PDF, Word, images, photos
- **Data quality**: Typos and errors during manual transcription
- **Slow response**: Days or weeks to respond to qualified candidates
- **Lost candidates**: Top talent lost due to slow screening

**Recruitment impact**: 52% of recruiters say the hardest part of recruitment is screening candidates from a large applicant pool.

## Solution: Direct Upload Resume Parsing

Automated resume extraction with direct file upload:

1. **Upload**: Candidate or recruiter uploads resume image/PDF
2. **Extract**: Parse all resume sections (contact, experience, education, skills)
3. **Structure**: Convert to JSON for ATS integration
4. **Match**: Auto-match candidates to job requirements
5. **Rank**: Score candidates based on qualifications
6. **Store**: Sync to ATS (Greenhouse, Lever, Workday)

**Result**: 90% time savings, 5-minute candidate screening, improved candidate experience.

## What Gets Extracted

### JSON Output for ATS Integration

```json
{
  "personal_info": {
    "full_name": "Sarah Johnson",
    "email": "sarah.johnson@email.com",
    "phone": "+1-555-0123",
    "location": {
      "city": "San Francisco",
      "state": "CA",
      "country": "USA"
    },
    "linkedin": "linkedin.com/in/sarahjohnson",
    "github": "github.com/sarahj",
    "portfolio": "sarahjohnson.dev"
  },

  "professional_summary": "Full-stack software engineer with 5+ years of experience building scalable web applications. Expertise in React, Node.js, and cloud architecture. Passionate about clean code and user experience.",

  "work_experience": [
    {
      "company": "TechCorp Inc.",
      "position": "Senior Software Engineer",
      "location": "San Francisco, CA",
      "start_date": "2021-03",
      "end_date": "present",
      "duration_months": 46,
      "responsibilities": [
        "Lead development of microservices architecture serving 10M+ users",
        "Mentored team of 5 junior engineers",
        "Reduced API response time by 40% through optimization"
      ],
      "technologies": ["React", "Node.js", "PostgreSQL", "AWS", "Docker"]
    },
    {
      "company": "StartupXYZ",
      "position": "Software Engineer",
      "location": "Remote",
      "start_date": "2019-06",
      "end_date": "2021-02",
      "duration_months": 21,
      "responsibilities": [
        "Built customer-facing dashboard using React and TypeScript",
        "Implemented CI/CD pipeline reducing deployment time by 60%",
        "Collaborated with design team on UX improvements"
      ],
      "technologies": ["React", "TypeScript", "MongoDB", "GraphQL"]
    }
  ],

  "education": [
    {
      "institution": "University of California, Berkeley",
      "degree": "Bachelor of Science",
      "field": "Computer Science",
      "graduation_year": 2019,
      "gpa": 3.8,
      "honors": ["Dean's List", "Summa Cum Laude"]
    }
  ],

  "skills": {
    "programming_languages": ["JavaScript", "Python", "TypeScript", "Java"],
    "frameworks": ["React", "Node.js", "Express", "Django"],
    "databases": ["PostgreSQL", "MongoDB", "Redis"],
    "tools": ["Git", "Docker", "AWS", "Jenkins", "Kubernetes"],
    "soft_skills": ["Team Leadership", "Agile/Scrum", "Technical Writing"]
  },

  "certifications": [
    {
      "name": "AWS Certified Solutions Architect",
      "issuer": "Amazon Web Services",
      "date": "2022-08",
      "credential_id": "AWS-SA-12345"
    }
  ],

  "projects": [
    {
      "name": "E-commerce Platform",
      "description": "Built full-stack e-commerce platform serving 50k+ monthly users",
      "technologies": ["React", "Node.js", "Stripe API"],
      "url": "github.com/sarahj/ecommerce"
    }
  ],

  "metadata": {
    "total_experience_years": 5.5,
    "career_level": "senior",
    "primary_role": "software_engineer",
    "keywords": ["full-stack", "react", "node.js", "aws", "microservices"],
    "languages": ["English (native)", "Spanish (conversational)"]
  }
}
```

## Pattern Setup

```bash
curl -X POST https://img-go.com/api/patterns \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Resume Parser - Complete",
    "output_format": "json",
    "instructions": "Extract all information from resume/CV. Include personal info (name, email, phone, location, LinkedIn, GitHub), professional summary, complete work history with company names, positions, dates, responsibilities and technologies, education details, skills categorized by type, certifications, projects, and languages. Calculate total years of experience. Preserve all details accurately.",
    "schema": {
      "personal_info": {
        "full_name": "string",
        "email": "email",
        "phone": "phone",
        "location": {
          "city": "string",
          "state": "string",
          "country": "string"
        },
        "linkedin": "url",
        "github": "url"
      },
      "professional_summary": "string",
      "work_experience": [
        {
          "company": "string",
          "position": "string",
          "start_date": "date",
          "end_date": "string",
          "responsibilities": ["string"],
          "technologies": ["string"]
        }
      ],
      "education": [
        {
          "institution": "string",
          "degree": "string",
          "field": "string",
          "graduation_year": "number"
        }
      ],
      "skills": {
        "programming_languages": ["string"],
        "frameworks": ["string"],
        "tools": ["string"]
      },
      "metadata": {
        "total_experience_years": "number",
        "career_level": "string"
      }
    }
  }'
```

## Direct Upload Implementation

### Job Application Portal (React)

```javascript
// ResumeUpload.jsx
import React, { useState } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';

const ResumeUpload = ({ jobId }) => {
  const [uploading, setUploading] = useState(false);
  const [candidateData, setCandidateData] = useState(null);
  const [matchScore, setMatchScore] = useState(null);

  const processResume = async (file) => {
    setUploading(true);

    try {
      // Create FormData for direct upload
      const formData = new FormData();
      formData.append('file', file);

      // Upload directly to ImgGo
      const response = await axios.post(
        `https://img-go.com/api/patterns/${process.env.REACT_APP_PATTERN_ID}/ingest`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${process.env.REACT_APP_API_KEY}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      const jobId = response.data.data.job_id;

      // Poll for results
      const resumeData = await pollJobResult(jobId);

      // Validate data
      const validation = validateResumeData(resumeData);

      if (!validation.isValid) {
        alert('Resume parsing incomplete: ' + validation.errors.join(', '));
        return;
      }

      // Calculate job match score
      const score = await calculateJobMatch(resumeData, jobId);

      setCandidateData(resumeData);
      setMatchScore(score);

      // Submit to backend
      await submitApplication({
        job_id: jobId,
        candidate_data: resumeData,
        match_score: score
      });

      // Show success
      alert('Application submitted successfully!');

    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to process resume');
    } finally {
      setUploading(false);
    }
  };

  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png'],
      'application/pdf': ['.pdf']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    onDrop: (files) => {
      if (files.length > 0) {
        processResume(files[0]);
      }
    }
  });

  const validateResumeData = (data) => {
    const errors = [];

    if (!data.personal_info?.full_name) {
      errors.push('Name not found');
    }

    if (!data.personal_info?.email) {
      errors.push('Email not found');
    }

    if (!data.work_experience || data.work_experience.length === 0) {
      errors.push('No work experience found');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  };

  const calculateJobMatch = async (resumeData, jobId) => {
    // Get job requirements
    const jobReqs = await fetchJobRequirements(jobId);

    let score = 0;

    // Match skills
    const candidateSkills = [
      ...resumeData.skills.programming_languages,
      ...resumeData.skills.frameworks,
      ...resumeData.skills.tools
    ];

    const matchedSkills = jobReqs.required_skills.filter(skill =>
      candidateSkills.some(cs => cs.toLowerCase().includes(skill.toLowerCase()))
    );

    score += (matchedSkills.length / jobReqs.required_skills.length) * 50;

    // Match experience level
    if (resumeData.metadata.total_experience_years >= jobReqs.min_experience) {
      score += 30;
    }

    // Match education
    if (resumeData.education.some(edu =>
      edu.degree.toLowerCase().includes(jobReqs.required_degree.toLowerCase())
    )) {
      score += 20;
    }

    return Math.min(score, 100);
  };

  const pollJobResult = async (jobId) => {
    let attempts = 0;

    while (attempts < 30) {
      const response = await axios.get(
        `https://img-go.com/api/jobs/${jobId}`,
        {
          headers: {
            'Authorization': `Bearer ${process.env.REACT_APP_API_KEY}`
          }
        }
      );

      const data = response.data.data;

      if (data.status === 'completed') {
        return data.result;
      } else if (data.status === 'failed') {
        throw new Error('Processing failed');
      }

      await new Promise(resolve => setTimeout(resolve, 2000));
      attempts++;
    }

    throw new Error('Timeout');
  };

  return (
    <div className="resume-upload">
      <div {...getRootProps()} className="dropzone">
        <input {...getInputProps()} />
        {uploading ? (
          <div className="uploading">
            <Spinner />
            <p>Processing your resume...</p>
          </div>
        ) : (
          <div className="upload-prompt">
            <FileIcon size={48} />
            <h3>Upload Your Resume</h3>
            <p>Drag & drop or click to select</p>
            <p className="hint">Supports PDF, JPG, PNG (max 10MB)</p>
          </div>
        )}
      </div>

      {candidateData && (
        <div className="candidate-preview">
          <h3>Application Preview</h3>
          <div className="match-score">
            <CircularProgress value={matchScore} />
            <span>{matchScore}% Match</span>
          </div>

          <div className="candidate-info">
            <h4>{candidateData.personal_info.full_name}</h4>
            <p>{candidateData.personal_info.email}</p>
            <p>{candidateData.professional_summary}</p>

            <div className="experience">
              <h5>Experience ({candidateData.metadata.total_experience_years} years)</h5>
              {candidateData.work_experience.map((exp, idx) => (
                <div key={idx} className="job">
                  <strong>{exp.position}</strong> at {exp.company}
                  <br />
                  <small>{exp.start_date} - {exp.end_date}</small>
                </div>
              ))}
            </div>

            <div className="skills">
              <h5>Skills</h5>
              <div className="skill-tags">
                {[...candidateData.skills.programming_languages,
                  ...candidateData.skills.frameworks].map((skill, idx) => (
                  <span key={idx} className="tag">{skill}</span>
                ))}
              </div>
            </div>
          </div>

          <button onClick={submitFinalApplication}>
            Submit Application
          </button>
        </div>
      )}
    </div>
  );
};

export default ResumeUpload;
```

### Backend API (Python Flask)

```python
# ats_integration.py
from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime

app = Flask(__name__)

API_KEY = os.environ["IMGGO_API_KEY"]
PATTERN_ID = os.environ["IMGGO_PATTERN_ID"]

@app.route('/api/candidates/upload', methods=['POST'])
def upload_resume():
    """Handle resume upload and parsing"""

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    job_id = request.form.get('job_id')

    # Direct upload to ImgGo
    files = {'file': file}

    response = requests.post(
        f"https://img-go.com/api/patterns/{PATTERN_ID}/ingest",
        headers={"Authorization": f"Bearer {API_KEY}"},
        files=files
    )

    job_id = response.json()["data"]["job_id"]

    # Poll for results
    candidate_data = poll_job_result(job_id)

    # Validate required fields
    if not validate_candidate_data(candidate_data):
        return jsonify({'error': 'Incomplete resume data'}), 422

    # Store in database
    candidate_id = store_candidate(candidate_data, job_id)

    # Sync to ATS (Greenhouse, Lever, etc.)
    sync_to_ats(candidate_id, candidate_data)

    # Send confirmation email
    send_confirmation_email(candidate_data['personal_info']['email'])

    return jsonify({
        'success': True,
        'candidate_id': candidate_id,
        'match_score': calculate_match_score(candidate_data, job_id)
    })

def sync_to_ats(candidate_id, candidate_data):
    """Sync to Greenhouse ATS"""

    # Greenhouse API
    greenhouse_endpoint = "https://harvest.greenhouse.io/v1/candidates"

    payload = {
        'first_name': candidate_data['personal_info']['full_name'].split()[0],
        'last_name': ' '.join(candidate_data['personal_info']['full_name'].split()[1:]),
        'email_addresses': [{
            'value': candidate_data['personal_info']['email'],
            'type': 'personal'
        }],
        'phone_numbers': [{
            'value': candidate_data['personal_info']['phone'],
            'type': 'mobile'
        }],
        'applications': [{
            'job_id': candidate_data.get('applied_job_id')
        }],
        'custom_fields': {
            'years_of_experience': candidate_data['metadata']['total_experience_years'],
            'primary_skills': ', '.join(candidate_data['skills']['programming_languages'][:5])
        }
    }

    response = requests.post(
        greenhouse_endpoint,
        json=payload,
        auth=(os.environ['GREENHOUSE_API_KEY'], '')
    )

    return response.json()

if __name__ == '__main__':
    app.run(port=5000)
```

## ATS Integration Examples

### Greenhouse API

```python
def create_greenhouse_candidate(resume_data):
    """Create candidate in Greenhouse ATS"""

    url = "https://harvest.greenhouse.io/v1/candidates"

    candidate = {
        'first_name': resume_data['personal_info']['full_name'].split()[0],
        'last_name': ' '.join(resume_data['personal_info']['full_name'].split()[1:]),
        'company': resume_data['work_experience'][0]['company'] if resume_data['work_experience'] else None,
        'title': resume_data['work_experience'][0]['position'] if resume_data['work_experience'] else None,
        'email_addresses': [{'value': resume_data['personal_info']['email'], 'type': 'personal'}],
        'phone_numbers': [{'value': resume_data['personal_info']['phone'], 'type': 'mobile'}]
    }

    response = requests.post(
        url,
        json=candidate,
        auth=(os.environ['GREENHOUSE_API_KEY'], '')
    )

    return response.json()
```

### Lever API

```python
def create_lever_candidate(resume_data):
    """Create candidate in Lever ATS"""

    url = "https://api.lever.co/v1/candidates"

    candidate = {
        'name': resume_data['personal_info']['full_name'],
        'emails': [resume_data['personal_info']['email']],
        'phones': [{'type': 'mobile', 'value': resume_data['personal_info']['phone']}],
        'links': [
            resume_data['personal_info'].get('linkedin'),
            resume_data['personal_info'].get('github')
        ],
        'headline': resume_data.get('professional_summary', '')[:100]
    }

    response = requests.post(
        url,
        json=candidate,
        auth=(os.environ['LEVER_API_KEY'], '')
    )

    return response.json()
```

## Performance Metrics

| Metric | Manual Screening | Automated Parsing |
|--------|------------------|-------------------|
| Time per Resume | 5-10 minutes | 30-60 seconds |
| Data Accuracy | 85-90% | 95-98% |
| Cost per Resume | $8-12 | $0.50-1 |
| Daily Capacity (per recruiter) | 40-50 resumes | 500+ resumes |
| Time to First Contact | 3-5 days | Same day |
| Candidate Experience | Average | Excellent |

## Integration Examples

Available in `integration-examples/`:

- [React Job Portal](./integration-examples/react-resume-upload.jsx)
- [Python ATS Backend](./integration-examples/python-ats-api.py)
- [Greenhouse Integration](./integration-examples/greenhouse-sync.py)
- [Lever Integration](./integration-examples/lever-sync.py)

## Next Steps

- Explore [KYC Verification](../kyc-verification) for document uploads
- Review [Direct Upload Patterns](../../examples/direct-upload)
- Set up [ATS Integration](../../integration-guides/ats-systems.md)

---

**SEO Keywords**: resume parser API, CV data extraction, applicant tracking system integration, resume to JSON, direct file upload parsing

**Sources**:
- [Resume Parsing](https://www.affinda.com/resume-parser)
- [ATS Integration](https://www.workable.com/recruiting-resources/ats)
