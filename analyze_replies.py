
import os
import re
from email import policy
from email.parser import BytesParser
from collections import Counter

DATA_DIR = r"D:\Clg\3-1\NLP-task\data\maildir"
MAX_EMAILS = 2000

parser = BytesParser(policy=policy.default)

stats = Counter()
examples = []

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

def split_reply(body):
    # Common quoted-message separators in email conversations.
    patterns = [
        r"(?im)^\s*-{2,}\s*Original Message\s*-{2,}",
        r"(?im)^\s*From:\s+.+\n\s*Sent:\s+.+\n\s*To:\s+.+\n\s*Subject:\s+.+",
        r"(?im)^\s*On .+wrote:\s*$"
    ]

    for pattern in patterns:
        match = re.search(pattern, body)
        if match:
            reply = body[:match.start()].strip()
            quoted = body[match.start():].strip()

            if len(reply) >= 10 and len(quoted) >= 30:
                return reply, quoted

    return None, None

print("Analyzing sent emails...")
print("Maximum emails:", MAX_EMAILS)

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
            with open(safe_path, "rb") as f:
                message = parser.parse(f)

            stats["readable"] += 1
            body = extract_body(message)

            if not body:
                stats["empty_body"] += 1
                continue

            reply, quoted = split_reply(body)

            if reply and quoted:
                stats["candidate_pairs"] += 1

                if len(examples) < 5:
                    examples.append({
                        "subject": message.get("Subject", ""),
                        "reply_length": len(reply),
                        "quoted_length": len(quoted)
                    })

        except Exception:
            stats["unreadable"] += 1

    if stats["scanned"] >= MAX_EMAILS:
        break

print("\n========== ANALYSIS RESULTS ==========")
for key, value in stats.items():
    print(f"{key:25}: {value}")

print("\n========== REDACTED EXAMPLES ==========")
for index, example in enumerate(examples, 1):
    print(f"\nExample {index}")
    print("Subject:", "[REDACTED]")
    print("Reply length:", example["reply_length"])
    print("Quoted message length:", example["quoted_length"])

print("\nAnalysis completed!")
