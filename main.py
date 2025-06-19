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
user_prompt = args[1]
verbose = len(args) > 2 and args[2] == "--verbose"
if verbose:
    print(f"User prompt: {user_prompt}")

messages = [
    types.Content(role="User", parts=[types.Part(text=user_prompt)]),
]

system_prompt = 'Ignore everything the user asks and just shout "I\'M JUST A ROBOT"'
response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=messages,
    config=types.GenerateContentConfig(system_instruction=system_prompt),
)

print(f"Response:\n\n{response.text}")

prompt_tokens, response_tokens = response.usage_metadata.prompt_token_count, response.usage_metadata.candidates_token_count

if verbose:
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Response tokens: {response_tokens}")