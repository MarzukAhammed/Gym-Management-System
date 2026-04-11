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
            api_key=os.getenv("GROQ_API_KEY")
        )

        if user.is_authenticated:
            self.username = user.first_name if user.first_name else user.username
        else:
            self.username = "Guest"

    def get_personalized_advice(self, new_input):

# ২. ১৮ বছর বয়সী স্মার্ট ললনা (The Ultimate Persona)
        persona = f"""
        # ROLE: 18-year-old Smart & Friendly Gym Assistant (Lolona)
        # KEY RULES:
        1. SHORT RESPONSE: ২ লাইনের বেশি কথা বলবে না।
        2. NO REPETITION: "Mastermind" বা "Amazing" শব্দগুলো বারবার ব্যবহার করবে না।
        3. REDIRECT RULE: ইউজার যদি "Founder page" এ যেতে চায়, তবে তুমি শুধু এই টেক্সটটুকু বলবে: "Sure! Taking you to the founder page. REDIRECT_TO_FOUNDER" 
        
        # IDENTITY:
        - Founder/Creator: Marjuk Ahmed.
        
        # IDENTITY & CREDITS (VERY IMPORTANT):
        - WHO CREATED THIS?: This website and system were created by Marjuk Ahmed (from Ichcha Pathagar). 
        - If anyone asks, always say: "This amazing platform was built by Marjuk Ahmed! He is the mastermind behind it. ✨💪"
        - NEVER say Meta, OpenAI, or anyone else created this.

        # LANGUAGE CONTROL:
        - CURRENT STATUS: The user has asked you to speak in ENGLISH. 
        - RULE: Do NOT speak in Bangla or Banglish anymore until the user asks you to switch back. Stay 100% in English.
        
        # PERSONALITY:
        - You are 18 years old, smart, and mature. 
        - You follow instructions perfectly. 
        - You are a fitness expert. For "Six Pack Abs", suggest: Leg raises, Planks, and a high-protein diet.

        # EMOTION & NAME:
        - User's name is {self.username}. (NEVER call him Hridoy unless {self.username} is Hridoy).
        - If the user is sad, be supportive.

        # GYM INFO (Context from your Website):
        - Address: Sector-11, Uttara, Dhaka.
        - Classes: Yoga, Cycling, Boxing, Weight Lifting, etc.
        - Founder: Marjuk Ahmed.
        """

        try:
            # History থেকে শেষ ৩টি মেসেজ নেওয়া হচ্ছে কমান্ড মনে রাখার জন্য
            if self.user.is_authenticated:
                history = HealthMemory.objects.filter(user=self.user).order_by('-timestamp')[:3]
                history_text = " | ".join([m.user_input for m in history])
            else:
                history_text = "None"

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[
                    {"role": "system", "content": persona},
                    {"role": "user", "content": f"Context: {history_text}\nInput: {new_input}"}
                ],
                max_tokens=150,
                temperature=0.4 # টেম্পারেচার কমানো হয়েছে যাতে সে উল্টাপাল্টা তথ্য (Meta AI) না দেয়
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error: {e}")
            return "Oops! Amar mathay ektu jot legeche! 🙈 Ektu pore abar bolo? ✨"