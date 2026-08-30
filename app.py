import streamlit as st

from src.youtube_summarizer_agent.agent import summarize_youtube
from src.youtube_summarizer_agent.utils import extract_video_id


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="YouTube Summarizer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

defaults = {
    "summary": None,
    "transcript": None,
    "video_id": None,
    "video_url": "",
    "history": [],
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

st.markdown("""
<style>
.block-container {
    max-width: 1080px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* Hero header */
.hero {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 60%, #db2777 100%);
    border-radius: 18px;
    padding: 2.2rem 2.4rem;
    color: white;
    margin-bottom: 1.8rem;
    box-shadow: 0 10px 30px rgba(79, 70, 229, 0.25);
}
.hero h1 {
    font-size: 2.1rem;
    font-weight: 800;
    margin: 0 0 0.4rem 0;
    color: white;
}
.hero p {
    font-size: 1.02rem;
    opacity: 0.92;
    margin: 0;
}

/* Section labels */
.section-label {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #7c3aed;
    margin-bottom: 0.4rem;
}

/* Cards */
.card {
    background: #ffffff08;
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1.2rem;
}

/* Result title */
.result-title {
    font-size: 1.5rem;
    font-weight: 800;
    margin-bottom: 0.6rem;
}

/* Footer */
.footer {
    text-align: center;
    margin-top: 3rem;
    padding-top: 1.2rem;
    border-top: 1px solid rgba(148, 163, 184, 0.25);
    color: #94a3b8;
    font-size: 0.82rem;
}

/* Buttons */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 🎬 YouTube Summarizer")
    st.caption("Turn long videos into a quick, readable summary.")

    st.divider()
    st.markdown("#### Summary style")
    summary_style = st.selectbox(
        "Select a style",
        ["Short", "Detailed", "Academic"],
        index=1,
        help="Choose how detailed you want the generated summary.",
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("#### How it works")
    st.markdown(
        "1. Paste a YouTube link\n"
        "2. We pull the transcript\n"
        "3. LangGraph orchestrates the pipeline\n"
        "4. Groq writes the summary"
    )

    st.divider()
    if st.button("🗑️ Clear session", use_container_width=True):
        for key, value in defaults.items():
            st.session_state[key] = value
        st.rerun()

    st.divider()
    st.caption("Built by Syed Talha Ali Shah · UET Peshawar")


# ---------------------------------------------------------------------------
# Hero header
# ---------------------------------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>YouTube Summarizer</h1>
    <p>Paste a link, and get the key ideas, explanations and takeaways
    from any video — without watching the whole thing.</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

st.markdown('<div class="section-label">Video link</div>', unsafe_allow_html=True)

youtube_url = st.text_input(
    "YouTube URL",
    value=st.session_state.video_url,
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed",
)
st.caption("Works best on videos with an available English transcript.")

summarize_button = st.button("✨ Summarize Video", type="primary", use_container_width=True)


# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------

if summarize_button:
    if not youtube_url.strip():
        st.warning("Please paste a YouTube URL first.")
    else:
        try:
            video_id = extract_video_id(youtube_url)
            st.session_state.video_url = youtube_url

            with st.spinner("Fetching transcript and generating summary..."):
                result = summarize_youtube(youtube_url, summary_style)

            st.session_state.video_id = video_id
            st.session_state.transcript = result.get("transcript")
            st.session_state.summary = result.get("summary")

            st.session_state.history.insert(0, {
                "video_id": video_id,
                "url": youtube_url,
                "summary": result.get("summary", ""),
            })
            st.session_state.history = st.session_state.history[:10]

            st.success("Summary generated successfully.")

        except Exception as e:
            st.error(f"Unable to summarize this video: {e}")


# ---------------------------------------------------------------------------
# Summary display
# ---------------------------------------------------------------------------

if st.session_state.summary:
    st.divider()
    st.markdown('<div class="result-title">📝 Summary</div>', unsafe_allow_html=True)

    info1, info2, info3 = st.columns(3)
    with info1:
        st.caption("Video ID")
        st.code(st.session_state.video_id)
    with info2:
        st.caption("Summary style")
        st.write(summary_style)
    with info3:
        transcript_length = len(st.session_state.transcript or "")
        st.caption("Transcript size")
        st.write(f"{transcript_length:,} characters")

    st.write("")
    st.markdown(st.session_state.summary)
    st.write("")

    st.download_button(
        label="⬇️ Download Summary",
        data=st.session_state.summary,
        file_name="youtube_summary.md",
        mime="text/markdown",
    )


# ---------------------------------------------------------------------------
# Transcript
# ---------------------------------------------------------------------------

if st.session_state.transcript:
    st.divider()
    with st.expander("📄 View transcript"):
        st.text_area(
            "Retrieved transcript",
            st.session_state.transcript,
            height=350,
            label_visibility="collapsed",
        )
        st.download_button(
            label="⬇️ Download Transcript",
            data=st.session_state.transcript,
            file_name="youtube_transcript.txt",
            mime="text/plain",
        )


# ---------------------------------------------------------------------------
# Recent history
# ---------------------------------------------------------------------------

if st.session_state.history:
    st.divider()
    st.markdown("### 🕘 Recent videos")

    for number, item in enumerate(st.session_state.history):
        with st.expander(f"{number + 1}. {item['video_id']}"):
            st.caption(item["url"])
            st.markdown(item["summary"])


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown("""
<div class="footer">
    YouTube Summarizer · Built with LangGraph, LangChain & Groq
</div>
""", unsafe_allow_html=True)