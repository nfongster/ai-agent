import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

args = sys.argv
if len(args) < 2:
    sys.exit("Too few args were provided.  Please provide a prompt, in quotes, as an argument.")
prompt = args[1]

messages = [
    types.Content(role="User", parts=[types.Part(text=user_prompt)]),
]

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=messages,
)

print(f"Response:\n\n{response.text}")

prompt_tokens, response_tokens = response.usage_metadata.prompt_token_count, response.usage_metadata.candidates_token_count
print(f"Prompt tokens: {prompt_tokens}")
print(f"Response tokens: {response_tokens}")