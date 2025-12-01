from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
filename = os.path.dirname(__file__) + "/audio.m4a"

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)
completion = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
      {
        "role": "user",
        "content": "hola, dime un chiste sobre programadores"
      }
    ],
    temperature=1,
    max_completion_tokens=8192,
    top_p=1,
    reasoning_effort="medium",
    stream=True,
    stop=None
)

with open(filename, "rb") as file:
    transcription = client.audio.transcriptions.create(
      file=(filename, file.read()),
      model="whisper-large-v3",
      temperature=0,
      response_format="verbose_json",
    )
    print(transcription.text)
      

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
