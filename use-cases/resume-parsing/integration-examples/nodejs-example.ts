/**
 * Resume Parsing - TypeScript Integration Example
 * Extract structured data from resume images and integrate with ATS systems
 */

import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

const IMGGO_API_KEY = process.env.IMGGO_API_KEY;
const IMGGO_BASE_URL = process.env.IMGGO_BASE_URL || 'https://img-go.com/api';
const RESUME_PATTERN_ID = process.env.RESUME_PATTERN_ID || 'pat_resume_text';

interface JobResponse {
  success: boolean;
  data: {
    job_id: string;
    status: string;
  };
}

interface JobResult {
  success: boolean;
  data: {
    job_id: string;
    status: 'queued' | 'processing' | 'completed' | 'failed';
    result?: string;
    error?: string;
  };
}

interface Resume {
  candidate_name: string | null;
  email: string | null;
  phone: string | null;
  location: string | null;
  linkedin: string | null;
  summary: string | null;
  skills: string[];
  experience: ExperienceEntry[];
  education: string[];
  certifications: string[];
  languages: string[];
}

interface ExperienceEntry {
  title: string;
  company: string;
  dates: string;
}

interface Scoring {
  overall_score: number;
  skill_matches: string[];
  skill_gaps: string[];
  experience_years: number;
  education_level: number;
}

async function uploadResume(imagePath: string): Promise<string> {
  if (!IMGGO_API_KEY) {
    throw new Error('IMGGO_API_KEY not set');
  }

  const formData = new FormData();
  formData.append('image', fs.createReadStream(imagePath));

  console.log(`\nUploading resume: ${path.basename(imagePath)}`);

  const response = await axios.post<JobResponse>(
    `${IMGGO_BASE_URL}/patterns/${RESUME_PATTERN_ID}/ingest`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${IMGGO_API_KEY}`,
        'Idempotency-Key': `resume-${Date.now()}`,
        ...formData.getHeaders(),
      },
    }
  );

  return response.data.data.job_id;
}

async function waitForResult(jobId: string, maxAttempts: number = 60): Promise<string> {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const response = await axios.get<JobResult>(
      `${IMGGO_BASE_URL}/jobs/${jobId}`,
      {
        headers: {
          'Authorization': `Bearer ${IMGGO_API_KEY}`,
        },
      }
    );

    const { status, manifest, result, error } = response.data.data;

    if (status === 'completed' || status === 'succeeded') {
      const data = manifest || result;
      if (!data) {
        throw new Error('No result in completed job');
      }
      return data;
    }

    if (status === 'failed') {
      throw new Error(`Job failed: ${error || 'Unknown error'}`);
    }

    console.log(`Attempt ${attempt}/${maxAttempts}: Status = ${status}`);
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  throw new Error('Timeout waiting for job completion');
}

function parseResumeText(text: string): Resume {
  const resume: Resume = {
    candidate_name: null,
    email: null,
    phone: null,
    location: null,
    linkedin: null,
    summary: null,
    skills: [],
    experience: [],
    education: [],
    certifications: [],
    languages: [],
  };

  // Extract email
  const emailMatch = text.match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/);
  if (emailMatch) {
    resume.email = emailMatch[0];
  }

  // Extract phone
  const phonePatterns = [
    /\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/,
    /\+\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/
  ];
  for (const pattern of phonePatterns) {
    const phoneMatch = text.match(pattern);
    if (phoneMatch) {
      resume.phone = phoneMatch[0];
      break;
    }
  }

  // Extract LinkedIn
  const linkedinMatch = text.match(/linkedin\.com\/in\/[\w-]+/i);
  if (linkedinMatch) {
    resume.linkedin = 'https://' + linkedinMatch[0];
  }

  // Extract name
  const lines = text.split('\n');
  for (const line of lines.slice(0, 5)) {
    const trimmed = line.trim();
    if (trimmed && !/@|linkedin|github|http/i.test(trimmed)) {
      if (trimmed.split(' ').length <= 4 && trimmed.length > 5) {
        resume.candidate_name = trimmed;
        break;
      }
    }
  }

  // Extract skills
  const skillsMatch = text.match(/(?:Skills|Technical Skills|Core Competencies):?\s*([^\n]+(?:\n(?!Experience|Education|Certifications)[^\n]+)*)/i);
  if (skillsMatch) {
    const skillsText = skillsMatch[1];
    resume.skills = skillsText.split(/[,;•\|]/).map(s => s.trim()).filter(s => s);
  }

  return resume;
}

function scoreResume(resume: Resume, jobRequirements: string[]): Scoring {
  const scoring: Scoring = {
    overall_score: 0,
    skill_matches: [],
    skill_gaps: [],
    experience_years: 0,
    education_level: 0,
  };

  // Check skill matches
  const candidateSkills = resume.skills.map(s => s.toLowerCase());

  for (const reqSkill of jobRequirements) {
    if (candidateSkills.some(cs => cs.includes(reqSkill.toLowerCase()))) {
      scoring.skill_matches.push(reqSkill);
    } else {
      scoring.skill_gaps.push(reqSkill);
    }
  }

  // Calculate skill score
  const skillScore = jobRequirements.length > 0
    ? (scoring.skill_matches.length / jobRequirements.length) * 100
    : 0;

  // Estimate experience years (simplified)
  for (const job of resume.experience) {
    if (job.dates.includes('-')) {
      const [start, end] = job.dates.split('-');
      try {
        const endYear = end.includes('Present') ? 2024 : parseInt(end.match(/\d{4}/)?.[0] || '0');
        const startYear = parseInt(start.match(/\d{4}/)?.[0] || '0');
        if (endYear && startYear) {
          scoring.experience_years += endYear - startYear;
        }
      } catch (e) {
        // Skip invalid dates
      }
    }
  }

  const experienceScore = Math.min(scoring.experience_years * 10, 100);

  // Check education level
  const educationText = resume.education.join(' ').toLowerCase();

  if (educationText.includes('phd') || educationText.includes('doctorate')) {
    scoring.education_level = 100;
  } else if (educationText.includes('master') || educationText.includes('m.s.') || educationText.includes('m.a.')) {
    scoring.education_level = 80;
  } else if (educationText.includes('bachelor') || educationText.includes('b.s.') || educationText.includes('b.a.')) {
    scoring.education_level = 60;
  } else if (educationText.includes('associate')) {
    scoring.education_level = 40;
  } else {
    scoring.education_level = 20;
  }

  // Calculate overall score
  scoring.overall_score = Math.round(
    (skillScore * 0.5) +
    (experienceScore * 0.3) +
    (scoring.education_level * 0.2)
  );

  return scoring;
}

async function saveToATS(resume: Resume, scoring: Scoring): Promise<boolean> {
  console.log('\n' + '='.repeat(60));
  console.log('SAVING TO ATS');
  console.log('='.repeat(60));

  const atsPayload = {
    candidate: {
      name: resume.candidate_name,
      email: resume.email,
      phone: resume.phone,
      linkedin: resume.linkedin,
    },
    profile: {
      skills: resume.skills,
      experience_years: scoring.experience_years,
      education: resume.education,
    },
    scoring: {
      overall_score: scoring.overall_score,
      skill_matches: scoring.skill_matches,
      skill_gaps: scoring.skill_gaps,
    },
    status: 'new_application',
  };

  console.log('ATS Payload:');
  console.log(JSON.stringify(atsPayload, null, 2));

  // In production: await axios.post('https://ats-system.example.com/api/candidates', atsPayload);

  console.log('\n✓ Resume saved to ATS (simulated)');
  return true;
}

async function main() {
  console.log('='.repeat(60));
  console.log('RESUME PARSING - TYPESCRIPT EXAMPLE');
  console.log('='.repeat(60));

  if (!IMGGO_API_KEY) {
    console.error('\n✗ Error: IMGGO_API_KEY not set');
    process.exit(1);
  }

  const testImage = path.join(__dirname, '../../../test-images/resume1.jpg');

  if (!fs.existsSync(testImage)) {
    console.error(`\n⚠ Test image not found: ${testImage}`);
    console.error('Using placeholder for demonstration');
    process.exit(1);
  }

  try {
    // Upload and process resume
    const jobId = await uploadResume(testImage);
    console.log(`✓ Job created: ${jobId}`);

    const resumeText = await waitForResult(jobId);
    console.log('✓ Processing completed');

    // Save raw text
    const outputFile = 'resume_raw.txt';
    fs.writeFileSync(outputFile, resumeText);
    console.log(`\n✓ Saved raw text to ${outputFile}`);

    // Parse resume
    const resume = parseResumeText(resumeText);

    // Save parsed JSON
    const jsonFile = 'resume_parsed.json';
    fs.writeFileSync(jsonFile, JSON.stringify(resume, null, 2));
    console.log(`✓ Saved parsed data to ${jsonFile}`);

    console.log('\n' + '='.repeat(60));
    console.log('PARSED RESUME DATA');
    console.log('='.repeat(60));
    console.log(`Name: ${resume.candidate_name}`);
    console.log(`Email: ${resume.email}`);
    console.log(`Phone: ${resume.phone}`);
    console.log(`LinkedIn: ${resume.linkedin}`);
    console.log(`\nSkills (${resume.skills.length}):`);
    resume.skills.slice(0, 10).forEach(skill => console.log(`  • ${skill}`));

    // Score against job requirements
    const jobRequirements = [
      'Python', 'JavaScript', 'React', 'Node.js',
      'REST API', 'SQL', 'Git', 'Agile'
    ];

    console.log(`\nScoring against job requirements...`);
    const scoring = scoreResume(resume, jobRequirements);

    console.log('\n' + '='.repeat(60));
    console.log('CANDIDATE SCORING');
    console.log('='.repeat(60));
    console.log(`Overall Score: ${scoring.overall_score}/100`);
    console.log(`Experience: ~${scoring.experience_years} years`);

    console.log(`\nSkill Matches (${scoring.skill_matches.length}/${jobRequirements.length}):`);
    scoring.skill_matches.forEach(skill => console.log(`  ✓ ${skill}`));

    if (scoring.skill_gaps.length > 0) {
      console.log(`\nSkill Gaps (${scoring.skill_gaps.length}):`);
      scoring.skill_gaps.forEach(skill => console.log(`  - ${skill}`));
    }

    console.log('\nRECOMMENDATION:');
    if (scoring.overall_score >= 80) {
      console.log('  ✓ STRONG CANDIDATE - Schedule interview');
    } else if (scoring.overall_score >= 60) {
      console.log('  ⚠ POTENTIAL FIT - Review in detail');
    } else {
      console.log('  ✗ NOT A MATCH - Consider for other roles');
    }

    // Save to ATS
    await saveToATS(resume, scoring);

    console.log('\n✓ Resume parsing completed!');

  } catch (error) {
    console.error(`\n✗ Error: ${error}`);
    process.exit(1);
  }
}

main();
