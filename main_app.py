import streamlit as st
from bot_core import stream_info
import html
import re

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Info Bot", page_icon="🤖", layout="wide")

# ------------- SESSION INIT -------------
if "conversations" not in st.session_state:
    st.session_state.conversations = {"New Chat": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Chat"
if "rename_mode" not in st.session_state:
    st.session_state.rename_mode = None
if "delete_mode" not in st.session_state:
    st.session_state.delete_mode = None

# ----------- HTML ESCAPE (SECURITY) -----------
def escape_text(text: str) -> str:
    """Escape HTML tags to prevent injection."""
    return html.escape(text or "")

# ----------- AUTO CHAT NAMING -----------
def generate_chat_name(user_message: str) -> str:
    """
    Generate a meaningful chat name from the user's first message.
    Takes first 3-5 words or limits to 30 characters.
    """
    # Clean the message
    cleaned = user_message.strip()
    
    # Split into words
    words = cleaned.split()
    
    # Take first 3-5 words (or fewer if message is short)
    if len(words) <= 3:
        name = " ".join(words)
    elif len(words) <= 5:
        name = " ".join(words[:4])
    else:
        name = " ".join(words[:3])
    
    # Limit to 30 characters
    if len(name) > 30:
        name = name[:27] + "..."
    
    # Capitalize first letter
    name = name.capitalize()
    
    # Ensure uniqueness
    base_name = name
    counter = 1
    while name in st.session_state.conversations:
        name = f"{base_name} ({counter})"
        counter += 1
    
    return name

# -------------- CUSTOM CSS --------------
st.markdown("""
<style>
body { background-color: #111; color: #e5e5e5; font-family: 'Segoe UI', sans-serif; }
.user-bubble {
    align-self: flex-end; background-color: #0078D7; color: white;
    padding: 10px 15px; border-radius: 15px 15px 0 15px;
    margin: 5px; max-width: 75%; word-wrap: break-word;
}
.bot-bubble {
    align-self: flex-start; background-color: #333; color: #f0f0f0;
    padding: 10px 15px; border-radius: 15px 15px 15px 0;
    margin: 5px; max-width: 75%; word-wrap: break-word;
}
.stButton>button {
    background-color: #0078D7; color: white; border: none;
    border-radius: 8px; padding: 4px 8px; font-size: 16px; transition: 0.3s;
}
.stButton>button:hover { background-color: #005EA6; transform: scale(1.05); }
.sidebar-chat-item:hover { background-color: #2a2a2a; }
</style>
""", unsafe_allow_html=True)

# -------------- SIDEBAR --------------
with st.sidebar:
    st.header("💬 Saved Chats (Session Only)")
    
    # Create new chat safely (unique name)
    if st.button("+ New Chat", use_container_width=True):
        base = "New Chat"
        new_name = base
        counter = 1
        while new_name in st.session_state.conversations:
            new_name = f"{base} {counter}"
            counter += 1
        st.session_state.conversations[new_name] = []
        st.session_state.current_chat = new_name
        st.rerun()
    
    chats = list(st.session_state.conversations.keys())
    
    # Render chat list
    for chat in chats:
        cols = st.columns([6, 2, 2])
        with cols[0]:
            if st.button(chat, key=f"open_{chat}"):
                st.session_state.current_chat = chat
                st.rerun()
        with cols[1]:
            if st.button("✏️", key=f"rename_{chat}"):
                st.session_state.rename_mode = chat
                st.session_state.delete_mode = None
                st.rerun()
        with cols[2]:
            if st.button("🗑️", key=f"delete_{chat}"):
                st.session_state.delete_mode = chat
                st.session_state.rename_mode = None
                st.rerun()
    
    # Rename logic (safe)
    if st.session_state.rename_mode:
        old = st.session_state.rename_mode
        new_name = st.text_input("Rename Chat:", value=old, key="rename_input")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm"):
                trimmed = new_name.strip()
                if not trimmed:
                    st.warning("Chat name cannot be empty.")
                elif trimmed == old:
                    st.info("Name unchanged.")
                elif trimmed in st.session_state.conversations:
                    st.warning("Name already exists.")
                else:
                    st.session_state.conversations[trimmed] = st.session_state.conversations.pop(old)
                    st.session_state.current_chat = trimmed
                st.session_state.rename_mode = None
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.rename_mode = None
                st.rerun()
    
    # Delete confirmation (bug-free)
    if st.session_state.delete_mode:
        chat_to_delete = st.session_state.delete_mode
        st.warning(f"Delete chat '{chat_to_delete}'? This cannot be undone.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Confirm Delete"):
                if chat_to_delete in st.session_state.conversations:
                    st.session_state.conversations.pop(chat_to_delete)
                # Ensure at least one valid chat exists
                if not st.session_state.conversations:
                    st.session_state.conversations["New Chat"] = []
                    st.session_state.current_chat = "New Chat"
                else:
                    # Move to the most recent remaining chat
                    st.session_state.current_chat = list(st.session_state.conversations.keys())[-1]
                st.session_state.delete_mode = None
                st.rerun()
        with col2:
            if st.button("Cancel"):
                st.session_state.delete_mode = None
                st.rerun()

# -------------- MAIN CHAT DISPLAY --------------
st.title("🤖 AI Info Bot")
st.caption("Powered by Google Gemini API — session memory only")


def clean_text_for_download(text: str) -> str:
    """
    Removing markdown symbols, HTML tags, and extra whitespace.
    Returns plain readable text.
    """
    # Remove markdown bullets, asterisks, underscores, and backticks
    text = re.sub(r'[*_`#>~-]+', '', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Replace multiple newlines/spaces with single newline
    text = re.sub(r'\n\s*\n', '\n\n', text.strip())
    return text.strip()


chat_history = st.session_state.conversations.get(st.session_state.current_chat, [])

# Render previous messages
for i, msg in enumerate(chat_history):
    role = msg.get("role")
    content = escape_text(msg.get("content", ""))

    if role == "user":
        st.markdown(f"<div class='user-bubble'>{content}</div>", unsafe_allow_html=True)

    elif role == "bot":
        st.markdown(f"<div class='bot-bubble'>{content}</div>", unsafe_allow_html=True)

        # Adding download button for the most recent bot response
        if i == len(chat_history) - 1:
            bot_response = msg.get("content", "").strip()

            # 🧩 Clean & format
            formatted_response = (
                f"🤖 AI Info Bot — Gemini Response\n"
                f"{'='*40}\n\n"
                f"Topic: {st.session_state.current_chat}\n\n"
                f"Response:\n{clean_text_for_download(bot_response)}\n\n"
                f"{'-'*40}\nGenerated using Google Gemini API"
            )

            st.download_button(
                label="⬇️ Download This Response",
                data=formatted_response,
                file_name=f"{st.session_state.current_chat.replace(' ', '_')}_response.txt",
                mime="text/plain",
                key=f"download_{i}"
            )

# Create a temporary placeholder *below* chat container for streaming only
temp_stream_area = st.empty()

# -------------- INPUT AREA --------------
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_area("Message:", key="user_input", height=80, placeholder="Message AI Info Bot...")
    send_pressed = st.form_submit_button("Send")

# -------------- MESSAGE HANDLING --------------
if send_pressed and user_input.strip():
    user_input = user_input.strip()
    
    # Check if this is the first message in the current chat
    current_chat_history = st.session_state.conversations.get(st.session_state.current_chat, [])
    is_first_message = len(current_chat_history) == 0
    
    # Auto-rename "New Chat" to meaningful name based on first message
    if is_first_message and st.session_state.current_chat.startswith("New Chat"):
        old_name = st.session_state.current_chat
        new_name = generate_chat_name(user_input)
        
        # Rename the chat
        st.session_state.conversations[new_name] = st.session_state.conversations.pop(old_name)
        st.session_state.current_chat = new_name
    
    # Add user message
    st.session_state.conversations.setdefault(st.session_state.current_chat, []).append({
        "role": "user",
        "content": user_input,
    })
    
    # Stream Gemini response inside placeholder (inside chat container)
    response_text = ""
    with st.spinner("🤖 Thinking..."):
        for chunk in stream_info(user_input):
            response_text += chunk
            temp_stream_area.markdown(
                f"""
                <div style='background-color:#333; color:#f0f0f0;
                            padding:10px 15px; border-radius:15px; margin:5px;'>
                    {escape_text(response_text)}
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Add bot response to history (for persistence within session)
    st.session_state.conversations[st.session_state.current_chat].append({
        "role": "bot",
        "content": response_text,
    })
    # --- Download button for AI response ---
    st.download_button(
        label="⬇️ Download Response",
        data=response_text,
        file_name=f"{st.session_state.current_chat.replace(' ', '_')}_response.txt",
        mime="text/plain",
        help="Download this AI-generated response as a text file"
    )

    # Rerun after display
    st.rerun()

# -------------- FOOTER --------------
st.markdown("---")
st.caption("Made with ❤️ using Streamlit and Google Gemini API (Session-based)")