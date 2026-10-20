
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY was not found in .env")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key,
)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: Hello, the model is working.",
        }
    ],
    max_tokens=50,
)

print(response.choices[0].message.content)
