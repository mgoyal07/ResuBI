import os
import filecmp
import hashlib

def get_file_hash(file_path):
    """
    Calculates the MD5 hash of a file.
    """
    with open(file_path, 'rb') as file:
        data = file.read()
        return hashlib.md5(data).hexdigest()

def remove_duplicates(folder_path):
    """
    Removes duplicate files in the specified folder, comparing Word files with Word files
    and PDF files with PDF files separately.
    """
    pdf_files = {}
    docx_files = {}

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if os.path.isfile(file_path):
            file_hash = get_file_hash(file_path)

            if file_name.endswith('.pdf'):
                if file_hash in pdf_files:
                    print(f"Removing duplicate PDF file: {file_name}")
                    os.remove(file_path)
                else:
                    pdf_files[file_hash] = file_path

            elif file_name.endswith('.docx'):
                if file_hash in docx_files:
                    print(f"Removing duplicate Word file: {file_name}")
                    os.remove(file_path)
                else:
                    docx_files[file_hash] = file_path

# Usage
folder_path = 'D:/Resume/docs'
remove_duplicates(folder_path)
