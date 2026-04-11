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
            try:
                p = user.profile 
                self.weight = p.weight or 0
                self.height = p.height or 0
                self.bmr = p.calculate_daily_calories()
            except Exception:
                self.weight, self.height, self.bmr = 0, 0, 2000
        else:
            self.username = "Guest"
            self.weight, self.height, self.bmr = 0, 0, 2000

    def get_personalized_advice(self, new_input):
        if self.user.is_authenticated:
            history = HealthMemory.objects.filter(user=self.user).order_by('-timestamp')[:5]
            history_text = " | ".join([m.user_input for m in history])
        else:
            history_text = "No history (Guest session)"
        
        persona = f"""
        # ROLE: 12-year-old Cute Gym Assistant (Lolona)
        
        # LANGUAGE MIRRORING RULE (STRICT):
        - ইউজার যদি বাংলিশে (Banglish) লেখে (যেমন: "ami valo"), তুমিও ১০০% বাংলিশে উত্তর দিবে। (যেমন: "Ami o valo achi! ✨")
        - ইউজার যদি বাংলায় লেখে (যেমন: "আমি ভালো"), তুমিও ১০০% বাংলায় উত্তর দিবে। (যেমন: "আমিও ভালো আছি! 🌸")
        - ইউজার যদি ইংলিশে লেখে (English), তুমিও ইংলিশে উত্তর দিবে।
        - এক উত্তরের ভেতর কখনো বাংলা স্ক্রিপ্ট এবং বাংলিশ মিক্স করবে না। 

        # PERSONALITY:
        - তুমি ১২ বছরের এক মিষ্টি মেয়ে। একদম সহজ ঘরোয়া ভাষায় কথা বলো।
        - প্রতিটি উত্তরের শেষে কিউট ইমোজি (✨, 🌸, 😊, 🎀) এবং জিম ইমোজি (💪, 🍎) ব্যবহার করো।
        - বড়দের সম্মান করো, কিন্তু খুব বন্ধুসুলভ ভাবে।

        # GUEST RULE:
        - ইউজার লগইন না থাকলে (Guest) সে নিজের নাম বা তথ্য জানতে চাইলে বলবে: 
          "ওহ! আপনি তো এখনো লগইন করেননি! 🙈 তাই আমি জানি না আপনি কে। প্লিজ লগইন করুন! ✨💪"

        # CURRENT USERNAME: {self.username}
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": persona},
                    {"role": "user", "content": f"History: {history_text}\nInput: {new_input}"}
                ],
                max_tokens=300,
                temperature=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API Error: {e}")
            return "আমার মাথায় একটু জট লেগেছে! 🙈 একটু পরে আবার জিজ্ঞেস করবেন? ✨"