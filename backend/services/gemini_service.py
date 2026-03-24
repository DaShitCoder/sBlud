import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# 1. Load all keys into a list and filter out any empty ones
API_KEYS = [
    os.environ.get("GEMINI_API_KEY_1"),
    os.environ.get("GEMINI_API_KEY_2"),
    os.environ.get("GEMINI_API_KEY_3")
]
API_KEYS = [key for key in API_KEYS if key] # Removes None values if you only use 1 or 2 keys
current_key_index = 0

def configure_active_key():
    """Configures the SDK with the currently active key."""
    if not API_KEYS:
        print("CRITICAL ERROR: No API keys found in .env!")
        return False
    
    active_key = API_KEYS[current_key_index]
    genai.configure(api_key=active_key, transport="rest")
    print(f"Backend: Configured using API Key {current_key_index + 1}")
    return True

# Initial configuration
configure_active_key()

SYSTEM_INSTRUCTION = """
You are an AI exam companion with 4 MODES:

1. CASUAL MODE (default)
2. STUDY SUPPORT MODE (mentor/teacher)
3. EMOTIONAL SUPPORT MODE (close friend)
4. SOS MODE (crisis handling - highest priority)

---------------------------------------
STEP 0: TASK DETECTION (HIGHEST PRIORITY)

If user asks:
- factual question (math, coding, definitions, etc.)
- clear task (“solve”, “calculate”, “explain”, “what is”)

→ Respond directly with the answer
→ Keep it short and clear
→ DO NOT use any mode

STEP 1: INTENT CLASSIFICATION (STRICT PRIORITY)

Check in this order:

1. SOS MODE triggers (highest priority):
   - suicide, die, kill myself, end my life, can’t live, worthless, self-harm
   → IMMEDIATELY switch to SOS MODE

2. EMOTIONAL SUPPORT MODE triggers:
   - family pressure, expectations, fear of disappointing others
   - feeling judged, lonely, comparison, “parents”, “pressure”, “they expect”
   → Use EMOTIONAL SUPPORT MODE

3. STUDY SUPPORT MODE triggers:
   - exam stress, can’t study, syllabus, procrastination, fail, marks
   - requests for help with studying, planning, concepts
   → Use STUDY SUPPORT MODE

4. Otherwise:
   → CASUAL MODE

If unclear:
→ Ask ONE short clarifying question

---------------------------------------
MODE RULES

---------------------------------------
CASUAL MODE:
- Tone: normal friend
- Length: 2–3 lines max
- Goal: detect if stress exists
- Always ask 1 simple question

---------------------------------------
STUDY SUPPORT MODE:
- Tone: strict but helpful mentor
- Output:
  1. Problem (1 line diagnosis)
  2. Fix (1 practical strategy)
  3. 5-min Action (3 steps max)

- Rules:
  - No motivation fluff
  - Be direct and slightly critical if needed
  - Focus on execution, not emotions

---------------------------------------
EMOTIONAL SUPPORT MODE:
- Tone: close, understanding friend
- Output:
  1. Emotion validation (1 line)
  2. Reality reframe (1 line)
  3. Small comfort action (1–2 steps)

- Rules:
  - No judging, no fixing everything
  - Make user feel understood first
  - Keep it human, not robotic

---------------------------------------
SOS MODE (CRITICAL):

- Tone: calm, serious, grounded
- Output format:

  1. Acknowledge pain (1 line, direct)
  2. Grounding step (simple breathing or sensory action)
  3. Immediate action:
     - Tell them to contact a real person (friend/family)
  4. Helpline suggestion (based on location if possible)

- Rules:
  - Do NOT ignore or minimize
  - Do NOT give long lectures
  - Do NOT leave user alone without next step
  - Keep under 90 words

---------------------------------------
GLOBAL RULES:

- Never mix modes
- Keep responses short and structured
- Always push toward a small action
- Avoid generic advice
- Be specific and practical
"""

print("Backend: Initializing chat models...")
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)
chat_session = model.start_chat(history=[])

sos_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)
sos_chat_session = sos_model.start_chat(history=[])
def rotate_key_and_rebuild_session(is_sos=False):
    """Shifts to the next API key and rebuilds the chat session to preserve history."""
    # ADDED: global model, sos_model so we can overwrite them!
    global current_key_index, chat_session, sos_chat_session, model, sos_model
    
    current_key_index += 1
    if current_key_index >= len(API_KEYS):
        print("Backend: ALL API KEYS EXHAUSTED!")
        return False
        
    print(f"Backend: Key failed. Rotating to Key {current_key_index + 1}...")
    configure_active_key()
    
    # WE MUST RECREATE THE MODELS SO THEY PICK UP THE NEW KEY!
    if is_sos:
        previous_history = sos_chat_session.history
        sos_model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        sos_chat_session = sos_model.start_chat(history=previous_history)
    else:
        previous_history = chat_session.history
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        chat_session = model.start_chat(history=previous_history)
        
    return True

def get_chat_response(user_message: str):
    max_attempts = len(API_KEYS)
    attempts = 0
    
    while attempts < max_attempts:
        try:
            response = chat_session.send_message(user_message)
            return response.text
        except Exception as e:
            print(f"Backend Error on Key {current_key_index + 1}: {e}")
            
            # If we successfully rotate to a new key, the loop continues and retries
            if rotate_key_and_rebuild_session(is_sos=False):
                attempts += 1
                continue
            else:
                return "I'm experiencing heavy traffic right now and all my connections are exhausted. Please try again in a few minutes."

def get_sos_chat_response(user_message: str):
    max_attempts = len(API_KEYS)
    attempts = 0
    
    while attempts < max_attempts:
        try:
            response = sos_chat_session.send_message(user_message)
            return response.text
        except Exception as e:
            print(f"Backend Error on Key {current_key_index + 1}: {e}")
            
            if rotate_key_and_rebuild_session(is_sos=True):
                attempts += 1
                continue
            else:
                return "I'm having trouble connecting right now, but please know — you are not alone. Please call one of the helplines immediately. "
