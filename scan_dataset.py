"""
scan_dataset.py
===============
Full Enron Email Dataset Metadata Scanner.

What this script does:
  1. Walks every email file in data/maildir (all 217,305 files).
  2. Reads only headers (fast - does NOT load email body yet).
  3. Counts important metadata fields.
  4. Identifies genuine reply/thread relationships via In-Reply-To and References.
  5. Saves 20 sample email headers for manual inspection.
  6. Writes the final statistics report to: data/dataset_stats.json
  7. Prints a formatted summary to the console.

Usage (from project root, with venv active):
    python scan_dataset.py

Expected runtime on a CPU laptop: 3-8 minutes for 217,305 files.
"""

import os
import json
import time
from email import policy
from email.parser import BytesHeaderParser

# --- Configuration -----------------------------------------------------------

DATA_DIR   = r"D:\Clg\3-1\NLP-task\data\maildir"
OUTPUT_DIR = r"D:\Clg\3-1\NLP-task\data"
STATS_FILE = os.path.join(OUTPUT_DIR, "dataset_stats.json")

MAX_SAMPLES    = 20
PROGRESS_EVERY = 25000

# --- Setup -------------------------------------------------------------------

parser = BytesHeaderParser(policy=policy.default)

stats = {
    "total_files"    : 0,
    "readable"       : 0,
    "unreadable"     : 0,
    "has_message_id" : 0,
    "has_in_reply_to": 0,
    "has_references" : 0,
    "has_subject"    : 0,
    "has_from"       : 0,
    "has_to"         : 0,
    "has_date"       : 0,
    "has_x_from"     : 0,
    "has_x_to"       : 0,
    "empty_subject"  : 0,
    "re_subject"     : 0,
    "fw_subject"     : 0,
}

seen_message_ids = set()
all_in_reply_to  = []
samples          = []
first_error      = None
start_time       = time.time()

# --- Main Scan Loop ----------------------------------------------------------

print("=" * 55)
print("  ENRON DATASET - FULL METADATA SCAN")
print("=" * 55)
print(f"  Dataset directory : {DATA_DIR}")
print(f"  Output file       : {STATS_FILE}")
print("=" * 55)
print("  Starting scan... This may take 3-8 minutes.\n")

for root, dirs, files in os.walk(DATA_DIR):
    for filename in files:

        file_path = os.path.join(root, filename)
        # Preserve trailing periods in Windows filenames.
        safe_path = "\\\\?\\" + file_path
        stats["total_files"] += 1

        try:
            with open(safe_path, "rb") as f:
                msg = parser.parse(f)

            stats["readable"] += 1

            msg_id     = msg.get("Message-ID", "").strip()
            in_reply   = msg.get("In-Reply-To", "").strip()
            references = msg.get("References", "").strip()
            subject    = msg.get("Subject", "").strip()
            from_field = msg.get("From", "").strip()
            to_field   = msg.get("To", "").strip()
            date_field = msg.get("Date", "").strip()
            x_from     = msg.get("X-From", "").strip()
            x_to       = msg.get("X-To", "").strip()

            if msg_id:
                stats["has_message_id"] += 1
                seen_message_ids.add(msg_id)

            if in_reply:
                stats["has_in_reply_to"] += 1
                all_in_reply_to.append(in_reply)

            if references:
                stats["has_references"] += 1

            if subject:
                stats["has_subject"] += 1
                s_lower = subject.lower()
                if s_lower.startswith("re:") or s_lower.startswith("re "):
                    stats["re_subject"] += 1
                if s_lower.startswith("fw:") or s_lower.startswith("fwd:"):
                    stats["fw_subject"] += 1
            else:
                stats["empty_subject"] += 1

            if from_field:  stats["has_from"]   += 1
            if to_field:    stats["has_to"]     += 1
            if date_field:  stats["has_date"]   += 1
            if x_from:      stats["has_x_from"] += 1
            if x_to:        stats["has_x_to"]   += 1

            if len(samples) < MAX_SAMPLES:
                samples.append({
                    "file"        : file_path,
                    "Message-ID"  : msg_id,
                    "In-Reply-To" : in_reply,
                    "References"  : references,
                    "Subject"     : subject,
                    "From"        : from_field,
                    "To"          : to_field,
                    "Date"        : date_field,
                    "X-From"      : x_from,
                    "X-To"        : x_to,
                })

        except Exception as error:
            stats["unreadable"] += 1
            if first_error is None:
                first_error = {"file": file_path, "error": repr(error)}

        if stats["total_files"] % PROGRESS_EVERY == 0:
            elapsed = time.time() - start_time
            print(f"  Scanned {stats['total_files']:>7,} files  ({elapsed:.0f}s elapsed)")

# --- Post-scan: Count verified reply pairs -----------------------------------

print("\n  Matching In-Reply-To against known Message-IDs...")
verified_reply_pairs = sum(
    1 for irt in all_in_reply_to if irt in seen_message_ids
)

elapsed_total = time.time() - start_time

report = {
    "scan_duration_seconds" : round(elapsed_total, 1),
    "stats"                 : stats,
    "verified_reply_pairs"  : verified_reply_pairs,
    "first_error"           : first_error,
    "samples"               : samples,
}

with open(STATS_FILE, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

# --- Print summary -----------------------------------------------------------

print("\n" + "=" * 55)
print("  FULL ENRON DATASET ANALYSIS - RESULTS")
print("=" * 55)

labels = {
    "total_files"    : "Total files scanned",
    "readable"       : "Readable files",
    "unreadable"     : "Unreadable files",
    "has_message_id" : "Have Message-ID",
    "has_in_reply_to": "Have In-Reply-To",
    "has_references" : "Have References",
    "has_subject"    : "Have Subject",
    "re_subject"     : "Subject starts with RE:",
    "fw_subject"     : "Subject starts with FW:/FWD:",
    "empty_subject"  : "Empty subject",
    "has_from"       : "Have From",
    "has_to"         : "Have To",
    "has_date"       : "Have Date",
    "has_x_from"     : "Have X-From (Enron)",
    "has_x_to"       : "Have X-To (Enron)",
}

for key, label in labels.items():
    value = stats[key]
    print(f"  {label:<35} : {value:>8,}")

print("-" * 55)
print(f"  {'Verified reply pairs':<35} : {verified_reply_pairs:>8,}")
print("=" * 55)
print(f"\n  Scan completed in {elapsed_total:.1f} seconds.")
print(f"  Full report saved to: {STATS_FILE}")

if first_error:
    print(f"\n  First unreadable file : {first_error['file']}")
    print(f"  Error                 : {first_error['error']}")

print("\n  Next step: Run  python build_training_pairs.py")
print("=" * 55)
