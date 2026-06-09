import os
import time
import sys
from groq import Groq

# We will drop your API key here when you are ready to test it
GROQ_API_KEY = "***ROTATED-REMOVED***"
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile" # This is a 70B model running at Groq speed

print(f"--- Booting Tester 2 (API: {MODEL}) ---")
history = []

try:
    while True:
        prompt = input("\nNymo: ")
        history.append({"role": "user", "content": prompt})

        print("\033[93m[Thinking...]\033[0m")
        
        # Start the clock
        start_time = time.time()
        
        try:
            response = client.chat.completions.create(
                messages=history,
                model=MODEL,
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = f"API Error: {e}"
            
        # Stop the clock
        end_time = time.time()
        latency = end_time - start_time

        history.append({"role": "assistant", "content": reply})

        print(f"\033[92m[Groq 70B] (Time: {latency:.2f} seconds)\033[0m")
        print(f"{reply}\n")

except KeyboardInterrupt:
    print("\n\n🛑 Tester 2 dismissed.")
    sys.exit()