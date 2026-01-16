from flask import Blueprint, request, jsonify
from services.session_manager import InterviewSessionManager
from services.gemini_service import GeminiService

sessions_bp = Blueprint('sessions', __name__)
session_manager = InterviewSessionManager()
gemini_service = GeminiService()

@sessions_bp.route('/create', methods=['POST'])
def create_session():
    """
    Create a new interview session
    """
    try:
        data = request.get_json()
        candidate_name = data.get('candidate_name', '')
        job_title = data.get('job_title', '')
        resume_text = data.get('resume_text', '')
        job_description = data.get('job_description', '')
        
        if not candidate_name or not job_title:
            return jsonify({'error': 'Candidate name and job title are required'}), 400
        
        session_id = session_manager.create_session(
            candidate_name, job_title, resume_text, job_description
        )
        
        return jsonify({'session_id': session_id}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sessions_bp.route('/<session_id>', methods=['GET'])
def get_session(session_id):
    """
    Get session details
    """
    try:
        session_data = session_manager.get_session(session_id)
        if session_data:
            return jsonify(session_data), 200
        else:
            return jsonify({'error': 'Session not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sessions_bp.route('/<session_id>/questions', methods=['POST'])
def generate_and_add_questions(session_id):
    """
    Generate questions using AI and add to session
    """
    try:
        session_data = session_manager.get_session(session_id)
        if not session_data:
            return jsonify({'error': 'Session not found'}), 404
        
        data = request.get_json() or {}
        experience_level = data.get('experience_level', 'intermediate')
        
        # Generate questions using Gemini
        questions_data = gemini_service.generate_interview_questions(
            session_data.get('resume_text', ''),
            session_data.get('job_description', ''),
            experience_level
        )
        
        questions = questions_data.get('questions', [])
        
        # Add questions to session
        success = session_manager.add_questions(session_id, questions)
        
        if success:
            return jsonify({'questions': questions}), 200
        else:
            return jsonify({'error': 'Failed to add questions to session'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sessions_bp.route('/<session_id>/next-question', methods=['GET'])
def get_next_question(session_id):
    """
    Get the next question for the interview
    """
    try:
        question = session_manager.get_next_question(session_id)
        if question:
            return jsonify(question), 200
        else:
            return jsonify({'message': 'No more questions'}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sessions_bp.route('/<session_id>/answer', methods=['POST'])
def add_answer(session_id):
    """
    Add answer to current question
    """
    try:
        data = request.get_json()
        question = data.get('question', '')
        answer = data.get('answer', '')
        question_id = data.get('question_id')
        
        if not question or not answer:
            return jsonify({'error': 'Question and answer are required'}), 400
        
        success = session_manager.add_qa_pair(session_id, question, answer, question_id)
        
        if success:
            return jsonify({'message': 'Answer added successfully'}), 200
        else:
            return jsonify({'error': 'Failed to add answer'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sessions_bp.route('/<session_id>/complete', methods=['POST'])
def complete_interview(session_id):
    """
    Complete interview and generate analysis
    """
    try:
        session_data = session_manager.get_session(session_id)
        if not session_data:
            return jsonify({'error': 'Session not found'}), 404
        
        # Generate analysis using Gemini
        analysis = gemini_service.analyze_interview_performance(session_data)
        
        # Mark session as completed
        success = session_manager.complete_session(session_id, analysis)
        
        if success:
            return jsonify(analysis), 200
        else:
            return jsonify({'error': 'Failed to complete session'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sessions_bp.route('/', methods=['GET'])
def list_sessions():
    """
    List all sessions
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        sessions = session_manager.list_sessions(limit)
        return jsonify({'sessions': sessions}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sessions_bp.route('/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    Delete a session
    """
    try:
        success = session_manager.delete_session(session_id)
        if success:
            return jsonify({'message': 'Session deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete session'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
