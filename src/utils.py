import json
import mimetypes
import os
import requests
import time
from PyQt6.QtWidgets import QApplication


def get_clipboard_files():
    clipboard = QApplication.clipboard()
    mime_data = clipboard.mimeData()
    if mime_data.hasUrls():
        return [url.toLocalFile() for url in mime_data.urls() if os.path.exists(url.toLocalFile())]
    return []


def is_probably_text_file(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type and mime_type.startswith('text/')


def get_file_content(file_path, max_file_size):
    if os.path.getsize(file_path) > max_file_size:
        return f"File {file_path} is too large (>{max_file_size / 1024 / 1024:.2f} MB). Skipping.\n", 0

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            line_count = content.count('\n') + 1
            return content, line_count
    except UnicodeDecodeError:
        return f"File {file_path} is not a text file or uses an unsupported encoding. Skipping.\n", 0
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}\n", 0


def process_path(path, settings):
    content = ""
    total_files = 0
    total_lines = 0
    file_names = []
    if os.path.isfile(path):
        if settings.process_all_files or any(path.endswith(ext) for ext in settings.supported_extensions):
            file_content, line_count = get_file_content(path, settings.max_file_size * 1024 * 1024)
            content += f"File: {os.path.basename(path)}\n"
            content += f"Path: {path}\n"
            content += file_content
            content += "\n\n"
            total_files += 1
            total_lines += line_count
            file_names.append(os.path.basename(path))
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if settings.process_all_files or any(file_path.endswith(ext) for ext in settings.supported_extensions):
                    file_content, line_count = get_file_content(file_path, settings.max_file_size * 1024 * 1024)
                    content += f"File: {file}\n"
                    content += f"Path: {file_path}\n"
                    content += file_content
                    content += "\n\n"
                    total_files += 1
                    total_lines += line_count
                    file_names.append(file)
    return content, total_files, total_lines, file_names


def set_clipboard_content(content):
    clipboard = QApplication.clipboard()
    clipboard.setText(content)


def get_installed_ollama_models():
    try:
        response = requests.get('http://localhost:11434/api/tags')
        response.raise_for_status()
        models = response.json()['models']
        return [model['name'] for model in models]
    except requests.RequestException as e:
        print(f"Error fetching Ollama models: {e}")
        return []


def summarize_with_ollama(content, model, max_retries=3):
    prompt = f"Answer a title from the following content, just the title, nothing else:\n\n{content}\n\nAnswer a title from the content above, , just the title, nothing else."
    for attempt in range(max_retries):
        try:
            response = requests.post('http://localhost:11434/api/generate',
                                     json={'model': model, 'prompt': prompt},
                                     timeout=30, stream=True)  # Increased timeout to 30 seconds
            response.raise_for_status()

            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if 'response' in data:
                            full_response += data['response']
                        if data.get('done', False):
                            summary = ' '.join(full_response.strip().split()[:50])
                            return summary
                    except json.JSONDecodeError as json_err:
                        print(f"Error decoding JSON line: {line}")
                        print(f"Error details: {str(json_err)}")

            summary = ' '.join(full_response.strip().split()[:50])
            return summary if summary else "Unable to generate summary"

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                return f"Error: Unable to connect to Ollama after {max_retries} attempts."
        time.sleep(1)  # Wait before retrying
