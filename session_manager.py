import uuid
from memory import ConversationMemory


class SessionManager:

    def __init__(self):
        self.sessions = {}

    def create_session(self):

        session_id = str(uuid.uuid4())

        self.sessions[session_id] = ConversationMemory()

        return session_id

    def get_memory(self, session_id):

        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationMemory()

        return self.sessions[session_id]
