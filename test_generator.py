from retriever import retrieve_context
from generator import generate_answer

question = "Explain binary search"

context = retrieve_context(question)

answer = generate_answer(question, context)

print(answer)
# from google import genai
# import os
# from dotenv import load_dotenv

# load_dotenv()

# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# models = client.models.list()

# for model in models:
#     print(model.name)