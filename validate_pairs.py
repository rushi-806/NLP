
import os
import re
from collections import Counter
from email import policy
from email.parser import BytesParser

DATA_DIR = r"D:\Clg\3-1\NLP-task\data\maildir"

MAX_EMAILS = 500
MAX_FILE_SIZE = 1024 * 1024  # 1 MB

parser = BytesParser(policy=policy.default)
stats = Counter()


def extract_body(message):
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


def find_quoted_message(body):
    patterns = [
        (
            "original_message",
            r"(?im)^\s*-{2,}\s*Original Message\s*-{2,}"
        ),
        (
            "outlook_headers",
            r"(?im)^\s*From:\s+.+\n\s*Sent:\s+.+\n\s*To:\s+.+\n\s*Subject:\s*.+"
        ),
        (
            "on_wrote",
            r"(?im)^\s*On .+wrote:\s*$"
        )
    ]

    for name, pattern in patterns:
        match = re.search(pattern, body)

        if match:
            reply = body[:match.start()].strip()
            quoted = body[match.start():].strip()
            return name, reply, quoted

    return None, None, None


print("Fast validation started...")
print("Maximum files:", MAX_EMAILS)

for root, dirs, files in os.walk(DATA_DIR):

    folder = os.path.basename(root).lower()

    if "sent" not in folder:
        continue

    for filename in files:

        if stats["scanned"] >= MAX_EMAILS:
            break

        path = os.path.join(root, filename)
        safe_path = "\\\\?\\" + path

        stats["scanned"] += 1

        try:
            if os.path.getsize(safe_path) > MAX_FILE_SIZE:
                stats["large_files_skipped"] += 1
                continue

            with open(safe_path, "rb") as f:
                message = parser.parse(f)

            stats["readable"] += 1

            body = extract_body(message)

            if not body.strip():
                stats["empty_body"] += 1
                continue

            marker, reply, quoted = find_quoted_message(body)

            if not marker:
                continue

            stats["candidates"] += 1
            stats["marker_" + marker] += 1

            if len(reply) >= 30:
                stats["reply_at_least_30"] += 1

            if len(reply) >= 50:
                stats["reply_at_least_50"] += 1

            if len(quoted) >= 100:
                stats["quoted_at_least_100"] += 1

            if len(reply) >= 30 and len(quoted) >= 100:
                stats["length_filtered"] += 1

            if re.search(r"(?im)^\s*(From|To|Subject):", quoted):
                stats["quoted_has_headers"] += 1

            subject = message.get("Subject", "").lower()

            if subject.startswith(("fw:", "fwd:")):
                stats["forward_subject"] += 1

        except Exception as error:
            stats["unreadable"] += 1

    if stats["scanned"] >= MAX_EMAILS:
        break


print("\n========== VALIDATION RESULTS ==========")

for key, value in stats.items():
    print(f"{key:25}: {value}")

print("\n========== SUMMARY ==========")
print("Scanned:", stats["scanned"])
print("Candidates:", stats["candidates"])
print("Replies >= 30 chars:", stats["reply_at_least_30"])
print("Replies >= 50 chars:", stats["reply_at_least_50"])
print("Length-filtered:", stats["length_filtered"])
print("Quoted headers found:", stats["quoted_has_headers"])
print("Large files skipped:", stats["large_files_skipped"])

print("\nValidation completed!")
