import ollama
import time
import sys

# Define your squad
THINKER = "llama3.2:3b"
CODER = "qwen2.5-coder:3b"
JSON_GUY = "llama3.2:1b"

# Strict system prompts to enforce the 50-word limit and personalities
personas = {
    THINKER: "You are the Thinker. Analyze the previous message, brainstorm, and propose the next logical step. Speak casually to your team. STRICT RULE: Maximum 50 words.",
    CODER: "You are the Coder. Read the previous message and reply with technical logic, pseudocode, or architecture thoughts. Speak casually to your team. STRICT RULE: Maximum 50 words.",
    JSON_GUY: "You are the JSON Guy. Read the conversation and summarize the current state or extract data strictly as a small JSON object. STRICT RULE: Maximum 50 words."
}

def chat_with_agent(model_name, conversation_history):
    """Sends the rolling history to the specific model and gets a response."""
    # Inject the system prompt at the top of the context
    messages = [{"role": "system", "content": personas[model_name]}] + conversation_history
    
    response = ollama.chat(model=model_name, messages=messages)
    return response['message']['content']

print("--- The AI Roundtable is Booting Up ---")
print("Press [Ctrl + C] at any time to stop the loop.\n")

# Get the kick-off prompt from you
user_topic = input("Nymo, drop the starting prompt: ")

# The rolling memory (we keep it small so it stays fast)
history = [{"role": "user", "content": user_topic}]

# The turn order
turn_order = [
    ("🧠 THINKER", THINKER, "\033[94m"), # Blue text
    ("💻 CODER", CODER, "\033[92m"),    # Green text
    ("📦 JSON GUY", JSON_GUY, "\033[93m") # Yellow text
]

print("\n--- The Loop Begins ---\n")

try:
    while True:
        for name, model, color in turn_order:
            # 1. Get the response (Force retry if it returns blank)
            reply = ""
            retries = 0
            while not reply.strip() and retries < 3:
                reply = chat_with_agent(model, history)
                retries += 1
                if not reply.strip():
                    print(f"\033[91m   [!] {name} stayed silent. Kicking it to try again ({retries}/3)...\033[0m")
                    time.sleep(1)
            
            # If it still fails after 3 tries, insert a fallback so it doesn't break history
            if not reply.strip():
                reply = "[System: The agent failed to respond.]"
            
            # 2. Print it to the terminal with color formatting
            print(f"{color}--- {name} ---")
            print(f"{reply}\033[0m\n")
            
            # 3. Add to history so the next guy can read it
            history.append({"role": "user", "content": f"{name.strip()} said: {reply}"})
            
            # 4. Keep memory from exploding (keep last 5 messages only)
            if len(history) > 6:
                history = [history[0]] + history[-5:]
            
            # Pause for 2 seconds so you can actually read it
            time.sleep(2)

except KeyboardInterrupt:
    print("\n\n🛑 Nymo pulled the plug. Roundtable dismissed.")
    sys.exit()