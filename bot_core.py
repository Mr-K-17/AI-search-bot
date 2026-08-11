import os
from dotenv import load_dotenv
import google.generativeai as genai

# -------------------- #
#  Load API Key
# -------------------- #
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ API key not found. Please set GEMINI_API_KEY in your .env file.")

# -------------------- #
#  Configure Gemini
# -------------------- #
genai.configure(api_key=API_KEY)

# -------------------- #
#  Streaming Info Function
# -------------------- #
def stream_info(query: str):
    """
    Streams Gemini's response chunk by chunk for a smoother, faster user experience.
    Designed for integration with Streamlit or terminal apps.
    """

    if not query.strip():
        yield "⚠️ Please provide a valid topic."
        return

    try:
        # Use Gemini 2.5 Flash (fast and free)
        model = genai.GenerativeModel("models/gemini-2.5-flash")

        # Prompt for concise educational explanation
        prompt = (
            f"""You are a knowledgeable AI assistant that provides safe, factual, and educational information.
        Follow these rules:
        - Only provide factual and safe information.
        - If the topic is harmful, controversial, or inappropriate, politely refuse to answer.
        - Do not generate code, opinions, or speculation unless requested clearly.
        - Give a detailed and comprehensive answer.
        - Use clear, easy-to-understand language.

        Topic: '{query}'
        """
        )

        # Stream the response (piece by piece)
        response = model.generate_content(prompt, stream=True)

        for chunk in response:
            if chunk.text:
                yield chunk.text  # Send out each chunk immediately

        response.resolve()

    except Exception as e:
        yield f"❌ Error while fetching information: {str(e)}"


# -------------------- #
#  Debug Mode (for terminal testing)
# -------------------- #
if __name__ == "__main__":
    topic = input("Enter a topic: ")
    print("\n--- Gemini's Response ---\n")
    for text in stream_info(topic):
        print(text, end="", flush=True)
    print("\n--------------------------")
