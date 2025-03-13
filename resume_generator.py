# resume_generator.py
import openai
import json
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

class ResumeGenerator:
    def __init__(self, user_data_path="user_data.json"):
        with open(user_data_path) as f:
            self.user_data = json.load(f)
    
    def analyze_job_description(self, job_description):
        prompt = f"""Extract these elements from the job description:
        - Required technical skills
        - Key responsibilities
        - Tools/technologies mentioned
        Job Description: {job_description}
        Format as JSON: {{"skills": [], "tools": [], "responsibilities": []}}"""
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.choices[0].message.content)
    
    def tailor_resume(self, job_analysis):
        resume = {
            "summary": self._tailor_summary(job_analysis),
            "skills": self._tailor_skills(job_analysis),
            "experience": self._tailor_experience(job_analysis)
        }
        return resume
    
    def _tailor_summary(self, job_analysis):
        prompt = f"""Write a 3-line professional summary incorporating:
        User background: {self.user_data['professional']['summary']}
        Job requirements: {job_analysis}
        Include keywords: {', '.join(job_analysis['skills'])}"""
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt]}
        )
        return response.choices[0].message.content
    
    def generate_cover_letter(self, job_description):
        prompt = f"""Write a cover letter using:
        Job description: {job_description}
        Candidate info: {self.user_data}
        Focus on matching required skills with candidate experience"""
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt]}
        )
        return response.choices[0].message.content

    def save_resume(self, resume, filename="tailored_resume.pdf"):
        # Add PDF generation logic using ReportLab or Jinja2 template
        pass
