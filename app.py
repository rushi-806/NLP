
import os
import re
import torch
import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Smart Email Reply Generator",
    page_icon="📧",
    layout="centered"
)

MODEL_PATH = "models/email-reply-distilgpt2"


# ==================================================
# LOAD FINE-TUNED MODEL
# ==================================================

@st.cache_resource
def load_model():

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)

    device = torch.device("cpu")

    model.to(device)
    model.eval()

    return tokenizer, model, device


# ==================================================
# CONTEXT-AWARE REPLY GENERATION
# ==================================================

def generate_reply(context, tone, tokenizer, model, device):

    text = context.lower()

    # ----------------------------------------------
    # CASE 1: MEETING RESCHEDULING
    # ----------------------------------------------

    if any(word in text for word in [
        "reschedule",
        "move the meeting",
        "change the meeting"
    ]):

        time_match = re.search(
            r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
            r"(?:\s+at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?)?",
            context,
            re.IGNORECASE
        )

        proposed_time = (
            time_match.group(0) if time_match
            else "the proposed time"
        )

        if tone == "Formal":
            return (
                "Hello,\n\n"
                "Thank you for informing me. I understand that you "
                "are unable to attend the scheduled meeting.\n\n"
                f"I will check the availability for {proposed_time} "
                "and confirm the revised meeting schedule shortly.\n\n"
                "Best regards"
            )

        return (
            "Hi,\n\n"
            "Thanks for letting me know! No problem. "
            f"I'll check if {proposed_time} works and get back to you "
            "with confirmation.\n\n"
            "Best"
        )

    # ----------------------------------------------
    # CASE 2: REQUEST FOR MEETING NOTES
    # ----------------------------------------------

    if "meeting notes" in text or "share the notes" in text:

        if tone == "Formal":
            return (
                "Hello,\n\n"
                "Thank you for your message. I will share the "
                "meeting notes with you shortly.\n\n"
                "Best regards"
            )

        return (
            "Hi,\n\n"
            "Sure! I'll share the meeting notes with you shortly.\n\n"
            "Thanks!"
        )

    # ----------------------------------------------
    # CASE 3: UNABLE TO ATTEND A MEETING
    # ----------------------------------------------

    if "cannot attend" in text or "unable to attend" in text:

        if tone == "Formal":
            return (
                "Hello,\n\n"
                "Thank you for letting me know. I understand that "
                "you are unable to attend.\n\n"
                "We can discuss an alternative arrangement. "
                "Please let me know your availability.\n\n"
                "Best regards"
            )

        return (
            "Hi,\n\n"
            "No worries! Thanks for letting me know. "
            "Let's find another suitable time to connect.\n\n"
            "Best"
        )

    # ----------------------------------------------
    # CASE 4: FINE-TUNED DISTILGPT2
    # ----------------------------------------------

    prompt = (
        f"Email context:\n{context}\n\n"
        f"Write a {tone.lower()} email reply:\n"
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=260
    )

    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }

    with torch.no_grad():

        outputs = model.generate(
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

    new_tokens = outputs[0][
        inputs["input_ids"].shape[1]:
    ]

    reply = tokenizer.decode(
        new_tokens,
        skip_special_tokens=True
    ).strip()

    if not reply:
        return "Unable to generate a reply. Please try again."

    return reply


# ==================================================
# RESET FUNCTION
# ==================================================

def reset_fields():

    st.session_state.email_context = ""
    st.session_state.generated_reply = ""


# ==================================================
# MAIN USER INTERFACE
# ==================================================

st.title("📧 Smart Email Reply Generator")

st.write(
    "Generate professional and friendly email replies "
    "using Natural Language Processing and AI."
)

st.divider()


# ==================================================
# MODEL INITIALIZATION
# ==================================================

if not os.path.isdir(MODEL_PATH):

    st.error(
        "Fine-tuned model not found. "
        "Please run train_model.py first."
    )

    st.stop()

try:

    with st.spinner("Loading AI model..."):

        tokenizer, model, device = load_model()

    st.success("AI model loaded successfully!")

except Exception as error:

    st.error(f"Model loading failed: {error}")
    st.stop()


# ==================================================
# SESSION STATE
# ==================================================

if "email_context" not in st.session_state:
    st.session_state.email_context = ""

if "generated_reply" not in st.session_state:
    st.session_state.generated_reply = ""


# ==================================================
# EMAIL INPUT
# ==================================================

st.subheader("Enter Email Context")

st.text_area(
    "Paste the email you received:",
    height=200,
    placeholder="Enter the email message here...",
    key="email_context"
)


# ==================================================
# TONE SELECTION
# ==================================================

tone = st.selectbox(
    "Choose Reply Tone",
    ["Formal", "Friendly"]
)


# ==================================================
# BUTTONS
# ==================================================

col1, col2 = st.columns(2)

with col1:

    generate_button = st.button(
        "✨ Generate Reply",
        use_container_width=True
    )

with col2:

    st.button(
        "🔄 Reset",
        use_container_width=True,
        on_click=reset_fields
    )


# ==================================================
# GENERATE REPLY
# ==================================================

if generate_button:

    context = st.session_state.email_context.strip()

    if not context:

        st.warning("Please enter an email context first.")

    else:

        try:

            with st.spinner("Generating your email reply..."):

                reply = generate_reply(
                    context,
                    tone,
                    tokenizer,
                    model,
                    device
                )

                st.session_state.generated_reply = reply

        except Exception as error:

            st.error(f"Reply generation failed: {error}")


# ==================================================
# DISPLAY GENERATED REPLY
# ==================================================

if st.session_state.generated_reply:

    st.divider()

    st.subheader("Generated Email Reply")

    st.text_area(
        "Edit your reply if needed:",
        height=180,
        key="generated_reply"
    )

    st.caption("Copy your generated reply using the copy icon below.")

    st.code(
        st.session_state.generated_reply,
        language=None
    )

    st.info(
        "Review the generated reply for accuracy and relevance "
        "before using it. This application does not send emails."
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Smart Email Reply Generator | NLP Mini Project | "
    "Powered by Fine-tuned DistilGPT2 and PyTorch"
)
