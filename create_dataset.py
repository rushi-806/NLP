
import os
import re
import json
import hashlib
from email import policy
from email.parser import BytesParser
from collections import Counter

DATA_DIR = r"D:\Clg\3-1\NLP-task\data\maildir"
OUTPUT_FILE = "email_dataset.jsonl"

MAX_EMAILS = 5000
MIN_REPLY_LENGTH = 30
MIN_CONTEXT_LENGTH = 50

parser = BytesParser(policy=policy.default)

stats = Counter()
seen = set()


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


def split_email(body):
    patterns = [
        r"(?im)^\s*-{2,}\s*Original Message\s*-{2,}",
        r"(?im)^\s*From:\s+.+\n\s*Sent:\s+.+\n\s*To:\s+.+\n\s*Subject:\s*.+",
        r"(?im)^\s*On .+wrote:\s*$"
    ]

    for pattern in patterns:
        match = re.search(pattern, body)

        if match:
            return body[:match.start()].strip(), body[match.start():].strip()

    return None, None


def clean_text(text):
    # Remove HTML-like tags.
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove credential-bearing lines.
    text = re.sub(
        r"(?im)^.*(?:password|passwd|passcode|api[_ -]?key|secret|token)\s*[:=].*$",
        " [REDACTED CREDENTIAL] ",
        text
    )

    # Redact email addresses and phone numbers.
    text = re.sub(
        r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
        "[EMAIL]",
        text
    )

    text = re.sub(
        r"\b(?:\+?\d[\d\s().-]{8,}\d)\b",
        "[PHONE]",
        text
    )

    # Remove quoted reply markers and excess whitespace.
    text = re.sub(r"(?m)^\s*>+\s?", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_original_context(quoted):
    # Find the body after the original message headers.
    subject_match = re.search(
        r"(?im)^\s*Subject:\s*.*$",
        quoted
    )

    if subject_match:
        context = quoted[subject_match.end():].strip()
        context = re.sub(r"^\s*-+\s*", "", context)
        return context

    # Handle simple "On ... wrote:" quotations.
    wrote_match = re.search(
        r"(?im)^\s*On .+wrote:\s*$",
        quoted
    )

    if wrote_match:
        return quoted[wrote_match.end():].strip()

    return ""


def valid_text(text):
    if len(text) < 3:
        return False

    if len(set(text.split())) < 3:
        return False

    return True


print("Creating cleaned email dataset...")
print("Maximum emails:", MAX_EMAILS)

with open(OUTPUT_FILE, "w", encoding="utf-8") as output:

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

                subject = message.get("Subject", "").lower()

                # Exclude obvious forwards.
                if subject.startswith(("fw:", "fwd:")):
                    stats["forward_excluded"] += 1
                    continue

                body = extract_body(message)

                reply, quoted = split_email(body)

                if not reply or not quoted:
                    continue

                stats["candidates"] += 1

                context = extract_original_context(quoted)

                reply = clean_text(reply)
                context = clean_text(context)

                if len(reply) < MIN_REPLY_LENGTH:
                    stats["short_reply_excluded"] += 1
                    continue

                if len(context) < MIN_CONTEXT_LENGTH:
                    stats["short_context_excluded"] += 1
                    continue

                if not valid_text(reply) or not valid_text(context):
                    stats["invalid_text"] += 1
                    continue

                # Avoid duplicate examples.
                unique_key = hashlib.sha256(
                    (context + reply).encode("utf-8")
                ).hexdigest()

                if unique_key in seen:
                    stats["duplicates"] += 1
                    continue

                seen.add(unique_key)

                record = {
                    "context": context[:2000],
                    "reply": reply[:1000]
                }

                output.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )

                stats["saved"] += 1

            except Exception:
                stats["unreadable"] += 1

        if stats["scanned"] >= MAX_EMAILS:
            break

print("\n========== DATASET RESULTS ==========")

for key, value in stats.items():
    print(f"{key:25}: {value}")

print("\nDataset saved:", OUTPUT_FILE)
print("Dataset creation completed!")
