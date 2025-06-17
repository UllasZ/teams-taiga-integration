import os

def create_folder(file_path) -> str:

    """Create the folder if it doesn't exist."""
    folder_path: str = os.path.dirname(file_path)

    try:
        os.makedirs(folder_path, exist_ok=True)
        return f"Directory created successfully: {file_path}"
    except OSError as e:
        raise IOError(f"Error creating directory {folder_path}: {e}") from e