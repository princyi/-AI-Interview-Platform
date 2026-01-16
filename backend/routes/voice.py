from flask import Blueprint, request, jsonify, send_file
from services.voice_service import VoiceService
import tempfile
import os

voice_bp = Blueprint('voice', __name__)
voice_service = VoiceService()

@voice_bp.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    """
    Convert uploaded audio file to text
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        audio_file.save(temp_file.name)
        temp_file.close()
        
        # Convert speech to text
        result = voice_service.speech_to_text_from_file(temp_file.name)
        
        # Cleanup
        voice_service.cleanup_temp_files(temp_file.name)
        
        if result['success']:
            return jsonify({'text': result['text']}), 200
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    """
    Convert text to speech audio file
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'en')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate speech audio file
        result = voice_service.text_to_speech_file(text, language)
        
        if result['success']:
            audio_file_path = result['audio_file']
            
            # Return the audio file
            response = send_file(
                audio_file_path,
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name='speech.mp3'
            )
            
            # Schedule cleanup after response
            @response.call_on_close
            def cleanup():
                voice_service.cleanup_temp_files(audio_file_path)
            
            return response
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/speak', methods=['POST'])
def speak_text():
    """
    Speak text using local TTS (for server-side testing)
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Speak using local TTS
        result = voice_service.text_to_speech_local(text)
        
        if result['success']:
            return jsonify({'message': 'Text spoken successfully'}), 200
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/listen', methods=['POST'])
def listen_microphone():
    """
    Listen to microphone and return transcribed text
    """
    try:
        data = request.get_json() or {}
        timeout = data.get('timeout', 10)
        phrase_time_limit = data.get('phrase_time_limit', None)
        
        # Listen and transcribe
        result = voice_service.speech_to_text(
            timeout=timeout, 
            phrase_time_limit=phrase_time_limit
        )
        
        if result['success']:
            return jsonify({'text': result['text']}), 200
        else:
            return jsonify({'error': result['error']}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
