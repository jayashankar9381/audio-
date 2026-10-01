import os
import streamlit as st
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from googletrans import Translator
import io
import pypdf

# .env నుండి API కీ లోడ్ చేయడం
load_dotenv()

# పేజీ సెటప్ (Wide Layout)
st.set_page_config(
    page_title="AI వాయిస్ ట్రాన్స్‌లేటర్ & స్టూడియో",
    page_icon="🎙️",
    layout="centered"
)

# డిజైన్ స్టైలింగ్
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #4f46e5; color: white; border-radius: 12px; font-weight: bold; height: 3.2em; }
    .stButton>button:hover { background-color: #4338ca; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #6366f1;'>🎙️ ఆటోమేటిక్ AI ట్రాన్స్‌లేటర్ & వాయిస్ స్టూడియో</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>టెక్స్ట్ ఇవ్వండి లేదా PDF అప్‌లోడ్ చేయండి -> ఆటోమేటిక్‌గా వేరే భాషలోకి మారి -> మనుషుల వాయిస్‌లా మారుతుంది!</p>", unsafe_allow_html=True)

# ElevenLabs మరియు Translator ఇనిషియలైజేషన్
api_key = os.getenv("ELEVENLABS_API_KEY", "YOUR_ACTUAL_API_KEY_HERE")
elevenlabs = ElevenLabs(api_key=api_key)
translator = Translator()

# వాయిస్ IDs
VOICE_MAP = {
    "ప్రశాంతమైన మగ వాయిస్ (George - Natural)": "JBFqnCBsd6RMkjVDRZzb",
    "ప్రొఫెషనల్ న్యూస్ వాయిస్ (Adam)": "21m00Tcm4TlvDq8ikWAM",
    "మృదువైన ఆడ వాయిస్ (Rachel - Natural)": "EXAVITQu4vr4xnSDxMaL",
    "కార్పొరేట్ ఆడ వాయిస్ (Elli)": "MF3mGyEYCl7XYWbV9V6O",
    "స్టోరీ టెల్లర్ (Josh)": "TxGEqnHWrfWFTfGW9XjX",
    "⭐ మీ సొంత వాయిస్ (Custom Cloned Voice ID)": "YOUR_CUSTOM_VOICE_ID_HERE"
}

# లాంగ్వేజ్ కోడ్స్ మ్యాపింగ్
LANG_MAP = {
    "తెలుగు (Telugu)": "te",
    "हिंदी (Hindi)": "hi",
    "മലയാളം (Malayalam)": "ml",
    "ಕನ್ನಡ (Kannada)": "kn",
    "தமிழ் (Tamil)": "ta",
    "English": "en"
}

# 1. PDF లేదా టెక్స్ట్ ఇన్‌పుట్
uploaded_file = st.file_uploader("📂 PDF ఫైల్ అప్‌లోడ్ చేయండి (పుస్తకాలు / డాక్యుమెంట్స్)", type=["pdf"])

source_text = ""
if uploaded_file is not None:
    try:
        reader = pypdf.PdfReader(uploaded_file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                source_text += extracted + "\n"
        st.success("✅ PDF ఫైల్ విజయవంతంగా రీడ్ చేయబడింది!")
    except Exception as e:
        st.error(f"PDF రీడింగ్ లోపం: {e}")

# టెక్స్ట్ బాక్స్
user_text = st.text_area("✍️ మీ టెక్స్ట్ ఇక్కడ టైప్ చేయండి లేదా PDF టెక్స్ట్ నివారించండి:", value=source_text, height=150)

# 2. లాంగ్వేజ్ మరియు వాయిస్ సెలెక్షన్
col1, col2 = st.columns(2)
with col1:
    selected_lang_name = st.selectbox("ఏ భాషలోకి మార్చాలి? (Translate To):", list(LANG_MAP.keys()))
with col2:
    selected_voice_name = st.selectbox("వాయిస్ స్టైల్ (Human Voice):", list(VOICE_MAP.keys()))

# 3. జనరేట్ బటన్
if st.button("🚀 టెక్స్ట్ అనువదించి, వాయిస్‌గా మార్చండి"):
    if not user_text.strip():
        st.warning("⚠️ దయచేసి టెక్స్ట్ ఎంటర్ చేయండి లేదా PDF అప్‌లోడ్ చేయండి!")
    else:
        with st.spinner("⏳ టెక్స్ట్ అనువాదం మరియు AI వాయిస్ జనరేషన్ జరుగుతోంది... దయచేసి వేచి ఉండండి..."):
            try:
                target_lang_code = LANG_MAP[selected_lang_name]
                
                # స్టెప్ 1: గూగుల్ ద్వారా ఆటోమేటిక్ ట్రాన్స్‌లేషన్
                translation = translator.translate(user_text[:3000], dest=target_lang_code)
                translated_text = translation.text
                
                st.info(f"🌐 **అనువదించబడిన టెక్స్ట్ ({selected_lang_name}):**\n\n {translated_text[:400]}...")

                # స్టెప్ 2: ElevenLabs ద్వారా మనుషుల వాయిస్ ఓవర్ జనరేట్ చేయడం
                voice_id = VOICE_MAP[selected_voice_name]
                
                audio_stream = elevenlabs.text_to_speech.convert(
                    text=translated_text,
                    voice_id=voice_id,
                    model_id="eleven_multilingual_v2",  # బహుళ భాషలను అద్భుతంగా సపోర్ట్ చేస్తుంది
                    output_format="mp3_44100_128",
                )
                
                audio_bytes = io.BytesIO()
                for chunk in audio_stream:
                    audio_bytes.write(chunk)
                audio_bytes.seek(0)
                
                st.success("🎉 ఆడియో విజయవంతంగా తయారైంది!")
                
                # ఆడియో ప్లేయర్
                st.audio(audio_bytes, format="audio/mp3")
                
                # డైరెక్ట్ డౌన్‌లోడ్ బటన్
                st.download_button(
                    label="📥 ఆడియో ఫైల్‌ని డౌన్‌లోడ్ చేసుకోండి (.mp3)",
                    data=audio_bytes,
                    file_name=f"voiceover_{target_lang_code}.mp3",
                    mime="audio/mp3"
                )
                
            except Exception as e:
                st.error(f"❌ లోపం సంభవించింది: {e}")
