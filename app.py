import streamlit as st
from agent import run_agent_stream

st.set_page_config(page_title="Study Agent Pro", page_icon="🎓", layout="centered")

# --- Updated CSS: Low input bar, standard header, and text overflow prevention ---
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;700;800&display=swap');

[data-testid="stHeader"] { display: none !important; }

/* Vibrant and pleasant purple-lilac background */
.stApp {
    background: linear-gradient(135deg, #1e1136 0%, #2d184f 50%, #1e1136 100%) !important;
    font-family: 'Heebo', sans-serif !important;
    color: #ffffff !important;
}

/* General right-to-left (RTL) alignment */
p, h1, h2, h3, .stMarkdown {
    direction: rtl !important;
    text-align: right !important;
}

/* Bottom padding - reduced to allow the input bar to sit lower */
.block-container {
    padding-bottom: 90px !important;
}

/* --- Centered captivating headers (no sticky effect!) --- */
.title-container { 
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    margin-top: 10px; margin-bottom: 40px; text-align: center;
}
.title-main {
    background: -webkit-linear-gradient(45deg, #00f3ff, #b088f9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-size: 4rem; font-weight: 800; margin: 0 auto !important; display: inline-block;
    text-shadow: 0px 0px 20px rgba(176, 136, 249, 0.4);
}
.subtitle-main { color: #d8b4fe !important; font-size: 1.2rem; margin-top: 5px; text-align: center !important;}

/* --- Chat bubbles and icons arrangement --- */
[data-testid="stChatMessage"] {
    display: flex !important;
    align-items: flex-end !important; /* Icons aligned to the bottom (bubble tail)! */
    background-color: transparent !important;
    border: none !important; padding: 0 !important; margin-bottom: 35px !important;
}

[data-testid="stChatMessageAvatarUser"], 
[data-testid="stChatMessageAvatarAssistant"] {
    background-color: transparent !important; width: 55px !important; height: 55px !important;
}
[data-testid="stChatMessageAvatarUser"] svg, 
[data-testid="stChatMessageAvatarAssistant"] svg {
    width: 40px !important; height: 40px !important;
}

/* 1. User bubble (Miri) */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse !important; 
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .stMarkdown {
    background: rgba(176, 136, 249, 0.15) !important;
    border: 1.5px solid #b088f9 !important;
    border-radius: 20px 20px 0px 20px !important; 
    box-shadow: 0 0 15px rgba(176, 136, 249, 0.3) !important; 
    max-width: 80%; padding: 15px 25px !important;
    margin-left: auto !important; margin-right: 12px !important;
}

/* 2. Bot bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    flex-direction: row !important; 
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) .stMarkdown {
    background: rgba(0, 243, 255, 0.1) !important;
    border: 1.5px solid #00f3ff !important; 
    border-radius: 20px 20px 20px 0px !important; 
    box-shadow: 0 0 15px rgba(0, 243, 255, 0.25) !important; 
    max-width: 80%; padding: 15px 25px !important;
    margin-right: auto !important; margin-left: 12px !important;
}

[data-testid="stChatMessage"] .stMarkdown p, [data-testid="stChatMessage"] .stMarkdown li {
    color: #ffffff !important; font-size: 1.15rem !important; line-height: 1.7 !important;
}

/* --- Fix for text leaking under the input bar (with low bar!) --- */
[data-testid="stBottom"] { 
    background-color: #1e1136 !important; 
    box-shadow: 0px -30px 40px #1e1136 !important; /* The shadow that creates the masking effect */
    z-index: 99;
}
[data-testid="stBottom"] > div {
    background: transparent !important; 
    padding-bottom: 5px !important; /* Pushed the input bar completely to the bottom */
    padding-top: 10px !important;
}
[data-testid="stChatInput"] { background: transparent !important; }
[data-testid="stChatInput"] > div {
    background-color: rgba(30, 17, 54, 0.95) !important; 
    border: 2px solid #b088f9 !important;
    border-radius: 30px !important;
    direction: rtl !important;
    box-shadow: 0 0 15px rgba(176, 136, 249, 0.2) !important; 
}
[data-testid="stChatInput"] textarea { color: #ffffff !important; font-size: 1.1rem !important;}
[data-testid="stChatInput"] textarea::placeholder { color: #b088f9 !important; opacity: 0.8 !important; }

/* Light blue submit button */
[data-testid="stChatInputSubmitButton"]:hover, 
[data-testid="stChatInputSubmitButton"]:focus, 
[data-testid="stChatInputSubmitButton"]:active,
[data-testid="stChatInputSubmitButton"] {
    color: #00f3ff !important; background-color: transparent !important;
}
[data-testid="stChatInputSubmitButton"] svg { fill: #00f3ff !important; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Headers without sticky effect
st.markdown("""
<div class='title-container'>
    <h1 class='title-main'>Study Agent Pro</h1>
    <p class='subtitle-main'>העוזר האישי שלך לתקשורת מחשבים&rlm;</p>
</div>
""", unsafe_allow_html=True)

USER_AVATAR = "user"
AI_AVATAR = "assistant"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "היי! המערכות מוכנות. איזה נושא נלמד היום?"}
    ]

for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else AI_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("הקלידי כאן שאלות..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AI_AVATAR):
        message_placeholder = st.empty()
        
        # Natural thinking animation
        message_placeholder.markdown("⏳ מחפש בסיכומים...")
        
        try:
            full_response = ""
            for chunk in run_agent_stream(st.session_state.messages):
                full_response += chunk
                message_placeholder.markdown(full_response + " ▌")
                
            message_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"❌ שגיאה: {e}"
            message_placeholder.markdown(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})