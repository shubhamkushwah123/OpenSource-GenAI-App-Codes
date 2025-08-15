# app.py
import os
from flask import Flask, render_template_string, request, jsonify, session
from flask_session import Session
from groq import Groq

# ------------------------------------------------------------------
# Flask & session setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")
app.config["SESSION_TYPE"] = "filesystem"     # server-side cookie store
Session(app)
# ------------------------------------------------------------------

# Groq client
client   = Groq(api_key=os.getenv("GROQ_API_KEY", "ENTER-YOUR-OWN-GROQ-KEY-HERE"))
MODEL_ID = os.getenv("GROQ_MODEL", "llama3-8b-8192")

def chat_history():
    """Create / return this browser tab’s conversation history."""
    if "history" not in session:
        session["history"] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
    return session["history"]

# ---------------------------- front page --------------------------
HTML = """
<!doctype html><html lang="en"><head>
<meta charset="utf-8"><title>Voice Chat (Groq)</title>
<style>
 body{font-family:sans-serif;margin:2rem;}
 #chat{border:1px solid #ddd;padding:1rem;height:60vh;overflow-y:auto;}
 .user{color:#0d6efd;margin:.5rem 0;}
 .bot {color:#198754;margin:.5rem 0;}
 #controls{display:flex;gap:.5rem;margin-top:1rem;}
 textarea{flex:1;padding:.5rem;} button{padding:.5rem 1rem;}
</style></head><body>
<h2>Voice-enabled Chat&nbsp;· Groq</h2>
<div id="chat"></div>

<div id="controls">
  <textarea id="text" rows="2" placeholder="Type or press mic…"></textarea>
  <button id="mic">🎤</button>
  <button id="send">Send</button>
</div>

<script>
const chat   = document.getElementById("chat");
const text   = document.getElementById("text");
const send   = document.getElementById("send");
const micBtn = document.getElementById("mic");

function add(role, msg){
  const div=document.createElement("div");
  div.className=role; div.textContent=(role==="user"?"> ":"")+msg;
  chat.appendChild(div); chat.scrollTop=chat.scrollHeight;
}

async function post(msg){
  add("user", msg); text.value="";
  add("bot","…"); const holder=chat.lastChild;
  try{
    const r = await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({message:msg})});
    const j = await r.json();
    holder.textContent = j.answer || j.error;
    // speak reply
    window.speechSynthesis.cancel();
    speechSynthesis.speak(new SpeechSynthesisUtterance(j.answer||j.error));
  }catch{ holder.textContent="⚠️ server error"; }
}

send.onclick = ()=>{ const v=text.value.trim(); if(v){ post(v); } };
text.addEventListener("keydown",e=>{ if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();send.click();}});

/* ---- Web-Speech mic ----- */
let recog, on = false;
if("webkitSpeechRecognition" in window){
  recog = new webkitSpeechRecognition();
  recog.lang="en-US"; recog.continuous=false; recog.interimResults=false;
  recog.onresult = e=>{ post(e.results[0][0].transcript); };
  recog.onerror  = e=>console.error(e);
}
micBtn.onclick=()=>{
  if(!recog){ alert("Browser doesn’t support Speech Recognition"); return;}
  if(!on){ recog.start(); micBtn.textContent="⏹️"; on=true; }
  else   { recog.stop();  micBtn.textContent="🎤"; on=false; }
};
</script></body></html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

# ----------------------------- chat API ---------------------------
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message","")
    history = chat_history()
    history.append({"role":"user","content":user_msg})

    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=history,
            temperature=0.8,
            max_tokens=1024,
            top_p=1,
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        reply = f"⚠️ Groq error: {e}"

    history.append({"role":"assistant","content":reply})
    session.modified = True
    return jsonify(answer=reply)

# ------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
