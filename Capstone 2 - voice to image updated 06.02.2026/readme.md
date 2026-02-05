# Voice to Image Generator App

A Streamlit app that turns your voice request into a generated image using AI.  
Supports voice recording or upload, shows transcript and expanded prompt, generates images with DALL·E, and displays every step transparently.

---

## Usage Workflow (Screenshots)

Screenshot 01
The application starts with a clean landing page, providing access to the main features and guiding the user through the workflow.

Screenshot 02
The system converts a spoken transcript into a structured voice prompt and generates an image using the OpenAI DALL·E model.

Screenshot 02-1
An alternative view of the transcript-to-prompt conversion process, demonstrating intermediate steps before image generation.

Screenshot 03
Image generation using the same transcript-to-voice prompt workflow, producing a second image with different visual output to demonstrate prompt variability.

Screenshot 04
The recording and uploading interface, allowing users to record audio or upload existing files for processing by the application.

---

## Features

- Record in-browser or upload short voice message (.wav)
- Live speech-to-text transcription
- AI-powered prompt engineering (GPT)
- DALL·E image generation (OpenAI API)
- All intermediate data and results visible in-app
- Secure API key management with Streamlit secrets

---

## Installation & Setup

git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
pip install -r requirements.txt

text

Or manually:

pip install streamlit openai speechrecognition audiorecorder

text

**API Key:**  
Create `.streamlit/secrets.toml` (at project root):

OPENAI_API_KEY = "sk-PASTE-YOUR-KEY-HERE"


**FFmpeg (Required for voice recording):**  
- [Download FFmpeg](https://ffmpeg.org/download.html)
- Add `/bin` directory to your system PATH

---

## Usage

streamlit run app.py

text
- Record voice or upload a `.wav` file
- See transcription and generated image prompt
- Review the AI-created image and all workflow details

---

## Security

- No data (audio, transcript, prompt, images) is stored or logged
- API keys are managed only in Streamlit secrets

---

## Troubleshooting

- **API errors:** Verify your OpenAI key and credits
- **Audio errors:** Ensure FFmpeg is installed and in PATH
- **Image errors:** Refine your voice command (prompt) or avoid restricted content

---

## Credits

Streamlit, OpenAI (GPT, DALL·E), SpeechRecognition, audiorecorder