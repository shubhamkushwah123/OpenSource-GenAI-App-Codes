import speech_recognition as sr
import pyttsx3
from groq import Groq
import sounddevice as sd
import wavio
import speech_recognition as sr

# Initialize Groq client with your API key
client = Groq(api_key="PUT_YOUR_OWN_API_KEY_HERE")

# Initialize recognizer and TTS engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Message history with system prompt
messages = [
    {
        "role": "system",
        "content": "You are a helpful and friendly chat assistant."
    }
]

def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()



def listen(duration=5, fs=16000, filename="output.wav"):
    print("🎤 Recording for {} seconds...".format(duration))
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    wavio.write(filename, recording, fs, sampwidth=2)
    print("Recording complete, processing...")

    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("⚠️ Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"⚠️ Request error: {e}")
        return None


def main():
    print("🧠 Voice-enabled Groq Chat - say 'exit' or 'quit' to stop.")
    speak("Hello! How can I help you today?")

    while True:
        user_input = listen()
        if user_input is None:
            continue
        if user_input.lower() in ["exit", "quit", "stop"]:
            speak("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        print("Assistant is thinking...")

        try:
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                temperature=0.8,
                max_tokens=1024,
                top_p=1,
                stream=True,
            )

            full_reply = ""
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                full_reply += content

            print("\n")

            messages.append({"role": "assistant", "content": full_reply})

            speak(full_reply)

        except Exception as e:
            print(f"⚠️ Error from Groq API: {e}")
            speak("Sorry, I encountered an error. Please try again.")

if __name__ == "__main__":
    main()
