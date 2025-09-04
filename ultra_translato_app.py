import streamlit as st
from googletrans import Translator
from gtts import gTTS
import base64
import os
import uuid
import speech_recognition as sr
from pydub import AudioSegment
import pyaudio
import wave

# --- Page Configuration and Headers ---
st.set_page_config(page_title="🌍 Ultra Translato", layout="centered")

st.markdown("<h1 style='text-align: center;'>🌍 Ultra Translato</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Translate your text (from any language) or audio into multiple languages</p>", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'translations' not in st.session_state:
    st.session_state.translations = {}
if 'audio_to_play' not in st.session_state:
    st.session_state.audio_to_play = None
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None
if 'audio_source_type' not in st.session_state:
    st.session_state.audio_source_type = None

# --- Language Options ---
language_names = {
    "Hindi": "hi", "Spanish": "es", "French": "fr", "German": "de",
    "Chinese (Simplified)": "zh-cn", "Arabic": "ar", "Russian": "ru",
    "Japanese": "ja", "Korean": "ko", "Italian": "it", "Portuguese": "pt",
    "Turkish": "tr", "English": "en", "Afrikaans": "af", "Albanian": "sq",
    "Amharic": "am", "Azerbaijani": "az", "Basque": "eu", "Belarusian": "be",
    "Bengali": "bn", "Bosnian": "bs", "Bulgarian": "bg", "Catalan": "ca",
    "Cebuano": "ceb", "Chichewa": "ny", "Corsican": "co", "Croatian": "hr",
    "Czech": "cs", "Danish": "da", "Dutch": "nl", "Esperanto": "eo",
    "Estonian": "et", "Filipino": "tl", "Finnish": "fi", "Frisian": "fy",
    "Galician": "gl", "Georgian": "ka", "Greek": "el", "Gujarati": "gu",
    "Haitian Creole": "ht", "Hausa": "ha", "Hawaiian": "haw", "Hebrew": "iw",
    "Hmong": "hmn", "Hungarian": "hu", "Icelandic": "is", "Igbo": "ig",
    "Indonesian": "id", "Irish": "ga", "Javanese": "jw", "Kannada": "kn",
    "Kazakh": "kk", "Khmer": "km", "Kinyarwanda": "rw", "Lao": "lo",
    "Latin": "la", "Latvian": "lv", "Lithuanian": "lt", "Luxembourgish": "lb",
    "Macedonian": "mk", "Malagasy": "mg", "Malay": "ms", "Malayalam": "ml",
    "Maltese": "mt", "Maori": "mi", "Marathi": "mr", "Mongolian": "mn",
    "Myanmar (Burmese)": "my", "Nepali": "ne", "Norwegian": "no", "Oriya": "or",
    "Pashto": "ps", "Persian": "fa", "Polish": "pl", "Punjabi": "pa",
    "Romanian": "ro", "Samoan": "sm", "Scots Gaelic": "gd", "Serbian": "sr",
    "Sesotho": "st", "Shona": "sn", "Sindhi": "sd", "Sinhala": "si",
    "Slovak": "sk", "Slovenian": "sl", "Somali": "so", "Sundanese": "su",
    "Swahili": "sw", "Swedish": "sv", "Tajik": "tg", "Tamil": "ta",
    "Tatar": "tt", "Telugu": "te", "Thai": "th", "Tongan": "to",
    "Ukrainian": "uk", "Urdu": "ur", "Uyghur": "ug", "Uzbek": "uz",
    "Vietnamese": "vi", "Welsh": "cy", "Xhosa": "xh", "Yiddish": "yi",
    "Yoruba": "yo", "Zulu": "zu",
}

# --- gTTS Supported Languages ---
gtts_supported_languages = [
    'af', 'sq', 'ar', 'bn', 'bs', 'my', 'ca', 'ceb', 'zh-cn', 'zh-tw', 'hr', 'cs', 'da',
    'nl', 'en', 'eo', 'et', 'fil', 'fi', 'fr', 'gl', 'de', 'el', 'gu', 'ht', 'ha', 'iw',
    'hi', 'hmn', 'hu', 'is', 'id', 'ga', 'it', 'ja', 'kn', 'kk', 'km', 'ko', 'la',
    'lv', 'lt', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'ne', 'no', 'fa', 'pl', 'pt',
    'pa', 'ro', 'ru', 'sm', 'gd', 'sr', 'st', 'sn', 'si', 'sk', 'sl', 'so', 'es',
    'su', 'sw', 'sv', 'tl', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'uy', 'uz', 'vi', 'cy', 'xh',
    'yi', 'yo', 'zu'
]

# --- Translator and TTS Functions ---
translator = Translator()

def translate_text(text, dest_lang):
    try:
        translated_obj = translator.translate(text, dest=dest_lang)
        return translated_obj.text, translated_obj.src
    except Exception as e:
        st.error(f"⚠️ Translation Error: {e}")
        return "Translation failed.", "unknown"

def text_to_speech(text, lang_code):
    try:
        if lang_code not in gtts_supported_languages:
            return None
        
        tts = gTTS(text=text, lang=lang_code, slow=False)
        filename = f"{uuid.uuid4()}.mp3"
        tts.save(filename)
        with open(filename, "rb") as f:
            audio_bytes = f.read()
        os.remove(filename)
        b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio controls autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
        """
        return audio_html
    except Exception as e:
        st.error(f"⚠️ Audio Error for code `{lang_code}`: {e}")
        return None

# New function to record audio from the microphone
def record_audio_to_file(filename, duration=5, channels=1, rate=16000, chunk=1024):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)
    
    st.info("Recording for 5 seconds...")
    frames = []
    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    return filename

# --- Sidebar Mode Selection ---
st.sidebar.markdown("### Choose a Mode")
mode = st.sidebar.selectbox(" ", ["Text Translator", "Speech Translator"])

# --- Main app logic based on selected mode ---
if mode == "Text Translator":
    st.markdown("## Translate your text to multiple languages")
    selected_languages = st.multiselect("Choose target languages", options=list(language_names.keys()))

    st.subheader("Enter text to translate")
    input_text = st.text_area("Your Text", height=150, placeholder="Type something in any language...")

    translate_button, clear_button = st.columns([1, 1])

    with translate_button:
        if st.button("Translate"):
            if not input_text.strip():
                st.warning("Please enter some text.")
            elif not selected_languages:
                st.warning("Please select at least one target language.")
            else:
                st.session_state.translations = {}
                st.session_state.audio_to_play = None
                
                try:
                    detected_lang = translator.detect(input_text).lang
                    st.success(f"Detected language: `{detected_lang}`")
                except Exception:
                    detected_lang = "unknown"
                    st.error("Could not detect input language.")
                
                for lang in selected_languages:
                    target_code = language_names[lang]
                    if target_code == detected_lang:
                        st.session_state.translations[lang] = "Same as input language."
                    else:
                        translated, _ = translate_text(input_text, target_code)
                        if translated != "Translation failed.":
                            st.session_state.translations[lang] = translated
                        else:
                            st.session_state.translations[lang] = None
                st.rerun()

    with clear_button:
        if st.button("🗑️ Clear All"):
            st.session_state.translations = {}
            st.session_state.audio_to_play = None
            input_text = ""
            st.session_state.selected_languages = []
            st.rerun()
            
    # --- Display Translations for Text Mode ---
    if st.session_state.translations:
        st.markdown("---")
        st.subheader("Translated Texts")
        for lang in selected_languages:
            translated = st.session_state.translations.get(lang)
            
            if translated is None:
                continue
            
            st.markdown(f"**{lang}**: {translated}")

            if translated != "Same as input language.":
                col1, col2 = st.columns([0.2, 0.8])
                
                with col1:
                    target_code = language_names[lang]
                    if target_code in gtts_supported_languages:
                        if st.button("▶️ Play", key=f"play_{lang}"):
                            st.session_state.audio_to_play = (translated, target_code)
                            st.rerun()
                    else:
                        st.markdown("_(Audio N/A)_")
                
                with col2:
                    if st.button("📋 Copy", key=f"copy_{lang}"):
                        st.info("Text copied to clipboard!")
                        st.code(translated, language="plaintext")

        # --- Audio Playback Logic ---
        if st.session_state.audio_to_play:
            translated_text, target_code = st.session_state.audio_to_play
            audio_html = text_to_speech(translated_text, target_code)
            
            if audio_html:
                st.markdown("---")
                st.markdown(f"**Playing audio for {target_code}**")
                st.components.v1.html(audio_html, height=80)
            
            st.session_state.audio_to_play = None

elif mode == "Speech Translator":
    st.markdown("## Translate from audio 🔊")
    selected_languages = st.multiselect("Choose target languages", options=list(language_names.keys()))

    st.markdown("---")
    st.subheader("Option 1: Record your voice")

    if st.button("Start Recording"):
        st.session_state.translations = {}  # Clear previous translations
        st.session_state.audio_file = f"recorded_audio_{uuid.uuid4()}.wav"
        st.session_state.audio_source_type = "mic"
        
        with st.spinner("Recording for 5 seconds..."):
            record_audio_to_file(st.session_state.audio_file)
        
        # Rerun to process the recorded file
        st.rerun()

    st.markdown("---")
    st.subheader("Option 2: Upload an audio file")
    uploaded_file = st.file_uploader("Drag and drop file here", type=["wav", "mp3", "flac"])

    if uploaded_file and st.session_state.audio_file is None:
        st.session_state.translations = {}
        st.session_state.audio_source_type = "file"
        
        # Save uploaded file to session state
        st.session_state.audio_file = f"temp_uploaded_{uuid.uuid4()}.{uploaded_file.name.split('.')[-1]}"
        with open(st.session_state.audio_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.rerun()

    # --- Unified processing logic for both mic and uploaded file ---
    if st.session_state.audio_file and selected_languages:
        with st.spinner("Transcribing and translating... Please wait."):
            temp_file_path = f"temp_audio_{uuid.uuid4()}.wav"

            try:
                # Convert the audio to WAV format for SpeechRecognition
                audio = AudioSegment.from_file(st.session_state.audio_file)
                audio.export(temp_file_path, format="wav")
                
                # Transcribe the audio from the temporary WAV file
                r = sr.Recognizer()
                with sr.AudioFile(temp_file_path) as source:
                    audio_data = r.record(source)
                
                # Use a try-except block to gracefully handle transcription failures
                try:
                    transcribed_text = r.recognize_google(audio_data, language='en-US') 
                    st.success("Transcription successful!")
                    st.markdown(f"**Original Text:** _{transcribed_text}_")
                    st.session_state.translations = {}
                    st.session_state.audio_to_play = None
                    
                    for lang in selected_languages:
                        translated_text, _ = translate_text(transcribed_text, language_names[lang])
                        st.session_state.translations[lang] = translated_text
                    
                    # Clear the temporary audio file from session state and disk
                    os.remove(st.session_state.audio_file)
                    st.session_state.audio_file = None
                    st.session_state.audio_source_type = None
                    st.rerun()

                except sr.UnknownValueError:
                    st.error("Google Speech Recognition could not understand the audio.")
                except sr.RequestError as e:
                    st.error(f"Could not request results from Google Speech Recognition service; {e}")

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
    
    # --- Display Translations for Speech Mode ---
    if st.session_state.translations:
        st.markdown("---")
        st.subheader("Translated Texts")
        for lang in selected_languages:
            translated = st.session_state.translations.get(lang)
            
            if translated is None:
                continue
            
            st.markdown(f"**{lang}**: {translated}")

            if translated != "Same as input language.":
                col1, col2 = st.columns([0.2, 0.8])
                
                with col1:
                    target_code = language_names[lang]
                    if target_code in gtts_supported_languages:
                        if st.button("▶️ Play", key=f"play_{lang}"):
                            st.session_state.audio_to_play = (translated, target_code)
                            st.rerun()
                    else:
                        st.markdown("_(Audio N/A)_")
                
                with col2:
                    if st.button("📋 Copy", key=f"copy_{lang}"):
                        st.info("Text copied to clipboard!")
                        st.code(translated, language="plaintext")

        if st.session_state.audio_to_play:
            translated_text, target_code = st.session_state.audio_to_play
            audio_html = text_to_speech(translated_text, target_code)
            
            if audio_html:
                st.markdown("---")
                st.markdown(f"**Playing audio for {target_code}**")
                st.components.v1.html(audio_html, height=80)
            
            st.session_state.audio_to_play = None