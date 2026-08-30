
import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from youtube_transcript_api import YouTubeTranscriptApi

from .state import YoutubeState
from .utils import extract_video_id
from .prompts import (
    CHUNK_SUMMARY_PROMPT,
    FINAL_SUMMARY_PROMPT,
    get_summary_instruction,
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# CREATE LLM
# ============================================================

def get_llm():
    """
    Create the Groq LLM.

    The API key is loaded from the .env file.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not configured. "
            "Please add it to your .env file."
        )

    return ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=api_key,
        temperature=0,
    )


# ============================================================
# FETCH TRANSCRIPT NODE
# ============================================================

def fetch_transcript_node(state: YoutubeState) -> dict:
    """
    Fetch the English transcript from YouTube.
    """

    video_id = extract_video_id(
        state["url"]
    )

    ytt = YouTubeTranscriptApi()

    transcript = ytt.fetch(
        video_id,
        languages=["en"],
    )

    # youtube-transcript-api returns FetchedTranscriptSnippet
    # objects, therefore we use item.text.
    full_text = " ".join(
        item.text
        for item in transcript
    )

    if not full_text.strip():
        raise ValueError(
            "The YouTube transcript is empty."
        )

    return {
        "video_id": video_id,
        "transcript": full_text,
    }


# ============================================================
# SPLIT TRANSCRIPT
# ============================================================

def split_transcript(
    text: str,
    max_chars: int = 12000,
) -> list[str]:
    """
    Split a long transcript into smaller chunks.
    """

    words = text.split()

    chunks = []

    current_chunk = []
    current_length = 0

    for word in words:

        word_length = len(word) + 1

        if (
            current_length + word_length > max_chars
            and current_chunk
        ):

            chunks.append(
                " ".join(current_chunk)
            )

            current_chunk = []
            current_length = 0

        current_chunk.append(word)
        current_length += word_length

    if current_chunk:
        chunks.append(
            " ".join(current_chunk)
        )

    return chunks


# ============================================================
# SUMMARIZATION NODE
# ============================================================

def summarize_node(state: YoutubeState) -> dict:
    """
    Summarize the transcript using Groq.
    """

    llm = get_llm()

    style = state.get(
        "summary_style",
        "Detailed",
    )

    instruction = get_summary_instruction(
        style
    )

    transcript = state["transcript"]

    chunks = split_transcript(
        transcript
    )

    # --------------------------------------------------------
    # Summarize each transcript chunk
    # --------------------------------------------------------

    chunk_chain = (
        CHUNK_SUMMARY_PROMPT
        | llm
    )

    chunk_summaries = []

    for chunk in chunks:

        response = chunk_chain.invoke(
            {
                "instruction": instruction,
                "transcript": chunk,
            }
        )

        chunk_summaries.append(
            response.content
        )

    # --------------------------------------------------------
    # Combine summaries
    # --------------------------------------------------------

    combined_summaries = "\n\n".join(
        chunk_summaries
    )

    # --------------------------------------------------------
    # Generate final summary
    # --------------------------------------------------------

    final_chain = (
        FINAL_SUMMARY_PROMPT
        | llm
    )

    final_response = final_chain.invoke(
        {
            "instruction": instruction,
            "summaries": combined_summaries,
        }
    )

    return {
        "summary": final_response.content
    }


# ============================================================
# BUILD LANGGRAPH
# ============================================================

def build_graph():
    """
    Build the YouTube summarization LangGraph.

    Workflow:

        START
          ↓
        Fetch Transcript
          ↓
        Summarize
          ↓
        END
    """

    builder = StateGraph(
        YoutubeState
    )

    # --------------------------------------------------------
    # Add Nodes
    # --------------------------------------------------------

    builder.add_node(
        "fetch_transcript",
        fetch_transcript_node,
    )

    builder.add_node(
        "summarize",
        summarize_node,
    )

    # --------------------------------------------------------
    # Add Edges
    # --------------------------------------------------------

    builder.add_edge(
        START,
        "fetch_transcript",
    )

    builder.add_edge(
        "fetch_transcript",
        "summarize",
    )

    builder.add_edge(
        "summarize",
        END,
    )

    # --------------------------------------------------------
    # Compile
    # --------------------------------------------------------

    return builder.compile()


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def summarize_youtube(
    url: str,
    summary_style: str = "Detailed",
) -> dict:
    """
    Public function used by Streamlit.

    Parameters:
        url:
            YouTube video URL.

        summary_style:
            Short, Detailed or Academic.

    Returns:
        Final LangGraph state.
    """

    graph = build_graph()

    result = graph.invoke(
        {
            "url": url,
            "summary_style": summary_style,
        }
    )

    return result
