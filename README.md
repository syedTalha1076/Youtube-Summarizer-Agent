# YouTube Summarizer Agent

A simple AI-powered application that summarizes YouTube videos from their transcripts.

The project uses **LangGraph** to organize the workflow, **YouTube Transcript API** to retrieve the video transcript, and **Groq** through LangChain to generate the final summary. A **Streamlit** interface is provided so the application can be used directly from a web browser.

---

## About the Project

I built this project to practice building a practical **Agentic AI application** using LangGraph.

Instead of sending a YouTube video directly to an LLM, the application follows a small workflow:

```text
YouTube URL
     ↓
Extract Video ID
     ↓
Fetch Transcript
     ↓
Process Transcript
     ↓
Generate Summary
     ↓
Display Result
```

The main purpose is to make long YouTube videos easier to understand without manually watching the entire video when only the main ideas are needed.

---

## Features

* Summarize YouTube videos from their URLs
* Automatically extract the YouTube video ID
* Retrieve available English transcripts
* Process long transcripts in smaller sections
* Generate AI-powered summaries
* Three summary styles:

  * Short
  * Detailed
  * Academic
* View the retrieved transcript
* Download the generated summary
* Download the transcript
* Keep recent summaries during the current session
* Clear session history
* Simple Streamlit interface
* LangGraph-based workflow

---

## Project Architecture

The application is divided into separate components instead of putting everything into one Python file.

```text
youtube-summarizer-agent/
│
├── app.py
│
├── .env
│
├── requirements.txt
│
├── README.md
│
└── src/
    │
    ├── __init__.py
    ├── agent.py
    ├── prompts.py
    ├── state.py
    └── utils.py
```

### File Description

| File               | Description                                 |
| ------------------ | ------------------------------------------- |
| `app.py`           | Streamlit frontend and user interface       |
| `agent.py`         | LangGraph workflow and LLM logic            |
| `prompts.py`       | Prompts used for transcript summarization   |
| `state.py`         | Defines the state shared by LangGraph nodes |
| `utils.py`         | YouTube URL and video ID utilities          |
| `.env`             | Stores the Groq API key                     |
| `requirements.txt` | Python dependencies                         |
| `README.md`        | Project documentation                       |

---

## LangGraph Workflow

The core workflow is intentionally simple:

```text
                ┌─────────┐
                │  START  │
                └────┬────┘
                     │
                     ▼
          ┌─────────────────────┐
          │  Fetch Transcript   │
          │                     │
          │ YouTube Transcript  │
          │       API           │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │      Summarize      │
          │                     │
          │      Groq LLM       │
          └──────────┬──────────┘
                     │
                     ▼
                ┌─────────┐
                │   END   │
                └─────────┘
```

The project state contains information such as:

```python
class YoutubeState(TypedDict, total=False):
    url: str
    video_id: str
    transcript: str
    summary: str
    error: str
```

Each LangGraph node reads information from the state and returns the information needed by the next step.

---

## How It Works

### 1. User enters a YouTube URL

The user pastes a YouTube video URL into the Streamlit application.

For example:

```text
https://www.youtube.com/watch?v=XXXXXXXXXXX
```

The application validates the URL and extracts the video ID.

---

### 2. Transcript is retrieved

The application uses:

```text
youtube-transcript-api
```

to retrieve the available English transcript.

The transcript is then converted into one text string for processing.

---

### 3. Long transcripts are divided

Very long transcripts can contain a large amount of text.

To avoid sending an unnecessarily large request to the LLM, the transcript is divided into manageable sections.

Each section is summarized separately.

---

### 4. Section summaries are combined

The individual summaries are combined and sent to the final summarization prompt.

The LLM then produces one coherent summary.

---

### 5. Result is displayed

The final result is displayed in the Streamlit application.

The user can also download:

```text
youtube_summary.md
```

and:

```text
youtube_transcript.txt
```

---

## Technologies Used

### Python

The main programming language used for the project.

### Streamlit

Used to build the web interface.

### LangGraph

Used to create and execute the summarization workflow.

### LangChain

Used for prompts and integration with the language model.

### Groq

Used to run the language model used for summarization.

### YouTube Transcript API

Used to retrieve available transcripts from YouTube videos.

### python-dotenv

Used to load environment variables from `.env`.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/youtube-summarizer-agent.git
```

Move into the project directory:

```bash
cd youtube-summarizer-agent
```

---

### 2. Create a virtual environment

Using Python:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you are using `uv`:

```bash
uv venv
uv pip install -r requirements.txt
```

---

## Environment Variables

Create a file named:

```text
.env
```

in the root directory of the project.

Add your Groq API key:

```text
GROQ_API_KEY=your_groq_api_key_here
```

The project reads the API key from the environment instead of storing it directly in the source code.

### Important

Do not upload `.env` to GitHub.

Add this to `.gitignore`:

```text
.env
.venv/
__pycache__/
*.pyc
```

---

## Running the Application

From the project root directory:

```bash
streamlit run app.py
```

Streamlit will provide a local address similar to:

```text
http://localhost:8501
```

Open that address in your browser.

If you are using `uv`:

```bash
uv run streamlit run app.py
```

---

## Using the Application

### Step 1

Open the application.

### Step 2

Paste a YouTube video URL.

### Step 3

Select the summary style:

```text
Short
Detailed
Academic
```

### Step 4

Click:

```text
Summarize Video
```

### Step 5

Wait for the transcript to be retrieved and processed.

### Step 6

Read the generated summary.

You can also open the transcript section to see the original retrieved transcript.

---

## Example

Input:

```text
YouTube URL
https://www.youtube.com/watch?v=XXXXXXXXXXX
```

Select:

```text
Detailed
```

The application processes the video and returns a structured summary containing sections such as:

```text
# Video Summary

## Main Topic

...

## Important Points

...

## Detailed Explanation

...

## Examples

...

## Key Takeaways

...
```

---

## Error Handling

The application handles common problems such as:

* Empty YouTube URL
* Invalid YouTube URL
* Invalid video ID
* Missing Groq API key
* Missing transcript
* Empty transcript
* Transcript retrieval failures
* LLM/API errors

If a problem occurs, the Streamlit interface displays an error message rather than stopping without explanation.

---

## Project Structure in Detail

### `app.py`

This file contains the Streamlit frontend.

Responsibilities include:

* Page configuration
* Sidebar
* URL input
* Summary style selection
* Buttons
* Progress/status messages
* Displaying summaries
* Displaying transcripts
* Download buttons
* Session history

---

### `src/agent.py`

This is the main AI/agent component.

It contains:

* Groq LLM configuration
* Transcript retrieval node
* Transcript chunking
* Summarization node
* LangGraph construction
* Public `summarize_youtube()` function

The graph connects the transcript and summarization steps.

---

### `src/prompts.py`

Contains the prompts used by the language model.

Keeping prompts in a separate file makes it easier to modify the behavior of the summarizer without changing the application logic.

---

### `src/state.py`

Defines the state used by LangGraph.

```python
class YoutubeState(TypedDict, total=False):
    url: str
    video_id: str
    transcript: str
    summary: str
    error: str
```

---

### `src/utils.py`

Contains helper functions such as extracting a video ID from different YouTube URL formats.

---

## Requirements

The main Python packages are:

```text
streamlit
langgraph
langchain-core
langchain-groq
youtube-transcript-api
python-dotenv
```

Install them using:

```bash
pip install -r requirements.txt
```

---

## Limitations

This project currently depends on the availability of a YouTube transcript.

Some videos may not work if:

* No transcript is available
* The transcript is unavailable in English
* YouTube restricts access to the transcript
* The video is private or restricted
* The transcript cannot be retrieved by the API

The generated summary is based on the retrieved transcript, so it may not represent information that is missing from the transcript.

---

## Future Improvements

Some possible improvements for future versions include:

* Support for multiple transcript languages
* Automatic language detection
* YouTube video title and thumbnail extraction
* Timestamp-based summaries
* Chapter-wise summaries
* Ask questions about the video
* Conversational chat with the transcript
* RAG-based transcript question answering
* Multiple LLM provider support
* Better handling of very long videos
* Summary export to PDF
* Persistent database for summary history
* User authentication
* Deployment to a cloud platform

---

## What I Learned

Through this project, I practiced:

* Building applications with LangGraph
* Understanding state-based AI workflows
* Working with LangChain prompts
* Connecting an LLM to an application
* Retrieving data from YouTube
* Processing long text
* Handling API keys securely
* Building a Streamlit frontend
* Managing application state with `st.session_state`
* Structuring a Python project into separate modules

---

## Developer

**Syed Talha Ali Shah**

Computer Systems Engineering
University of Engineering and Technology (UET), Peshawar

Interested in:

* Artificial Intelligence
* Agentic AI
* Machine Learning
* Generative AI
* Computer Vision
* AI-based software development

This project was developed as a practical implementation of an Agentic AI workflow using LangGraph and LLMs.

---

## Acknowledgements

This project uses the following open-source technologies:

* LangGraph
* LangChain
* Streamlit
* YouTube Transcript API
* Groq

---

## License

This project is intended for educational and portfolio purposes.

You are free to modify and extend the project for your own learning and development.
