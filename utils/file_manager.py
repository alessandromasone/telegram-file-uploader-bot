import os

def save_uploaded_file(file_name, log_file='uploaded_files.txt'):
    with open(log_file, 'a') as file:
        file.write(file_name + '\n')

def load_uploaded_files(log_file='uploaded_files.txt'):
    if not os.path.exists(log_file):
        return set()
    with open(log_file, 'r') as file:
        return set(line.strip() for line in file)

def is_supported_file(file_path, uploaded_files, video_extensions, image_extensions):
    if not os.path.isfile(file_path):
        return False
    filename = os.path.basename(file_path)
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    return (filename not in uploaded_files) and (ext in video_extensions or ext in image_extensions)
