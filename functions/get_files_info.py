from pathlib import Path
import os

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
        print(f'Error: {e}')