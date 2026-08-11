import streamlit as st
from bot_core import stream_info  # ✅ use streaming version

st.set_page_config(page_title="AI Info Bot", page_icon="🤖", layout="centered")

# --- Custom CSS for Theme ---
st.markdown(
    """
    <style>
    body {
        background-color: #F9FAFB;
        color: #222;
        font-family: "Segoe UI", sans-serif;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 1px solid #999;
        padding: 10px;
        font-size: 16px;
    }
    .stButton>button {
        background-color: #0078D7;
        color: white;
        border-radius: 8px;
        padding: 8px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #005EA6;
        transform: scale(1.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Header Section ---
st.markdown(
    """
    <div style="text-align:center; padding:20px;">
        <h1 style="color:#0078D7;">🤖 AI Info Bot</h1>
        <p style="font-size:18px;">Your personal knowledge assistant powered by <b>Google Gemini</b></p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Sidebar Info ---
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    **AI Info Bot** explains any topic in seconds using **Gemini 2.5 Flash**.  
    Built by **Team Name Unknown** ✨  
    """)

# --- Main Input Area ---
query = st.text_input("🔍 Enter your topic:", placeholder="e.g., What is Deep Learning?")

if st.button("Search"):
    if not query:
        st.warning("Please type something before clicking search.")
    else:
        st.markdown("### 📘 Information:")

        # Placeholder for live updates
        placeholder = st.empty()
        response_text = ""

        with st.spinner("🤖 Thinking..."):
            # Stream Gemini's chunks as they arrive
            for chunk in stream_info(query):
                response_text += chunk
                placeholder.markdown(
                    f"""
                    <div style="
                        background-color:#f0f0f0;
                        padding:20px;
                        border-radius:10px;
                        border:1px solid #ccc;
                        color:#222;
                        font-size:16px;
                        line-height:1.6;
                    ">
                        {response_text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

st.markdown("---")
st.caption("Made with ❤️ using Streamlit and Google Gemini API")
