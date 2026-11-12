
import os
from email import policy
from email.parser import BytesParser

DATA_DIR = r"D:\Clg\3-1\NLP-task\data\maildir"
USER = "badeer-r"

FOLDERS = ["inbox", "sent_items", "_sent_mail"]

parser = BytesParser(policy=policy.default)

def get_body(message):
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                try:
                    return part.get_content()
                except Exception:
                    continue
    else:
        try:
            return message.get_content()
        except Exception:
            pass

    return ""

for folder in FOLDERS:
    folder_path = os.path.join(DATA_DIR, USER, folder)

    print("\n" + "=" * 65)
    print("FOLDER:", folder)
    print("=" * 65)

    if not os.path.isdir(folder_path):
        print("Folder not found.")
        continue

    count = 0

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            safe_path = "\\\\?\\" + file_path

            try:
                with open(safe_path, "rb") as f:
                    message = parser.parse(f)

                print("\nEmail:", filename)
                print("From:", message.get("From", ""))
                print("To:", message.get("To", ""))
                print("Date:", message.get("Date", ""))
                print("Subject:", message.get("Subject", ""))
                print("Message-ID:", message.get("Message-ID", ""))
                print("In-Reply-To:", message.get("In-Reply-To", ""))

                body = get_body(message)
                print("Body preview:", body[:250].replace("\n", " "))

                count += 1

            except Exception as error:
                print("Could not read:", filename, error)

            if count >= 5:
                break

        if count >= 5:
            break

print("\nInspection completed!")
