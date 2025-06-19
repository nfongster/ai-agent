from pathlib import Path
import os, subprocess

# Max number of characters to read from a file
MAX_CHARS = 10000


def get_files_info(working_directory, directory=None):
    try:
        working_dir_path = os.path.abspath(working_directory)
        sub_dir_path = os.path.abspath(os.path.join(working_dir_path, directory))

        if not os.path.isdir(sub_dir_path):
            return f'Error: "{directory}" is not a directory'
        if not sub_dir_path.startswith(working_dir_path):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        return '\n'.join(
            [f'- {item}: \
file_size={os.path.getsize(os.path.join(sub_dir_path, item))} bytes, \
is_dir={os.path.isdir(os.path.join(sub_dir_path, item))}' 
            for item in os.listdir(sub_dir_path)]
        )
    
    except Exception as e:
        return f'Error: {e}'


def get_file_content(working_directory, file_path):
    try:
        working_dir_abs_path = os.path.abspath(working_directory)
        file_abs_path = os.path.abspath(os.path.join(working_dir_abs_path, file_path))

        if not os.path.isfile(file_abs_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        if not file_abs_path.startswith(working_dir_abs_path):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        with open(file_abs_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)
            if len(f.read()) > MAX_CHARS:
                file_content_string += f'...File "{file_abs_path}" truncated at 10000 characters'
            return file_content_string

    except Exception as e:
        return f'Error: {e}'


def write_file(working_directory, file_path, content):
    try:
        working_dir_abs_path = os.path.abspath(working_directory)
        file_abs_path = os.path.abspath(os.path.join(working_dir_abs_path, file_path))

        if not file_abs_path.startswith(working_dir_abs_path):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        if not os.path.exists(file_abs_path):
            os.makedirs(os.path.dirname(file_abs_path), exist_ok=True)
        
        with open(file_abs_path, 'w') as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        
    except Exception as e:
        return f'Error: {e}'


def run_python_file(working_directory, file_path):
    try:
        working_dir_abs_path = os.path.abspath(working_directory)
        file_abs_path = os.path.abspath(os.path.join(working_dir_abs_path, file_path))

        if not file_abs_path.startswith(working_dir_abs_path):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.exists(file_abs_path):
            return f'Error: File "{file_path}" not found.'
        _, extension = os.path.splitext(file_path)
        if extension != ".py":
            return f'Error: "{file_path}" is not a Python file.'
        
        process = subprocess.run([file_abs_path], timeout=30)
        stdout, stderr, code = process.stdout, process.stderr, process.check_returncode()
        if not stdout:
            return "No output produced."
        output = f'STDOUT:{stdout}, STDERR:{stderr}'
        if code != 0:
            output += f', Process exited with code {code}'
        return output
    
    except Exception as e:
        return f'Error: {e}'