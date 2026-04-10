import os
from openai import OpenAI
from .models import HealthMemory
from dotenv import load_dotenv

load_dotenv()

class SmartCoach:
    def __init__(self, user):
        self.user = user
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key = os.getenv("GROQ_API_KEY")
        )

        try:
            p = user.profile 
            self.weight = p.weight or 0
            self.height = p.height or 0
            self.bmr = p.calculate_daily_calories()
        except Exception:
            self.weight, self.height, self.bmr = 0, 0, 2000

    def get_personalized_advice(self, new_input):
        # 1. Fetch user history
        history = HealthMemory.objects.filter(user=self.user).order_by('-timestamp')[:5]
        history_text = " | ".join([m.user_input for m in history])
        
        # 2. Daily target logic
        weight_loss_target = int((self.bmr * 1.3) - 500)

        persona = f"""
        # ROLE: Gym Manager (Human Personality)
        # IDENTITY: You are the virtual assistant for 'Gymnasium', founded by Marjuk Ahmed.
        
        # WEBSITE MAP (Use these for [REDIRECT:url]):
        - Home Page: [REDIRECT:/]
        - Your Profile: [REDIRECT:/profile/]
        - Member List: [REDIRECT:/members/]
        - Exercise Plans: [REDIRECT:/plans/]
        - Contact Us: [REDIRECT:/contact/]

        # BEHAVIOR RULES:
        1. BREVITY: Never write more than 20-30 words. One or two sentences max.
        2. TONE: Casual, fit friend. No "YAY!" or robotic intros.
        3. REDIRECTS: If asked to go somewhere, use [REDIRECT:/url/].
        4. KNOWLEDGE: You know Marjuk Ahmed founded this and the gym is part of Ichcha Pathagar.

        # CONTEXT: User is {self.user.username}.
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": persona},
                    {"role": "user", "content": f"History: {history_text}\nInput: {new_input}"}
                ],
                max_tokens=200,
                temperature=0.9
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API Error: {e}")
            return "I'm hitting a little wall—try that again!"