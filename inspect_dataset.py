
import json
from collections import Counter

FILE_PATH = "email_dataset.jsonl"

total = 0
valid = 0
field_counts = Counter()
lengths = Counter()

print("Inspecting cleaned email dataset...")

with open(FILE_PATH, "r", encoding="utf-8") as file:
    for line in file:
        total += 1

        try:
            item = json.loads(line)

            if not isinstance(item, dict):
                continue

            valid += 1

            for key, value in item.items():
                field_counts[key] += 1

                if isinstance(value, str):
                    lengths[key] += len(value)

        except json.JSONDecodeError:
            print("Invalid JSON at line:", total)

print("\n========== DATASET INSPECTION ==========")
print("Total records:", total)
print("Valid records:", valid)

print("\nFields found:")
for key, count in field_counts.items():
    print(f"{key}: {count} records")

print("\nAverage text lengths:")
for key, count in field_counts.items():
    if count and key in lengths:
        print(f"{key}: {lengths[key] / count:.1f} characters")

print("\nInspection completed!")
