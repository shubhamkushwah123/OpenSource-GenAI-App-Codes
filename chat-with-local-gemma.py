import requests
import os

# Base Ollama OpenAI-compatible endpoint (no /v1/chat/completions here)
BASE_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:11434")
MODEL    = os.getenv("LOCAL_MODEL", "gemma:2b")

# Initialize chat history
messages = [
    {"role": "system", "content": "You are a helpful assistant powered by Gemma 2B running locally."}
]

def chat_with_llm(user_input):
    messages.append({"role": "user", "content": user_input})

    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": MODEL,
                "messages": messages,
                "temperature": 0.7,
                "stream": False
            },
            timeout=60,
        )
        response.raise_for_status()  # catch HTTP errors
        data = response.json()
        reply = data["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"⚠️ Error: {e}"

def main():
    print("💬 Chat with Gemma 2B (locally via Ollama). Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        reply = chat_with_llm(user_input)
        print(f"Gemma: {reply}\n")

if __name__ == "__main__":
    main()
