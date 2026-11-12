
import os
from collections import Counter
from email import policy
from email.parser import BytesHeaderParser

DATA_DIR = r"D:\Clg\3-1\NLP-task\data\maildir"
SAMPLE_LIMIT = 1000

parser = BytesHeaderParser(policy=policy.default)

header_counts = Counter()
stats = {
    "scanned": 0,
    "readable": 0,
    "unreadable": 0
}

print("Inspecting a sample of Enron emails...")
print(f"Maximum sample size: {SAMPLE_LIMIT}\n")

for root, dirs, files in os.walk(DATA_DIR):
    for filename in files:
        if stats["scanned"] >= SAMPLE_LIMIT:
            break

        file_path = os.path.join(root, filename)

        # Preserve filenames that end with a period on Windows.
        safe_path = "\\\\?\\" + file_path

        stats["scanned"] += 1

        try:
            with open(safe_path, "rb") as f:
                message = parser.parse(f)

            stats["readable"] += 1

            for header in message.keys():
                header_counts[header.lower()] += 1

        except Exception:
            stats["unreadable"] += 1

    if stats["scanned"] >= SAMPLE_LIMIT:
        break

print("\n========== SAMPLE RESULTS ==========")
print("Files scanned:", stats["scanned"])
print("Readable:", stats["readable"])
print("Unreadable:", stats["unreadable"])

print("\n========== MOST COMMON HEADERS ==========")
for header, count in header_counts.most_common(30):
    print(f"{header:25} : {count}")

print("\n========== THREAD-RELATED HEADERS ==========")

thread_headers = [
    "message-id",
    "in-reply-to",
    "references",
    "thread-index",
    "thread-topic",
    "subject",
    "x-folder",
    "x-origin",
    "x-filename",
    "x-from",
    "x-to"
]

for header in thread_headers:
    print(f"{header:25} : {header_counts.get(header, 0)}")

print("\nSample inspection completed!")
