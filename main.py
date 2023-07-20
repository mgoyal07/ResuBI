import os
import mail
import compare
import datetime
# mere pass docs folder mein files aa gyi h

import resume
from resume import insert_to_db

# Specify the directory path where your files are located
directory = ""

for filename in os.listdir(directory):
    if filename.endswith(".doc") or filename.endswith(".docx") or filename.endswith(".pdf"):
        file_path = os.path.join(directory, filename)
        print("starting...............")
        insert_to_db(file_path)

file = open(r'D:/Resume/result.txt', 'a')
file.write(f'{datetime.datetime.now()} - The script ran \n')
