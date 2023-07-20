import imaplib
import email
import os

from credentials import useName,passWord

imap_url ='imap.gmail.com'
mail = imaplib.IMAP4_SSL(imap_url)
mail.login(useName, passWord)

# Select the mailbox you want to work with
mail.select('INBOX')
filename_count = {}
# Search for emails with the keyword "resume" in the subject or body
# search_criteria = '(OR SUBJECT "resume" SUBJECT "cv" SUBJECT "internship" TEXT "resume" TEXT "cv" TEXT "internship")'
# result, data = mail.search(None, search_criteria)

keywords = ['resume', 'cv', 'internship', 'job']
print(len(keywords))
for i in range(0, len(keywords)):
    search_criteria = '(OR'
    # for keyword in keywords:     
    search_criteria += f' SUBJECT "{keywords[i]}" TEXT "{keywords[i]}"'
    search_criteria += ') UNSEEN'

    print(search_criteria)
    result, data = mail.search(None, search_criteria)

# Iterate through the list of email IDs
    for email_id in data[0].split():
       # Fetch the email data
        result, email_data = mail.fetch(email_id, '(RFC822)')
        raw_email = email_data[0][1]
        email_message = email.message_from_bytes(raw_email)
    
        # Iterate through the email parts
        for part in email_message.walk():
           # Check if the part is an attachment
           if part.get_content_maintype() == 'multipart':
            continue
           if part.get('Content-Disposition') is None:
            continue
    
           # Extract the attachment filename
           filename = part.get_filename()

           # Download the attachment if it exists and has a resume-related extension
           if filename:
                count = filename_count.get(filename, 0)
                count += 1
                filename_count[filename] = count

                # Add a count suffix to the filename to avoid conflicts
                filename_parts = os.path.splitext(filename)
                new_filename = f"{filename_parts[0]}_{count}{filename_parts[1]}"

                # Download the attachment to a specific directory with the new filename
                save_path = os.path.join('D:/Resume/docs', new_filename)
                with open(save_path, 'wb') as f:
                    f.write(part.get_payload(decode=True))
# Close the connection to the email server
mail.close()
mail.logout()


