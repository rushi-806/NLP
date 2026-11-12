
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = "distilgpt2"

print("Loading DistilGPT2 model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

device = torch.device("cpu")
model.to(device)
model.eval()

print("DistilGPT2 loaded successfully!")


def generate_email_reply(email_context, tone="Formal"):

    if not email_context.strip():
        return "Please enter the email context."

    prompt = f"""
Email context: {email_context}

Write a {tone.lower()} email reply.

Reply:
"""

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=400
    )

    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.8,
            top_p=0.9,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )

    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]

    reply = tokenizer.decode(
        new_tokens,
        skip_special_tokens=True
    )

    if not reply.strip():
        return "The model could not generate a reply. Please try again."

    return reply.strip()
