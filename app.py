import os
import json
import markdown
import re
from flask import Flask, render_template, abort

app = Flask(__name__)

TRANSCRIPTS_DIR = "transcripts"
SUMMARIES_DIR = "summaries"

def parse_summary(summary_text):
    """
    Parses the summary text into 6 sections.
    Expected format is "1. ... 2. ... 6. ..."
    """
    sections = {
        "subject": "",
        "built": "",
        "strategy": "",
        "playbook": "",
        "stack": "",
        "advice": ""
    }
    
    keys = ["subject", "built", "strategy", "playbook", "stack", "advice"]
    
    # Split by number headers (e.g., "Question 1.", "**Question 1.**", etc.)
    # Pattern: ^\**Question\s+\d+\.?\** (multiline)
    parts = re.split(r'(?m)^\**Question\s+\d+\.?\**', summary_text)
    
    # parts[0] is usually empty or text before "1."
    # parts[1] corresponds to answer 1, etc.
    
    for i in range(1, len(parts)):
        if i - 1 < len(keys):
            content = parts[i].strip()
            sections[keys[i-1]] = markdown.markdown(content)
            
    return sections

def get_video_data(video_id=None):
    """
    Helper to get video data. 
    If video_id is None, returns a list of all videos (metadata + summary).
    If video_id is provided, returns full data for that video including transcript.
    """
    if not os.path.exists(TRANSCRIPTS_DIR):
        return []

    videos = []
    
    # If looking for a specific video, just check that one file
    if video_id:
        filename = f"{video_id}.json"
        filepath = os.path.join(TRANSCRIPTS_DIR, filename)
        if not os.path.exists(filepath):
            return None
        files = [filename]
    else:
        files = [f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith(".json")]

    for filename in files:
        filepath = os.path.join(TRANSCRIPTS_DIR, filename)
        with open(filepath, "r") as f:
            data = json.load(f)
            
        vid_id = data.get("video_id")
        title = data.get("title", "Unknown Title")
        date = data.get("upload_date", "Unknown Date")
        transcript = data.get("transcript", "")
        
        # Read summary
        summary_path = os.path.join(SUMMARIES_DIR, f"{vid_id}_summary.md")
        summary_parts = {
            "subject": "<em>No summary</em>",
            "built": "",
            "strategy": "",
            "playbook": "",
            "stack": "",
            "advice": ""
        }
        
        if os.path.exists(summary_path):
            with open(summary_path, "r") as f:
                summary_text = f.read()
                summary_parts = parse_summary(summary_text)
        
        # Format date nicely
        date_str = date
        if date_str and len(date_str) == 8:
            date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

        video_obj = {
            "id": vid_id,
            "title": title,
            "date": date_str,
            "raw_date": date, # for sorting
            "transcript": transcript,
            "summary": summary_parts
        }
        
        if video_id:
            return video_obj
            
        videos.append(video_obj)

    # Sort videos by date descending
    videos.sort(key=lambda x: x["raw_date"] if x["raw_date"] else "0", reverse=True)
    return videos

@app.route('/')
def index():
    videos = get_video_data()
    return render_template('index.html', videos=videos)

@app.route('/transcript/<video_id>')
def transcript(video_id):
    video = get_video_data(video_id)
    if not video:
        abort(404)
    return render_template('transcript.html', video=video)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
