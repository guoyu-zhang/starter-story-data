# Starter Story Data

Fetch and summarise Starter Story YouTube videos, display in a table.

## Setup

1.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Ensure you have a `.env` file with the necessary API keys (look at .env.sample).

## Usage

1.  **Fetch Videos & Transcripts**:
    Downloads recent video metadata and transcripts.

    ```bash
    python fetch_recent_videos.py
    ```

2.  **Generate Summaries**:
    Generates summaries for the fetched transcripts.

    ```bash
    python summarize_transcripts.py
    ```

3.  **Run the Web View**:
    Starts a local web server to view the summaries and transcripts in a table format.
    ```bash
    python app.py
    ```
