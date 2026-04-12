import os
import json
import requests
from groq import Groq # Using Groq since you mentioned Llama-3.3
from dotenv import load_dotenv

load_dotenv()

class SmartCoach:
    def __init__(self, user=None):
        self.user = user
        # Initialize the Groq client here
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def search_internet(self, query):
        """Allows the AI to find answers using environment variables."""
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        
        # Retrieve the key safely from the environment
        api_key = os.getenv('SERPER_API_KEY')
        
        if not api_key:
            print("Error: SERPER_API_KEY not found in environment.")
            return None

        headers = {
            'X-API-KEY': api_key, 
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, data=payload)
        return response.json()

    def get_persona(self, username, memory_dict):
        """Generates the persona instructions."""
        facts = json.dumps(memory_dict)
        return f"""
        # ROLE: Super-Intelligent Gym Assistant (Lolona).
        # CONTEXT: User is {username}. Known user facts: {facts}.
        
        # BEHAVIOR:
        1. Speak only English. Be witty, smart, and concise (1-2 sentences).
        2. PERSONALIZATION: Use 'Known user facts' to customize advice. 
        3. SEARCH: If you don't know an answer, you MUST use the search tool.
        
        # OUTPUT FORMAT (STRICT JSON ONLY):
        {{
            "reply": "Your message to user",
            "new_facts": {{"key": "value"}}, 
            "search_query": "query if info is missing, else null"
        }}
        """

    def generate_response(self, new_input, memory_dict, history_text="None"):
        """The brain that calls the AI model."""
        username = self.user.username if self.user and self.user.is_authenticated else "Guest"
        persona = self.get_persona(username, memory_dict)

        try:
            # Using the Groq client correctly
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[
                    {"role": "system", "content": persona},
                    {"role": "user", "content": f"Context: {history_text}\nInput: {new_input}"}
                ],
                max_tokens=150,
                temperature=0.4 
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI Generation Error: {e}")
            return json.dumps({
                "reply": "Oops! My brain is a bit tangled! 🙈 Try again? ✨",
                "new_facts": {},
                "search_query": None
            })