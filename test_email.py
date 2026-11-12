
from model import generate_email_reply

email_context = """
I cannot attend tomorrow's project meeting
because of a personal commitment.
Please share the meeting notes with me.
"""

print("\nFORMAL EMAIL REPLY:")
print(generate_email_reply(email_context, "Formal"))

print("\nFRIENDLY EMAIL REPLY:")
print(generate_email_reply(email_context, "Friendly"))
