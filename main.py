import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions import get_files_info as tools


WORKING_DIR = "./calculator"


def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_name, args = function_call_part.name, function_call_part.args
    args["working_directory"] = WORKING_DIR
    function_result = ""
    match function_name:
        case "get_files_info":
            function_result = tools.get_files_info(**args)
        case "get_file_content":
            function_result = tools.get_file_content(**args)
        case "write_file":
            function_result = tools.write_file(**args)
        case "run_python_file":
            function_result = tools.run_python_file(**args)
        case _:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_name,
                        response={"error": f"Unknown function: {function_name}"},
                    )
                ],
            )
    
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )


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

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description=f"Gets the contents of a specified file in the specified working directory, limited to {tools.MAX_CHARS} characters.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file whose contents will be returned."
            )
        }
    )
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description=f"Runs a specified Python file.  Returns an error if the file is not a Python file.  Note that this may require permissions.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file."
            )
        }
    )
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description=f"Writes specified content to a file, creating a new file if it does not exist.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file."
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to be written to the file."
            )
        }
    )
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file
    ]
)

system_prompt = f"""
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan.  If the prompt requires you to run and/or modify files, start by looking in the pkg folder.

You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

# system_prompt = """
# Write a sentence that has the same number of words as my prompt, such that each word is different than the prompt word, but has the same first letter as the corresponding prompt word.
# """

iter = 0
while iter < 20:

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )

    for candidate in response.candidates:
        messages.append(candidate.content)

    if response.function_calls:
        for function_call_part in response.function_calls:
            print(f"Calling function: {function_call_part.name}({function_call_part.args})")
            content = call_function(function_call_part, verbose)
            messages.append(content)
            content_response = content.parts[0].function_response.response
            if not content_response:
                raise Exception("Function did not have a response!")
            elif verbose:
                print(f"-> {content_response}")
    else:  # If no function was called, print final response and break loop
        print(response.text)
        break

    prompt_tokens, response_tokens = response.usage_metadata.prompt_token_count, response.usage_metadata.candidates_token_count

    if verbose:
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens: {response_tokens}")

    iter += 1