import streamlit as st

from custom_logger import logger
from yt_notes_generator import generate_notes_audio
from utils import TUTORIAL_ONLY, CLASS_LECTURE

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="YouTube AI Notes Generator",
    page_icon="🎬",
    layout="wide",
)

# ---------------- Header ----------------
st.markdown(
    """
    <h1 style='text-align: center;'>🎬 YouTube → AI Notes Generator</h1>
    <p style='text-align: center; font-size:18px;'>
    Convert any YouTube video into clean, structured notes using Gemini AI
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ---------------- Session State ----------------
if "generated_notes" not in st.session_state:
    st.session_state.generated_notes = ""

# ---------------- Layout ----------------
col1, col2 = st.columns([1, 2])

# ================= LEFT PANEL =================
with col1:
    st.subheader("⚙️ Configuration")

    youtube_url = st.text_input(
        "🔗 YouTube URL",
        placeholder="Paste YouTube link here..."
    )

    # Stable free-tier model
    model_name = "gemini-3-flash-preview"
    st.success("🤖 Model: Gemini 3 Flash (Free Tier)")

    system_prompt_option = st.selectbox(
        "💬 Notes Style",
        ["tutorial-only", "class-lecture", "custom"]
    )

    if system_prompt_option == "tutorial-only":
        system_prompt = TUTORIAL_ONLY
    elif system_prompt_option == "class-lecture":
        system_prompt = CLASS_LECTURE
    else:
        system_prompt = st.text_area(
            "✏️ Custom System Prompt",
            "You are an expert educator creating structured notes."
        )

    user_prompt = st.text_area(
        "🗨️ Instruction to AI",
        "Generate well-structured, easy-to-read notes from this transcript."
    )

    generate_button = st.button(
        "🚀 Generate Notes",
        use_container_width=True
    )

    if st.session_state.generated_notes:
        st.download_button(
            label="📥 Download Notes (.md)",
            data=st.session_state.generated_notes,
            file_name="notes.md",
            mime="text/markdown",
            use_container_width=True
        )

# ================= RIGHT PANEL =================
with col2:
    st.subheader("📄 Generated Notes")

    if generate_button:

        if not youtube_url:
            st.warning("⚠️ Please enter a valid YouTube URL.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Step 1: Extract transcript
                status_text.info("📄 Extracting transcript...")
                progress_bar.progress(30)

                response = generate_notes_audio(
                    youtube_url=youtube_url,
                    model_name=model_name,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )

                # Step 2: Generate notes
                status_text.info("🧠 Generating AI notes...")
                progress_bar.progress(70)

                if not response:
                    st.error("❌ Transcript not available or AI failed. Check logs.")
                else:
                    full_response = getattr(response, "text", "")

                    if not full_response.strip():
                        st.error("❌ No notes generated.")
                    else:
                        st.session_state.generated_notes = full_response
                        progress_bar.progress(100)
                        status_text.success("✅ Notes generated successfully!")
                        st.markdown(full_response)

                        logger.info("Notes generated successfully.")

            except Exception as e:
                logger.error(f"App crashed: {str(e)}")
                st.error(f"❌ Error: {str(e)}")

    elif st.session_state.generated_notes:
        st.markdown(st.session_state.generated_notes)

    else:
        st.info("Enter a YouTube URL and click 'Generate Notes'.")

# ---------------- Footer ----------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit + Gemini AI")
