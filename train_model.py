
import os
import json
import time
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM

# ---------------- CONFIGURATION ----------------

MODEL_NAME = "distilgpt2"
DATA_FILE = "email_dataset.jsonl"
OUTPUT_DIR = "models/email-reply-distilgpt2"

MAX_PROMPT_LENGTH = 260
MAX_REPLY_LENGTH = 120
BATCH_SIZE = 1
EPOCHS = 1
LEARNING_RATE = 5e-5
GRADIENT_ACCUMULATION = 4

torch.manual_seed(42)
torch.set_num_threads(4)

device = torch.device("cpu")

# ---------------- LOAD DATA ----------------

print("Loading dataset...")

examples = []

with open(DATA_FILE, "r", encoding="utf-8") as file:
    for line in file:
        item = json.loads(line)

        context = item.get("context", "").strip()
        reply = item.get("reply", "").strip()

        if context and reply:
            examples.append((context, reply))

print("Total training examples:", len(examples))

if not examples:
    raise ValueError("No valid training examples found.")

# ---------------- LOAD MODEL ----------------

print("\nLoading DistilGPT2...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model.config.pad_token_id = tokenizer.pad_token_id
model.to(device)
model.train()

print("Model loaded successfully!")

# ---------------- PREPARE DATASET ----------------

class EmailDataset(Dataset):

    def __init__(self, data):
        self.items = []

        print("\nPreparing training examples...")

        for context, reply in data:

            prompt = (
                "Email context:\n"
                + context
                + "\n\nWrite a professional email reply:\n"
            )

            prompt_ids = tokenizer.encode(
                prompt,
                add_special_tokens=False,
                truncation=True,
                max_length=MAX_PROMPT_LENGTH
            )

            reply_ids = tokenizer.encode(
                reply,
                add_special_tokens=False,
                truncation=True,
                max_length=MAX_REPLY_LENGTH
            )

            reply_ids.append(tokenizer.eos_token_id)

            input_ids = prompt_ids + reply_ids

            labels = (
                [-100] * len(prompt_ids)
                + reply_ids
            )

            self.items.append({
                "input_ids": torch.tensor(input_ids, dtype=torch.long),
                "labels": torch.tensor(labels, dtype=torch.long)
            })

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]


dataset = EmailDataset(examples)

loader = DataLoader(
    dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)

print("Prepared examples:", len(dataset))

# ---------------- TRAINING ----------------

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LEARNING_RATE
)

print("\n========== TRAINING STARTED ==========")

start_time = time.time()

for epoch in range(EPOCHS):

    total_loss = 0.0
    optimizer.zero_grad()

    for step, batch in enumerate(loader):

        input_ids = batch["input_ids"].unsqueeze(0).to(device)
        labels = batch["labels"].unsqueeze(0).to(device)

        attention_mask = torch.ones_like(input_ids)

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )

        loss = outputs.loss / GRADIENT_ACCUMULATION
        loss.backward()

        total_loss += outputs.loss.item()

        if (step + 1) % GRADIENT_ACCUMULATION == 0:
            torch.nn.utils.clip_grad_norm_(
                model.parameters(), 1.0
            )

            optimizer.step()
            optimizer.zero_grad()

        if (step + 1) % 50 == 0:
            average_loss = total_loss / (step + 1)

            print(
                f"Epoch {epoch + 1}/{EPOCHS} | "
                f"Step {step + 1}/{len(loader)} | "
                f"Average Loss: {average_loss:.4f}"
            )

    # Update remaining accumulated gradients
    if len(loader) % GRADIENT_ACCUMULATION != 0:
        optimizer.step()
        optimizer.zero_grad()

    average_loss = total_loss / len(loader)

    print(
        f"\nEpoch {epoch + 1} completed. "
        f"Average Loss: {average_loss:.4f}"
    )

# ---------------- SAVE MODEL ----------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("\nSaving fine-tuned model...")

model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

elapsed = (time.time() - start_time) / 60

print("\n========== TRAINING COMPLETED ==========")
print("Model saved at:", OUTPUT_DIR)
print(f"Training time: {elapsed:.2f} minutes")
print("You can now test the fine-tuned model.")
