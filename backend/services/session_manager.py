import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

class InterviewSessionManager:
    def __init__(self, sessions_dir="sessions"):
        self.sessions_dir = sessions_dir
        os.makedirs(self.sessions_dir, exist_ok=True)
    
    def create_session(self, candidate_name: str, job_title: str, resume_text: str = "", job_description: str = "") -> str:
        """
        Create a new interview session
        """
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "candidate_name": candidate_name,
            "job_title": job_title,
            "resume_text": resume_text,
            "job_description": job_description,
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "questions": [],
            "conversation": [],
            "current_question_index": 0,
            "analysis": None
        }
        
        self._save_session(session_id, session_data)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve session data
        """
        try:
            session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error retrieving session {session_id}: {e}")
        return None
    
    def update_session(self, session_id: str, updates: Dict) -> bool:
        """
        Update session data
        """
        try:
            session_data = self.get_session(session_id)
            if session_data:
                session_data.update(updates)
                session_data["updated_at"] = datetime.now().isoformat()
                self._save_session(session_id, session_data)
                return True
        except Exception as e:
            print(f"Error updating session {session_id}: {e}")
        return False
    
    def add_questions(self, session_id: str, questions: List[Dict]) -> bool:
        """
        Add generated questions to session
        """
        return self.update_session(session_id, {
            "questions": questions,
            "status": "questions_generated"
        })
    
    def add_qa_pair(self, session_id: str, question: str, answer: str, question_id: int = None) -> bool:
        """
        Add question-answer pair to conversation
        """
        session_data = self.get_session(session_id)
        if session_data:
            qa_pair = {
                "question_id": question_id,
                "question": question,
                "answer": answer,
                "timestamp": datetime.now().isoformat()
            }
            
            conversation = session_data.get("conversation", [])
            conversation.append(qa_pair)
            
            return self.update_session(session_id, {
                "conversation": conversation,
                "current_question_index": len(conversation),
                "status": "in_progress"
            })
        return False
    
    def complete_session(self, session_id: str, analysis: Dict) -> bool:
        """
        Mark session as completed with analysis
        """
        return self.update_session(session_id, {
            "status": "completed",
            "analysis": analysis,
            "completed_at": datetime.now().isoformat()
        })
    
    def get_next_question(self, session_id: str) -> Optional[Dict]:
        """
        Get the next question for the interview
        """
        session_data = self.get_session(session_id)
        if session_data:
            questions = session_data.get("questions", [])
            current_index = session_data.get("current_question_index", 0)
            
            if current_index < len(questions):
                return questions[current_index]
        return None
    
    def list_sessions(self, limit: int = 50) -> List[Dict]:
        """
        List all sessions with basic info
        """
        sessions = []
        try:
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith('.json'):
                    session_id = filename[:-5]  # Remove .json extension
                    session_data = self.get_session(session_id)
                    if session_data:
                        # Return basic info only
                        sessions.append({
                            "session_id": session_id,
                            "candidate_name": session_data.get("candidate_name"),
                            "job_title": session_data.get("job_title"),
                            "status": session_data.get("status"),
                            "created_at": session_data.get("created_at"),
                            "question_count": len(session_data.get("questions", [])),
                            "conversation_count": len(session_data.get("conversation", []))
                        })
            
            # Sort by creation time (newest first)
            sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return sessions[:limit]
            
        except Exception as e:
            print(f"Error listing sessions: {e}")
        return []
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        """
        try:
            session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
            if os.path.exists(session_file):
                os.remove(session_file)
                return True
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
        return False
    
    def _save_session(self, session_id: str, session_data: Dict):
        """
        Save session data to file
        """
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
