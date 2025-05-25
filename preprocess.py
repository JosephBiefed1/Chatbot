import re
from ollama import Client

client = Client()  # Assumes Ollama is running locally

# === Define Keyword Lists ===
unrelated_keywords = [
    "auto gates", "auto gate", "auto queue", "off topic", "not allowed", "updates", "external link", "update", "$",
    "rain", "flood", "flooded", "debit", "atm", "larkin", "train", "hotel", "mid valley", "aeon", "sim card",
    "bukit indah", "dollar", 'grab', 'ksl', '#', '@', '^', 'pic', 'picture'
]

must_contain_keywords = [
    'bus', 'human', 'traffic', 'checkpoint', 'causeway', 'tuas', 'woodlands', 'sg', 'malaysia', 'singapore',
    'jam', 'min', 'egate', 'stairs', 'q'
]

question_keywords = [
    "question", "is it", "isit", "fast right", "slow right", "how", "hows", "?"
]

low_keywords = [
    "smooth", "moving fast", "not long queue", "no queue", "quite fast", "queue is ok", "queue is fine",
    "q is ok", "q is fine", "short", "fast", "is clear", "lots of buses", "many buses"
]

high_keywords = [
    "long q", "full", "rabak", "rabz", "jialat", "until the end", "end of bus terminal", "bus terminal",
    "not moving", "long", "waited", "bus not moving", "no bus", "waiting for bus"
]


# === Tier 1: Rule-based Classifier ===
def rule_based_classifier(message):
    try:
        msg = message.lower()

        if "@ct_img_bot" in msg:
            return ("Bot message", "Bot message", None)

        if any(kw in msg for kw in unrelated_keywords):
            return ("Not related", "Not related", None)

        if not any(kw in msg for kw in must_contain_keywords):
            return ("Not related", "Not related", None)

        if any(kw in msg for kw in question_keywords):
            return ("Not related", "Not related", None)

        high_count = sum(kw in msg for kw in high_keywords)
        low_count = sum(kw in msg for kw in low_keywords)

        if high_count >= 2:
            return ("High", infer_direction(msg), None)
        elif low_count >= 2:
            return ("Low", infer_direction(msg), None)
        else:
            return ("Uncertain", None, None)
    except Exception as e:
        return (message, "Error", str(e))

# === Direction Inference ===
def infer_direction(msg):
    if "to jb" in msg or "to malaysia" in msg or "entering malaysia" in msg:
        return "Singapore to Malaysia"
    elif "to sg" in msg or "back to sg" in msg or "to singapore" in msg or "entering singapore" in msg:
        return "Malaysia to Singapore"
    else:
        return "Not related"


# === Tier 2: LLM-based Classifier ===
def llm_classifier(message, model="myllama3:latest"):
    prompt = f'''
You are a customs message classifier.

Your job is to extract two things from each user message:
1. Crowd level: "High", "Low", "Not related", "Bot message"
2. Direction: "Singapore to Malaysia", "Malaysia to Singapore", or "Not related"

Rules:
- If message contains "@ct_img_bot", it is "Bot message"
- If message is a question or off-topic, it's "Not related"
- Many buses or short queue = Low
- Long wait or no buses = High

Format your answer exactly like this: ("Crowd Level", "Direction")

Message: "{message}"
'''
    response = client.generate(model=model, prompt=prompt)
    result = response['response'].strip()
    return eval(result) if result.startswith("(") and result.endswith(")") else ("Uncertain", "Not related")


# === Final Classification Wrapper ===
def classify_message(message):
    
    
    crowd, direction, error = rule_based_classifier(message)
    
    if error is not None:
        return (crowd, error, "Error") #returns the message and error
    if crowd == "Uncertain":
        crowd, direction = llm_classifier(message)
    return (crowd, direction, None)
