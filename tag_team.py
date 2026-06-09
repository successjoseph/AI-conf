import ollama
import time
import sys
import re
import subprocess
import os

# --- THE TAG TEAM ---
LEAD_DEV = "llama3.1:8b"
ARCHIVIST = "llama3.2:1b"

WORKSPACE_DIR = "agent_workspace"
if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR)

# --- PERSONAS ---
personas = {
    LEAD_DEV: f"""You are the Elite Solo Developer. Write Python code to solve the user's prompt only, no conversational text.
Your current working directory is: {os.getcwd()}
STRICT RULES:
1. You MUST wrap your code in standard ```python ... ``` markdown blocks.
2. use input() it is absolutely necessary.
3. If you want to test your code, end your message with the exact keyword: [RUN_TEST].""",

    ARCHIVIST: """You are the System Archivist. You only speak when the user approves working code.
Look at the conversation and determine what the code does.
STRICT RULES:
1. Invent a short, unique filename for this script (e.g., git_parser.py, file_reader.py).
2. You MUST output ONLY the filename using this exact format: [SAVE_AS: your_custom_name.py]
3. Do not include any other conversational text."""
}

def get_existing_files():
    return [f for f in os.listdir(WORKSPACE_DIR) if f.endswith('.py')]

def chat_with_agent(model_name, history, color):
    """Streams the AI's response to the terminal word-by-word like a typewriter."""
    messages = [{"role": "system", "content": personas[model_name]}] + history
    response = ollama.chat(model=model_name, messages=messages, stream=True)
    
    full_reply = ""
    print(color, end="") # Turn on agent color
    
    for chunk in response:
        word = chunk['message']['content']
        print(word, end="", flush=True) # Typewriter effect
        full_reply += word
        
    print("\033[0m\n") # Turn off color
    return full_reply

def extract_and_run_code(text):
    match = re.search(r'(?:```python)\s(.*?)(?:```|\[RUN_TEST\]|$)', text, re.DOTALL | re.IGNORECASE)
    if not match:
        return "[System Error: The Coder said [RUN_TEST] but forgot to include a ```python code block.]"
    
    # Extract and aggressively sanitize the code
    code = match.group(1).strip()
    code = re.sub(r'\[RUN_TEST\]', '', code, flags=re.IGNORECASE) # Scrub stray keywords
    code = code.replace("```", "").strip() # Scrub stray backticks
    
    file_path = os.path.abspath(os.path.join(WORKSPACE_DIR, "temp_script.py"))
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    
    print("\033[96m   [⚙️ SYSTEM] Popping open a new terminal for Nymo to test it...\033[0m")
    
    # Launch a new visible CMD window with foolproof Windows quote formatting
    cmd_string = f'start "AI_Test" /wait cmd /c ""{sys.executable}" "{file_path}" & echo. & pause"'
    subprocess.run(cmd_string, shell=True)
    
    # The script pauses here until the external CMD window is closed.
    print("\n\033[95m   [👨‍⚖️ NYMO'S VERDICT]\033[0m")
    verdict = input("Did it work exactly as expected? (y/n): ").strip().lower()
    
    if verdict == 'y':
        return "[NYMO_APPROVED]\nThe code ran perfectly."
    else:
        feedback = input("What was the error, or what needs changing?: ")
        return f"[NYMO_REJECTED]\nNymo's feedback: {feedback}\nCoder, fix this immediately."
    
print(f"--- Booting Tag Team (Lead: {LEAD_DEV} | Archivist: {ARCHIVIST}) ---")
user_topic = input("\nNymo, what are we building?: ")

history = [{"role": "user", "content": user_topic}]
current_speaker = LEAD_DEV

print("\n--- The Build Loop Begins ---\n")

try:
    while True:
        color = "\033[94m" if current_speaker == LEAD_DEV else "\033[93m"
        name = "🧠 LEAD DEV" if current_speaker == LEAD_DEV else "🗄️ ARCHIVIST"

        print(f"{color}--- {name} ---")
        reply = chat_with_agent(current_speaker, history, color)

        if not reply.strip():
            reply = "[System Error: Agent stayed silent.]"

        # --- LOGIC ROUTER ---
        if current_speaker == LEAD_DEV:
            history.append({"role": "user", "content": f"Lead Dev said: {reply}"})
            
            if "[RUN_TEST]" in reply.upper():
                terminal_output = extract_and_run_code(reply)
                print(f"\033[90m{terminal_output}\033[0m\n")
                
                if "[NYMO_APPROVED]" in terminal_output:
                    existing = get_existing_files()
                    history.append({"role": "user", "content": f"Nymo approved the code! Archivist, existing files in our workspace: {existing}. Invent a unique, descriptive name based on the code's function and output ONLY [SAVE_AS: your_chosen_name.py]."})
                    current_speaker = ARCHIVIST
                else:
                    history.append({"role": "user", "content": f"System/Nymo Feedback:\n{terminal_output}\nFix the code and end with [RUN_TEST]."})
            else:
                history.append({"role": "user", "content": "You forgot the [RUN_TEST] tag. Please test your code."})
                
        elif current_speaker == ARCHIVIST:
            match = re.search(r'\[SAVE_AS:\s*(.+?\.py)\]', reply, re.IGNORECASE)
            if match:
                raw_filename = match.group(1).strip()
                clean_filename = re.sub(r'[^a-zA-Z0-9_.]', '_', raw_filename).replace('_.py', '.py')
                
                old_path = os.path.join(WORKSPACE_DIR, "temp_script.py")
                new_path = os.path.join(WORKSPACE_DIR, clean_filename)
                
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                
                print(f"\n\033[92m✅ Task Complete! Code perfectly archived as: {clean_filename}\033[0m")
                break
            else:
                history.append({"role": "user", "content": "You forgot the [SAVE_AS: filename.py] tag. Try again."})
            
        # Memory limit to keep context fast
        if len(history) > 8:
            history = [history[0]] + history[-7:]

except KeyboardInterrupt:
    print("\n\n🛑 Nymo pulled the plug. Team dismissed.")
    sys.exit()