from flask import Blueprint, request, jsonify
from services.gemini_service import GeminiService

ai_bp = Blueprint('ai', __name__)
gemini_service = GeminiService()

@ai_bp.route('/generate-questions', methods=['POST'])
def generate_questions():
    """
    Generate interview questions based on resume and job description
    """
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        job_description = data.get('job_description', '')
        experience_level = data.get('experience_level', 'intermediate')
        
        if not resume_text or not job_description:
            return jsonify({'error': 'Resume text and job description are required'}), 400
        
        questions = gemini_service.generate_interview_questions(
            resume_text, job_description, experience_level
        )
        
        return jsonify(questions), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/analyze-interview', methods=['POST'])
def analyze_interview():
    """
    Analyze complete interview and provide scoring
    """
    try:
        data = request.get_json()
        interview_data = data.get('interview_data', {})
        
        if not interview_data.get('conversation'):
            return jsonify({'error': 'Interview conversation data is required'}), 400
        
        analysis = gemini_service.analyze_interview_performance(interview_data)
        
        return jsonify(analysis), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
