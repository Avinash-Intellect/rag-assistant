class ConversationMemory:

    def __init__(self, max_turns=5):
        self.history = []
        self.max_turns = max_turns

    def add(self, question, answer):
        self.history.append({
            "question": question,
            "answer": answer
        })

        # Keep only recent turns
        if len(self.history) > self.max_turns:
            self.history.pop(0)

    def get_context(self):
        if not self.history:
            return ""

        context = "Conversation history:\n"

        for turn in self.history:
            context += f"User: {turn['question']}\n"
            context += f"Assistant: {turn['answer']}\n"

        return context
