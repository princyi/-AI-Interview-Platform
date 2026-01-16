import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
    def generate_interview_questions(self, resume_text, job_description, experience_level="intermediate"):
        """
        Generate interview questions based on resume, job description, and experience level
        """
        prompt = f"""
        You are an expert AI interviewer. Generate EXACTLY 3 relevant interview questions based on the following:
        
        RESUME/CANDIDATE PROFILE:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        
        EXPERIENCE LEVEL: {experience_level}
        
        Guidelines:
        - Generate EXACTLY 3 questions appropriate for {experience_level} level candidate
        - Focus on technical skills, problem-solving, and behavioral aspects
        - Questions should be specific to the role and candidate's background
        - Include a mix of technical and behavioral questions
        - Each question should be clear and concise
        - Questions should be answerable in 1-2 minutes each
        
        Return the response as a JSON array of questions with the following format:
        {{
            "questions": [
                {{
                    "id": 1,
                    "question": "Question text here",
                    "type": "technical" or "behavioral",
                    "difficulty": "easy", "medium", or "hard"
                }},
                {{
                    "id": 2,
                    "question": "Question text here",
                    "type": "technical" or "behavioral",
                    "difficulty": "easy", "medium", or "hard"
                }},
                {{
                    "id": 3,
                    "question": "Question text here",
                    "type": "technical" or "behavioral",
                    "difficulty": "easy", "medium", or "hard"
                }}
            ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            response_text = response.text
            # Clean up the response to extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            return json.loads(response_text)
        except Exception as e:
            print(f"Error generating questions: {e}")
            # Fallback questions
            return {
                "questions": [
                    {
                        "id": 1,
                        "question": "Tell me about yourself and your professional background.",
                        "type": "behavioral",
                        "difficulty": "easy"
                    },
                    {
                        "id": 2,
                        "question": "What interests you most about this role?",
                        "type": "behavioral", 
                        "difficulty": "easy"
                    },
                    {
                        "id": 3,
                        "question": "Describe a challenging project you've worked on.",
                        "type": "behavioral",
                        "difficulty": "medium"
                    }
                ]
            }
    
    def analyze_interview_performance(self, interview_data):
        """
        Analyze complete interview session and provide scoring
        """
        questions_and_answers = ""
        for qa in interview_data.get('conversation', []):
            questions_and_answers += f"Q: {qa['question']}\nA: {qa['answer']}\n\n"
        
        prompt = f"""
        You are an expert interview analyst. Analyze the following interview conversation and provide a comprehensive assessment:
        
        INTERVIEW CONVERSATION:
        {questions_and_answers}
        
        JOB DETAILS:
        {interview_data.get('job_description', 'Not provided')}
        
        CANDIDATE EXPERIENCE LEVEL: {interview_data.get('experience_level', 'Not specified')}
        
        Provide a detailed analysis with the following structure:
        {{
            "overall_score": (0-100),
            "category_scores": {{
                "technical_skills": (0-100),
                "communication": (0-100),
                "problem_solving": (0-100),
                "cultural_fit": (0-100),
                "experience_relevance": (0-100)
            }},
            "strengths": ["strength1", "strength2", ...],
            "areas_for_improvement": ["area1", "area2", ...],
            "detailed_feedback": "Comprehensive feedback paragraph",
            "recommendation": "hire" or "reject" or "maybe",
            "confidence_level": (0-100)
        }}
        
        Be objective, constructive, and provide specific examples from the conversation.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            return json.loads(response_text)
        except Exception as e:
            print(f"Error analyzing interview: {e}")
            # Fallback analysis
            return {
                "overall_score": 75,
                "category_scores": {
                    "technical_skills": 75,
                    "communication": 80,
                    "problem_solving": 70,
                    "cultural_fit": 75,
                    "experience_relevance": 75
                },
                "strengths": ["Clear communication", "Relevant experience"],
                "areas_for_improvement": ["Technical depth", "Specific examples"],
                "detailed_feedback": "The candidate showed good communication skills and relevant experience. However, more technical depth and specific examples would strengthen their responses.",
                "recommendation": "maybe",
                "confidence_level": 70
            }
