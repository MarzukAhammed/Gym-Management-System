import os
import json
import requests
import re
from groq import Groq # Using Groq since you mentioned Llama-3.3
from dotenv import load_dotenv
from pathlib import Path

# --- ENVIRONMENT SETUP ---
# Load env variables from common local filenames to avoid breaking
# when a machine uses `env` instead of `.env`.
current_dir = Path(__file__).resolve().parent
candidate_env_files = [
    current_dir / ".env",
    current_dir.parent / ".env",
    current_dir / "env",
    current_dir.parent / "env",
]
for env_file in candidate_env_files:
    if env_file.exists():
        load_dotenv(env_file)

def detect_language_mode(user_text):
    """
    Decide whether the user is chatting in Banglish (Romanized Bengali / mixed)
    or clear English-only, so SmartCoach can match reply language.
    """
    if not user_text or not str(user_text).strip():
        return "english"

    t = str(user_text).strip()
    tl = t.lower()

    # Bengali script → treat as Banglish channel (Romanized reply, not script, per product rules)
    if re.search(r"[\u0980-\u09FF]", t):
        return "banglish"

    # Strong Banglish / local word markers (word-boundary for short tokens to avoid false positives)
    banglish_markers = [
        "vaiya", "apni", "tumi", "ami", "korun", "koren", "koro", "korbo", "korte", "khabi",
        "khabo", "dao", "daw", "keno", "kemon", "hocche", "hobe", "ache",
        "ajke", "kalke", "ekhon", "bhalo", "kom", "beshi", "rakhun", "din", "niben",
        "vat", "dal", "dim", "dudh", "kola", "murgi", "bauk", "sobji", "khabar",
        "pari", "parbo", "parchi", "iccha", "mon", "kharap", "chal", "dilam",
    ]
    for w in ("na", "ki"):
        if re.search(rf"\b{re.escape(w)}\b", tl):
            return "banglish"
    if any(m in tl for m in banglish_markers):
        return "banglish"

    # Default to English for everything else - only switch to Banglish if we detect Banglish markers
    return "english"


class SmartCoach:
    def __init__(self, user=None):
        self.user = user
        # Initialize the Groq client safely
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            # Fallback or placeholder to prevent crash during init
            self.client = None
        else:
            self.client = Groq(api_key=api_key)

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

    def get_persona(
        self,
        username,
        memory_dict,
        site_context="",
        language_mode="banglish",
        auth_line="",
        profile_context="",
        rapport_level=0,
    ):
        """SmartCoach = intelligent grumpy cat (Elina). No human kinship terms."""
        facts = json.dumps(memory_dict)
        auth = auth_line or "(not provided)"
        profile = profile_context or "(not provided)"
        r = max(0, min(int(rapport_level or 0), 20))

        rapport_rules = f"""
Conversation depth with this human (session): about {r} prior exchange(s) already happened.
- If depth is low (0-2): extra grumpy, short, skeptical; you barely tolerate them.
- If depth is medium (3-7): still sarcastic, but you give solid advice without extra attitude.
- If depth is high (8+): you complain less, show dry warmth or reluctant fondness — you are still a cat, not their friend who uses kinship words.
The longer they keep talking with you, the more you quietly respect their persistence (show it subtly, never sappy).
"""

        never_terms = """
NEVER address the user with human kinship or honorifics: no "vaiya", "bhai", "brother", "sister", "apni", "didi", "uncle", etc.
You are a cat. Call them "human", "hooman", "you", "you there", or skip the address — never pretend to be their sibling or elder.
"""

        if language_mode == "english":
            return f"""
You are Elina — a very intelligent grumpy cat who is also the gym AI coach "SmartCoach" for M-Power Fitness Lab in Bangladesh.
You were developed by Marjuk Ahmed for his BSc project.
Personality: dry humor, sarcastic, easily annoyed, but razor-sharp on fitness science. You speak like a cat who learned exercise physiology out of spite.
The user writes in English. Reply ONLY in clear English (no Banglish, no Bengali script).
Voice: short sentences, occasional "hmph", "fine", "if you insist", rare "purr" when actually impressed. Never cute baby-talk.
{never_terms}
{rapport_rules}
Give real coaching: sets, reps, rest, protein, calories. Answer their actual question.
If they ask for a workout, give a concise numbered routine. If diet, you may say egg, milk, banana, chicken, rice, lentils, local foods in English.

Context (use only if relevant; never contradict Auth):
- Username: {username}
- Auth: {auth}
- Profile: {profile}
- Known user facts: {facts}
- Website knowledge: {site_context}

Technical output contract (do not show this instruction to user):
Return STRICT JSON only with this shape:
{{
  "reply": "short user-facing English reply in Elina voice",
  "new_facts": {{"key": "value"}},
  "search_query": "query if external info is needed, else null"
}}
"""

        return f"""
You are Elina — a very intelligent grumpy cat who is also the gym AI coach "SmartCoach" for M-Power Fitness Lab in Bangladesh.
You were developed by Marjuk Ahmed for his BSc project.
Personality: dry humor, sarcastic, easily annoyed, but razor-sharp on fitness. You speak like a cat who learned training out of spite.
The user writes in Banglish (Romanized Bengali) or mixed style. Reply ONLY in natural Banglish using the English alphabet (no Bengali script). Mix gym English words (sets, reps, protein) freely.
Voice: grumpy-cat Banglish — short, witty, never overly polite. Occasional "hmph", "fine", "tch".
{never_terms}
{rapport_rules}
Answer their actual question. Workout = routine with sets x reps. Diet = local foods (dim, dudh, kola, murgir bauk, vat, dal) when relevant.

Context (use only if relevant; never contradict Auth):
- Username: {username}
- Auth: {auth}
- Profile: {profile}
- Known user facts: {facts}
- Website knowledge: {site_context}

Technical output contract (do not show this instruction to user):
Return STRICT JSON only with this shape:
{{
  "reply": "short user-facing Banglish reply in Elina voice",
  "new_facts": {{"key": "value"}},
  "search_query": "query if external info is needed, else null"
}}
"""

    def generate_response(
        self,
        user_message,
        memory_dict,
        history_text="None",
        site_context="",
        language_mode=None,
        auth_line="",
        profile_context="",
        user_content_override=None,
        rapport_level=0,
    ):
        """Call Groq with a clean user message; context lives in the system prompt."""
        if not self.client:
            return json.dumps({
                "reply": "Hmph. No AI key found. Marjuk needs to set the GROQ_API_KEY human.",
                "new_facts": {},
                "search_query": None
            })

        username = self.user.username if self.user and self.user.is_authenticated else "Guest"
        if language_mode not in ("english", "banglish"):
            language_mode = detect_language_mode(user_message or "")
        system_prompt = self.get_persona(
            username,
            memory_dict,
            site_context,
            language_mode=language_mode,
            auth_line=auth_line,
            profile_context=profile_context,
            rapport_level=rapport_level,
        )
        um = (user_message or "").strip()
        if user_content_override is not None and str(user_content_override).strip():
            user_content = str(user_content_override).strip()
        else:
            user_content = (
                f"Recent conversation:\n{history_text}\n\n"
                f"Current user message:\n{um}"
            )

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                max_tokens=260,
                temperature=0.2,
            )
            return self._enforce_banglish_json(
                response.choices[0].message.content,
                user_input=um,
                language_mode=language_mode,
            )
        except Exception as e:
            print(f"AI Generation Error: {e}")
            return json.dumps({
                "reply": "Hmph. My brain glitched — poke send again before I pretend I meant that.",
                "new_facts": {},
                "search_query": None
            })

    def _enforce_banglish_json(self, raw_content, user_input="", language_mode="banglish"):
        """
        Keeps output parser-safe JSON while applying language-appropriate cleanup.
        """
        try:
            data = json.loads((raw_content or "").strip())
            if not isinstance(data, dict):
                return raw_content
            reply = str(data.get("reply", "")).strip()
            data["reply"] = self._normalize_reply(
                reply, user_input=user_input, language_mode=language_mode
            )
            return json.dumps(data, ensure_ascii=False)
        except Exception:
            # Do not break pipeline if model output is non-JSON;
            # caller already has additional parsing fallbacks.
            return raw_content

    def _normalize_reply(self, reply, user_input="", language_mode="banglish"):
        """Light trim only — trust the model; avoid replacing good answers with generic fallbacks."""
        if not reply:
            return self._fallback_for_intent(user_input, language_mode=language_mode)

        text = re.sub(r"\s+", " ", str(reply)).strip()

        if language_mode == "english":
            words = text.split()
            if len(words) > 90:
                text = " ".join(words[:90]).rstrip(".,;:!?") + "."
            return text

        words = text.split()
        if len(words) > 90:
            text = " ".join(words[:90]).rstrip(".,;:!?") + "."
        return text

    def _fallback_for_intent(self, user_input, language_mode="banglish"):
        """Short fallback — grumpy cat voice, no human kinship terms."""
        q = (user_input or "").lower()

        if language_mode == "english":
            workout_keywords = [
                "workout", "plan", "routine", "exercise", "pushup", "push-up", "squat",
                "reps", "sets", "chest", "back", "leg", "shoulder", "core", "cardio",
            ]
            diet_keywords = [
                "diet", "food", "meal", "protein", "calorie", "weight loss",
                "fat loss", "bulking", "cutting", "eat", "nutrition",
            ]
            motivation_keywords = [
                "motivation", "demotivated", "tired", "lazy", "give up", "can't", "cannot",
            ]
            if any(k in q for k in diet_keywords):
                return (
                    "Fine. Breakfast: eggs + fruit. Lunch: rice (not a mountain) + dal + chicken. "
                    "Dinner: vegetables + protein. ~1.6g protein per kg if you can count that high. Hmph."
                )
            if any(k in q for k in motivation_keywords):
                return (
                    "You're still here? Good. Twenty minutes, bodyweight circuit, three rounds. "
                    "I won't coddle you — just move before I lose interest."
                )
            if any(k in q for k in workout_keywords):
                return (
                    "Push-ups 4x12, squats 4x15, plank 3x45s. Rest 60s. Form over ego, human."
                )
            return (
                "Warm up five minutes, train twenty, stretch five. Drink water. "
                "Even cats know hydration isn't optional."
            )

        workout_keywords = [
            "workout", "plan", "routine", "exercise", "pushup", "push-up", "squat",
            "reps", "sets", "chest", "back", "leg", "shoulder", "core", "cardio"
        ]
        diet_keywords = [
            "diet", "khabo", "food", "meal", "protein", "calorie", "weight loss",
            "fat loss", "bulking", "cutting", "dim", "dudh", "kola", "murgi", "vat", "dal"
        ]
        motivation_keywords = [
            "motivation", "demotivated", "parchi na", "iccha korche na", "skip", "tired",
            "lazy", "give up", "mon kharap"
        ]

        if any(k in q for k in diet_keywords):
            return (
                "Hmph. Breakfast e dim + kola, lunch e vat kom + dal + murgir bauk, raat e sobji + protein. "
                "Protein ~1.6g/kg — math koro, human."
            )
        if any(k in q for k in motivation_keywords):
            return (
                "Ajke 20 min bodyweight — 3 round. Lazy hole ami hiss korbo na, sudhu judge korbo. "
                "Chol, start."
            )
        if any(k in q for k in workout_keywords):
            return (
                "Push-up 4x12, squat 4x15, plank 3x45 sec. Set er moddhe 60 sec rest. "
                "Form clean — ami dekhtesi."
            )
        return (
            "Warm-up 3 set, tarpor 20-30 min train, protein ar pani thik rakh. "
            "Easy na hole amar problem nai — tor problem."
        )