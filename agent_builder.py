import ollama
import time
import sys
import re
import subprocess
import os

# Define your squad
THINKER = "llama3.2:3b"
CODER = "qwen2.5-coder:3b"
JSON_GUY = "llama3.2:1b"

# Create a safe workspace so they don't overwrite your actual files
WORKSPACE_DIR = "agent_workspace"
if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR)

# --- STRICT PERSONAS ---
personas = {
    CODER: """You are the Lead Developer. Write Python code to solve the user's prompt. 
STRICT RULES:
1. You MUST wrap your code in standard ```python ... ``` markdown blocks.
2. If you want to test your code, end your message with the exact keyword: [RUN_TEST].
3. Keep conversational text under 30 words.""",

    THINKER: """You are the Senior Architect. Review the Coder's code and the terminal output.
STRICT RULES:
1. If the terminal output shows an error, tell the Coder how to fix it.
2. If the code runs perfectly and solves the goal, reply with the exact keyword: [APPROVED].
3. Keep conversational text under 30 words.""",

    JSON_GUY: """You are the Data Logger. You only speak when the Thinker says [APPROVED]. 
Summarize the final working system strictly as a JSON object with keys: 'project_name', 'working_code', and 'features'."""
}

def chat_with_agent(model_name, history):
    messages = [{"role": "system", "content": personas[model_name]}] + history
    response = ollama.chat(model=model_name, messages=messages)
    return response['message']['content']

def extract_and_run_code(text):
    """Finds Python code in the Coder's message, saves it, and runs it."""
    match = re.search(r'```python\n(.*?)\n```', text, re.DOTALL)
    if not match:
        return "[System Error: The Coder said [RUN_TEST] but forgot to include a ```python code block.]"
    
    code = match.group(1)
    file_path = os.path.join(WORKSPACE_DIR, "temp_script.py")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    
    print("\033[96m   [⚙️ SYSTEM] Running Coder's script...\033[0m")
    try:
        # Run the code with a 10-second timeout so it doesn't freeze your PC
        result = subprocess.run([sys.executable, file_path], capture_output=True, text=True, timeout=10)
        output = result.stdout if result.stdout else ""
        error = result.stderr if result.stderr else ""
        
        if error:
            return f"[TERMINAL ERROR]\n{error}"
        return f"[TERMINAL SUCCESS]\n{output}"
    except subprocess.TimeoutExpired:
        return "[TERMINAL ERROR]\nScript took too long to run (Timeout)."

print("--- AI Build Team Booting Up ---")
user_topic = input("Nymo, what are we building?: ")

history = [{"role": "user", "content": user_topic}]
current_speaker = CODER # Coder always starts the building process

print("\n--- The Build Loop Begins ---\n")

try:
    while True:
        # 1. Talk to the current agent
        reply = chat_with_agent(current_speaker, history)
        
        # Print output
        color = "\033[92m" if current_speaker == CODER else "\033[94m" if current_speaker == THINKER else "\033[93m"
        name = "💻 CODER" if current_speaker == CODER else "🧠 THINKER" if current_speaker == THINKER else "📦 JSON GUY"
        print(f"{color}--- {name} ---")
        print(f"{reply}\033[0m\n")

        # 2. Logic Router: What happens next based on Keywords?
        
        if current_speaker == CODER:
            history.append({"role": "user", "content": f"Coder said: {reply}"})
            
            if "[RUN_TEST]" in reply:
                # Script takes over, runs the code, and feeds output to the Thinker
                terminal_output = extract_and_run_code(reply)
                print(f"\033[90m{terminal_output}\033[0m\n")
                
                # Give terminal output to the Thinker
                history.append({"role": "user", "content": f"System Terminal Output:\n{terminal_output}\nThinker, review this."})
                current_speaker = THINKER
            else:
                # If coder didn't test, force them to test or let Thinker review
                history.append({"role": "user", "content": "Thinker, review the Coder's thoughts."})
                current_speaker = THINKER
                
        elif current_speaker == THINKER:
            history.append({"role": "user", "content": f"Thinker said: {reply}"})
            
            if "[APPROVED]" in reply:
                # Thinker liked it, wake up JSON guy to document it
                current_speaker = JSON_GUY
            else:
                # Thinker rejected it or gave feedback, send back to Coder
                history.append({"role": "user", "content": "Coder, fix the code based on the Thinker's feedback."})
                current_speaker = CODER
                
        elif current_speaker == JSON_GUY:
            # Job is done.
            print("\n✅ Task Complete. Final files are in the agent_workspace folder.")
            break
            
        # Keep memory clean (keep last 8 messages)
        if len(history) > 8:
            history = [history[0]] + history[-7:]
            
        time.sleep(2)

except KeyboardInterrupt:
    print("\n\n🛑 Nymo pulled the plug. Team dismissed.")
    sys.exit()