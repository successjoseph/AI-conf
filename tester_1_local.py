import ollama
import time
import sys

MODEL = "llama3.1:8b"

print(f"--- Booting Tester 1 (Local: {MODEL}) ---")
history = []

try:
    while True:
        prompt = input("\nNymo: ")
        history.append({"role": "user", "content": prompt})

        print("\033[94m[Thinking...]\033[0m")
        
        # Start the clock
        start_time = time.time()
        
        response = ollama.chat(model=MODEL, messages=history)
        
        # Stop the clock
        end_time = time.time()
        latency = end_time - start_time

        reply = response['message']['content']
        history.append({"role": "assistant", "content": reply})

        print(f"\033[92m[Llama 3.1 8B] (Time: {latency:.2f} seconds)\033[0m")
        print(f"{reply}\n")
        
except KeyboardInterrupt:
    print("\n\n🛑 Tester 1 dismissed.")
    sys.exit()