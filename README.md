# Smart Email Reply Generator

## 1. Project Overview

Smart Email Reply Generator is an NLP-based application that generates email reply drafts from user-provided email context.

The application provides two reply tones:
- Formal
- Friendly

It uses a fine-tuned DistilGPT2 language model along with context-aware rule-based responses for common email situations.

The generated replies can be edited and copied by users. The application does not send emails automatically.

## 2. Objectives

- Generate email reply drafts automatically.
- Provide Formal and Friendly response styles.
- Apply Natural Language Processing techniques to email communication.
- Fine-tune a pretrained language model using email reply examples.
- Provide a simple and interactive web interface.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Programming language |
| PyTorch | Model training and inference |
| DistilGPT2 | Pretrained language model |
| Hugging Face Transformers | Model loading and fine-tuning |
| Streamlit | Web application interface |
| JSONL | Training dataset format |
| Enron Email Dataset | Source corpus for candidate email examples |

## 4. System Architecture

The application follows this workflow:

1. User enters an email message.
2. User selects a reply tone.
3. The application identifies supported common email scenarios.
4. For recognized scenarios, context-aware response templates generate drafts.
5. For other scenarios, the fine-tuned DistilGPT2 model generates a reply.
6. The generated draft is displayed.
7. User can edit and copy the response.

## 5. Dataset Preparation

The Enron Email Dataset was used as the source corpus.

Dataset preparation results:

- Emails scanned: 5,000
- Candidate examples extracted: 1,204
- Examples saved: 986
- Short replies excluded: 154
- Forwarded emails excluded: 753
- Short contexts excluded: 47
- Duplicates removed: 16
- Invalid text records excluded: 1

The resulting JSONL dataset contains two fields:

- `context`: Original email context
- `reply`: Candidate reply text

These are automatically extracted candidate pairs and have not all been independently verified as genuine replies.

## 6. Model Training

The pretrained DistilGPT2 model was fine-tuned using PyTorch and Hugging Face Transformers.

Training configuration:

- Model: DistilGPT2
- Training examples: 986
- Epochs: 1
- Batch size: 1
- Learning rate: 0.00005
- Gradient accumulation: 4
- Training device: CPU

Final training loss: 3.7870

The trained model is saved in:

`models/email-reply-distilgpt2`

## 7. Application Features

- Email context input
- Formal and Friendly tone selection
- Generate Reply button
- Editable generated reply
- Reset functionality
- Copyable output
- Context-aware handling of common email scenarios
- Local model inference

## 8. How to Run the Project

### Step 1: Activate virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 2: Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 3: Start the application

```powershell
streamlit run app.py
```

### Step 4: Open the application

Open the local Streamlit address:

`http://localhost:8501`

## 9. Testing

The following scenarios were tested:

| Test Case | Expected Result | Status |
|---|---|---|
| Model loading | Model loads successfully | Passed |
| Meeting rescheduling – Formal | Formal reply draft | Passed |
| Meeting rescheduling – Friendly | Friendly reply draft | Passed |
| Meeting notes request | Notes-sharing reply | Passed |
| Empty input | Validation warning | Passed |
| Reset functionality | Input and output cleared | Passed |

These results describe the tested local application behavior, not a formal model accuracy evaluation.

## 10. Limitations

- DistilGPT2 may generate irrelevant or generic responses for unfamiliar email contexts.
- The training dataset contains automatically extracted candidate pairs that may include noisy examples.
- Rule-based responses cover only selected common scenarios.
- The model runs locally on CPU, which can increase inference time.
- Generated drafts require human review before use.

## 11. Future Enhancements

- Improve dataset quality and validation.
- Expand the range of supported email scenarios.
- Improve model response relevance.
- Add evaluation metrics such as BLEU and ROUGE.
- Integrate TorchServe for model API serving.
- Deploy the application using Amazon SageMaker.
- Add multilingual email reply generation.

## 12. Conclusion

Smart Email Reply Generator demonstrates the use of Natural Language Processing and language model fine-tuning to assist users in drafting email responses.

The project combines a fine-tuned DistilGPT2 model with context-aware response handling and a Streamlit interface to provide an interactive email drafting application.