import streamlit as st
from audiorecorder import audiorecorder 
import speech_recognition as sr
from openai import OpenAI
import tempfile
import io

st.set_page_config(page_title="Voice to Image Generator", layout="wide")
st.title("🎤 Voice to Image Generator App")

#STORE API KEY IN SECRETS
if "OPENAI_API_KEY" in st.secrets:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.sidebar.header("API Key Setup")
    openai_api_key = st.sidebar.text_input(
        "Enter your OpenAI API key:",
        type="password",
        help="Key is hidden."
    )

#OpenAI client set up
client = OpenAI(api_key=openai_api_key)

#AUDIO RECORDING WITH UPLOAD OPTION
st.header("Record or Upload your voice message")
st.subheader("Record here or upload a .wav file below")

audio_bytes = audiorecorder("Click to record", "Recording... Click to stop")
audio_file = st.file_uploader("Or upload a .wav file", type=["wav"])

transcript = ""

if audio_bytes:
    wav_bytes_io = io.BytesIO()
    audio_bytes.export(wav_bytes_io, format="wav")
    wav_bytes_io.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(wav_bytes_io.read())
        recorded_wav_path = f.name
    st.audio(recorded_wav_path, format="audio/wav")
    recognizer = sr.Recognizer()
    with sr.AudioFile(recorded_wav_path) as source:
        audio = recognizer.record(source)
    try:
        transcript = recognizer.recognize_google(audio)
        st.success(f"Transcript: {transcript}")
    except sr.UnknownValueError:
        st.error("Speech Recognition could not understand audio.")
    except sr.RequestError as e:
        st.error(f"Could not request results from Speech Recognition service; {e}")

elif audio_file:
    st.audio(audio_file, format="audio/wav")
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        transcript = recognizer.recognize_google(audio)
        st.success(f"Transcript: {transcript}")
    except sr.UnknownValueError:
        st.error("Speech Recognition could not understand audio.")
    except sr.RequestError as e:
        st.error(f"Could not request results from Speech Recognition service; {e}")

if transcript:
    st.subheader("Intermediate Transcript")
    st.text_area("Transcript:", value=transcript, height=100)

# Convert Transcript to Image Prompt
st.header("Convert transcript to image prompt")
image_prompt = ""
if transcript and openai_api_key:
    prompt_instruction = (
        "Convert the following description of a user's request for an image into a detailed prompt "
        "for an image generation AI. Be specific, visual, and concrete: "
        f"\n\nUser transcript: '{transcript}'\n"
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_instruction}],
            max_tokens=100,
            temperature=0.7
        )
        image_prompt = completion.choices[0].message.content
        st.success("Generated Image Prompt:")
        st.text_area("Image Prompt:", value=image_prompt, height=100)
    except Exception as e:
        st.error(f"OpenAI error: {e}")

# Image generation using Dall-e
st.header("Generate image using OpenAI DALL·E")
generated_image_url = ""
if image_prompt and openai_api_key:
    try:
        image_response = client.images.generate(
            model="dall-e-2",
            prompt=image_prompt,
            n=1,
            size="512x512"
        )
        generated_image_url = image_response.data[0].url
        st.image(generated_image_url, caption="Generated Image")
        st.success("Image successfully generated and displayed.")
    except Exception as e:
        st.error(f"Image generation error: {e}")

if generated_image_url:
    st.subheader("Result & Details")
    st.markdown(f"**Image Model Used:** OpenAI DALL·E")
    st.markdown(f"**Prompt:** {image_prompt}")
    st.markdown(f"**Image URL:** {generated_image_url}")

if not openai_api_key:
    st.warning("Please set up your openai api key inside ./streamlit/secrets.toml, if the files or folders do not exist create them")

#Print logs to the console to trace
if transcript or image_prompt or generated_image_url:
    print("LOG | Transcript:", transcript)
    print("LOG | Image Prompt:", image_prompt)
    print("LOG | Image URL:", generated_image_url)
