from config import gemini_client

print("Fetching available models...")

# In the new SDK, just list them. 
# The 'supported_generation_methods' check is often not needed for a simple list,
# or the attribute name is different (e.g., 'supported_actions' in some versions).

try:
    for model in gemini_client.models.list():
        # print(model) # Uncomment this if you want to see all properties
        print(f"- {model.name}")
        
except Exception as e:
    print(f"Error listing models: {e}")