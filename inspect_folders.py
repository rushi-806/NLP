
import os
from collections import Counter

DATA_DIR = r"D:\Clg\3-1\NLP-task\data\maildir"

folder_counts = Counter()
sent_folders = []
inbox_folders = []

for root, dirs, files in os.walk(DATA_DIR):
    for folder in dirs:
        path = os.path.join(root, folder)
        relative = os.path.relpath(path, DATA_DIR)

        folder_counts[relative] += 0

    for filename in files:
        path = os.path.join(root, filename)
        relative_folder = os.path.relpath(root, DATA_DIR)

        folder_counts[relative_folder] += 1

        folder_name = os.path.basename(root).lower()

        if "sent" in folder_name:
            sent_folders.append((relative_folder, filename))

        if "inbox" in folder_name:
            inbox_folders.append((relative_folder, filename))

print("\n========== TOP MAILBOX FOLDERS ==========")

for folder, count in folder_counts.most_common(30):
    print(f"{folder:55} : {count}")

print("\n========== SENT FOLDER SUMMARY ==========")
print("Emails in folders containing 'sent':", len(sent_folders))

for folder, filename in sent_folders[:10]:
    print(folder, "->", filename)

print("\n========== INBOX FOLDER SUMMARY ==========")
print("Emails in folders containing 'inbox':", len(inbox_folders))

for folder, filename in inbox_folders[:10]:
    print(folder, "->", filename)

print("\nFolder inspection completed!")