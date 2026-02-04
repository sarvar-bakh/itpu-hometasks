# Voice to Image Generator App

A Streamlit app that turns your voice request into a generated image using AI.  
Supports voice recording or upload, shows transcript and expanded prompt, generates images with DALL·E, and displays every step transparently.

---

## Screenshots

![Start Page](screenshots/1.png)
![Transcript & Prompt](screenshots/2.png)
![Image Generation](screenshots/3.png)
![Final Result](screenshots/4.png)

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