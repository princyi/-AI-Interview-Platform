import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import io
import tempfile
import os
from threading import Thread
import queue

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.tts_engine = None
        
        # Try to initialize microphone (may fail if PyAudio not installed)
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
        except Exception as e:
            print(f"Warning: Microphone initialization failed: {e}")
            print("Voice recording from microphone will not be available")
        
        # Try to initialize text-to-speech engine
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Speech rate
            self.tts_engine.setProperty('volume', 0.9)  # Volume level
        except Exception as e:
            print(f"Warning: TTS engine initialization failed: {e}")
            print("Local text-to-speech will not be available")
    
    def speech_to_text(self, audio_data=None, timeout=10, phrase_time_limit=None):
        """
        Convert speech to text using microphone input
        """
        if self.microphone is None:
            return {"success": False, "error": "Microphone not available. Please install PyAudio."}
        
        try:
            if audio_data is None:
                # Listen from microphone
                with self.microphone as source:
                    print("Listening...")
                    audio_data = self.recognizer.listen(
                        source, 
                        timeout=timeout, 
                        phrase_time_limit=phrase_time_limit
                    )
            
            # Convert speech to text
            text = self.recognizer.recognize_google(audio_data)
            return {"success": True, "text": text}
            
        except sr.WaitTimeoutError:
            return {"success": False, "error": "Listening timeout"}
        except sr.UnknownValueError:
            return {"success": False, "error": "Could not understand audio"}
        except sr.RequestError as e:
            return {"success": False, "error": f"Error with speech recognition service: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {e}"}
    
    def text_to_speech_file(self, text, language='en'):
        """
        Convert text to speech and return audio file path
        """
        try:
            # Create temporary file for audio
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            
            # Generate speech using gTTS
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(temp_file.name)
            
            return {"success": True, "audio_file": temp_file.name}
            
        except Exception as e:
            return {"success": False, "error": f"Error generating speech: {e}"}
    
    def text_to_speech_local(self, text):
        """
        Convert text to speech using local TTS engine (pyttsx3)
        """
        if self.tts_engine is None:
            return {"success": False, "error": "Local TTS engine not available"}
        
        try:
            # Use pyttsx3 for immediate speech output
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return {"success": True, "message": "Speech played successfully"}
            
        except Exception as e:
            return {"success": False, "error": f"Error with local TTS: {e}"}
    
    def speech_to_text_from_file(self, audio_file_path):
        """
        Convert audio file to text
        """
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                return {"success": True, "text": text}
                
        except sr.UnknownValueError:
            return {"success": False, "error": "Could not understand audio from file"}
        except sr.RequestError as e:
            return {"success": False, "error": f"Error with speech recognition service: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Error processing audio file: {e}"}
    
    def cleanup_temp_files(self, file_path):
        """
        Clean up temporary audio files
        """
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                return True
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {e}")
        return False
