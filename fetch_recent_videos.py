import os
import sys
import json
from dotenv import load_dotenv
import yt_dlp
from fetch_transcript import fetch_transcript

# Load environment variables from .env file
load_dotenv()

HISTORY_FILE = "fetched_videos.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return set(json.load(f))
        except json.JSONDecodeError:
            return set()
    return set()

def save_to_history(video_id):
    history = load_history()
    if video_id not in history:
        history.add(video_id)
        with open(HISTORY_FILE, "w") as f:
            json.dump(list(history), f, indent=4)

def get_recent_videos(channel_id, limit=2):
    proxy_username = os.getenv("PROXY_USERNAME")
    proxy_password = os.getenv("PROXY_PASSWORD")

    # Fetch more than the limit to account for videos already in history
    fetch_limit = limit + 50
    ydl_opts = {
        'extract_flat': 'in_playlist', # Just get video metadata, don't download
        'playlistend': fetch_limit, 
        'quiet': True,
        'ignoreerrors': True,
        'no_warnings': True,
    }

    if proxy_username and proxy_password:
        # Webshare proxy configuration
        # Username format: username-rotate for rotating proxies
        proxy_url = f"http://{proxy_username}-rotate:{proxy_password}@p.webshare.io:80/"
        ydl_opts['proxy'] = proxy_url
        print(f"Using Webshare proxy with user {proxy_username}-rotate")

    # Construct channel URL
    # Supports channel ID, user, or custom URL. Assuming channel ID or full URL.
    if channel_id.startswith("http"):
        url = channel_id
    elif channel_id.startswith("UC"):
        url = f"https://www.youtube.com/channel/{channel_id}/videos"
    else:
        # Fallback/Assumption for handle or other ID types, trying as channel ID first
        url = f"https://www.youtube.com/channel/{channel_id}/videos"

    print(f"Fetching recent videos from: {url}")

    try:
        history = load_history()
        new_videos_processed = 0

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info:
                print(f"\nScanning recent videos for {limit} new ones...")
                entries = list(info['entries'])
                
                for entry in entries:
                    if new_videos_processed >= limit:
                        break
                        
                    if not entry:
                        continue

                    video_id = entry.get('id')
                    
                    if video_id in history:
                        # print(f"Skipping {video_id} (already fetched)")
                        continue

                    video_title = entry.get('title')
                    
                    # Fetch detailed info to get upload_date if missing
                    upload_date = entry.get('upload_date')
                    if not upload_date:
                        print(f"  Fetching detailed metadata for {video_id} to get upload_date...")
                        try:
                            # Create a separate options dict for detail fetching, preserving proxy
                            detail_opts = {
                                'quiet': True,
                                'ignoreerrors': True,
                                'no_warnings': True,
                            }
                            if 'proxy' in ydl_opts:
                                detail_opts['proxy'] = ydl_opts['proxy']
                                
                            with yt_dlp.YoutubeDL(detail_opts) as ydl_detail:
                                detail_info = ydl_detail.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                                if detail_info:
                                    upload_date = detail_info.get('upload_date')
                                    video_title = detail_info.get('title', video_title)
                        except Exception as e:
                            print(f"  Could not fetch detailed info: {e}")

                    print(f"- {video_title} (ID: {video_id})")
                    
                    # Fetch transcript
                    print(f"  Fetching transcript for {video_id}...")
                    transcript_text = fetch_transcript(video_id)
                    
                    if transcript_text:
                        data = {
                            "video_id": video_id,
                            "title": video_title,
                            "upload_date": upload_date,
                            "transcript": transcript_text
                        }
                        
                        filename = f"transcripts/{video_id}.json"
                        with open(filename, "w", encoding="utf-8") as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)
                        print(f"  Saved transcript to {filename}")
                        
                        # Add to history
                        save_to_history(video_id)
                        print(f"  Added {video_id} to history")
                        
                        # Increment counter for new videos processed
                        new_videos_processed += 1
                    else:
                        print(f"  Could not fetch transcript for {video_id}")

            else:
                print("No videos found.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    limit = 2
    if len(sys.argv) > 1:
        channel_id = sys.argv[1]
        if len(sys.argv) > 2:
            try:
                limit = int(sys.argv[2])
            except ValueError:
                print("Invalid limit provided. Using default: 2")
    else:
        # print("No channel ID provided. Usage: python fetch_recent_videos.py <channel_id> [limit]")
        # Default to a known channel ID for testing (e.g., Google Developers)
        # print("Using default channel ID: UC_x5XG1OV2P6uZZ5FSM9Ttw (Google Developers)")
        channel_id = "UChhw6DlKKTQ9mYSpTfXUYqA"

    get_recent_videos(channel_id, limit)
