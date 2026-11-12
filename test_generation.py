"""
test_generation.py
==================
Tests the email reply generation quality after fine-tuning.
Run this AFTER train.py completes.

Usage:
    python test_generation.py
"""

from generate import generate_email_reply

TEST_CASES = [
    {
        "name"    : "Meeting Reschedule",
        "context" : (
            "The quarterly review meeting has been rescheduled to "
            "Friday November 15th at 2 PM. Please confirm your attendance "
            "or let us know if you have a conflict."
        ),
        "tones"   : ["Formal", "Friendly"],
    },
    {
        "name"    : "File Request",
        "context" : (
            "Could you please send me the latest version of the "
            "project proposal document? I need it before our call tomorrow."
        ),
        "tones"   : ["Formal", "Friendly"],
    },
    {
        "name"    : "Deadline Extension Request",
        "context" : (
            "I am requesting a one-week extension for the assignment "
            "submission due to unexpected technical issues with our system."
        ),
        "tones"   : ["Formal"],
    },
    {
        "name"    : "Thank You",
        "context" : (
            "Thank you for your help with the presentation yesterday. "
            "The client was very impressed with the demo."
        ),
        "tones"   : ["Friendly"],
    },
]

print("=" * 65)
print("  EMAIL REPLY GENERATION - QUALITY TEST")
print("=" * 65)
print()

for case in TEST_CASES:
    print(f"Test: {case['name']}")
    print("-" * 65)
    print(f"Context: {case['context']}")
    print()

    for tone in case["tones"]:
        print(f"  [{tone} Reply]")
        reply = generate_email_reply(case["context"], tone)
        print(f"  {reply}")
        print()

    print("=" * 65)
    print()

print("Quality check complete.")
print("Review the replies above for:")
print("  - Relevance to the context")
print("  - Appropriate tone")
print("  - Fluency and grammar")
print("  - No invented facts (names, dates, numbers)")
