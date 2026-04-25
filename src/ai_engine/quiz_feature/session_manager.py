import uuid
from typing import Dict, Optional, List, Set, Any


class QuizSession:
    def __init__(self, session_id: str, bank_id: str, user_id: str):
        self.session_id = session_id
        self.bank_id = bank_id
        self.user_id = user_id
        self.current_index = 0

        self.history: List[Dict[str, Any]] = []

        self.asked_questions: Set[str] = set()
        self.last_difficulty: str = "medium"


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, QuizSession] = {}

    def create_session(self, bank_id: str, user_id: str) -> QuizSession:
        session_id = str(uuid.uuid4())
        session = QuizSession(session_id, bank_id, user_id)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[QuizSession]:
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]


session_manager = SessionManager()
