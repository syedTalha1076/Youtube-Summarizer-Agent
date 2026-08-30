
from typing import TypedDict


class YoutubeState(TypedDict, total=False):
    """
    State shared between nodes in the LangGraph workflow.
    """

    url: str
    video_id: str
    transcript: str
    summary: str
    error: str

