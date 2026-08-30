
import re


def extract_video_id(url: str) -> str:
    """
    Extract the YouTube video ID from a YouTube URL.

    Supported formats:
        https://www.youtube.com/watch?v=VIDEO_ID
        https://youtu.be/VIDEO_ID
        https://www.youtube.com/shorts/VIDEO_ID
        https://www.youtube.com/embed/VIDEO_ID
    """

    if not url:
        raise ValueError("YouTube URL cannot be empty.")

    url = url.strip()

    patterns = [
        r"(?:youtube\.com/watch\?v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)

        if match:
            return match.group(1)

    # Allow direct video ID
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url

    raise ValueError(
        "Invalid YouTube URL. Please enter a valid YouTube video URL."
    )

