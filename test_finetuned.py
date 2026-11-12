
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_PATH = "models/email-reply-distilgpt2"

print("Loading fine-tuned email reply model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)

device = torch.device("cpu")
model.to(device)
model.eval()

def generate_reply(context, tone="Formal"):

    prompt = (
        f"Email context:\n{context}\n\n"
        f"Write a {tone.lower()} email reply:\n"
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=300
    )

    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )

    new_tokens = output[0][inputs["input_ids"].shape[1]:]

    return tokenizer.decode(
        new_tokens,
        skip_special_tokens=True
    ).strip()


sample_email = """
I cannot attend tomorrow's project meeting
because of a personal commitment.
Please share the meeting notes with me.
"""

print("\n========== FORMAL REPLY ==========")
print(generate_reply(sample_email, "Formal"))

print("\n========== FRIENDLY REPLY ==========")
print(generate_reply(sample_email, "Friendly"))
