import os
import sys
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

# Load environment variables from .env file
load_dotenv()

def fetch_transcript(video_id):
    proxy_username = os.getenv("PROXY_USERNAME")
    proxy_password = os.getenv("PROXY_PASSWORD")

    if not proxy_username or not proxy_password:
        print("Error: PROXY_USERNAME or PROXY_PASSWORD not found in .env file.")
        return

    print(f"Using Proxy Username: {proxy_username}")
    # Initialize the API with Webshare proxy configuration
    # Note: The user provided snippet suggests instantiating YouTubeTranscriptApi. 
    # If the installed version supports this instantiation pattern with proxy_config, this will work.
    try:
        ytt_api = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=proxy_username,
                proxy_password=proxy_password
            )
        )
        
        print(f"Fetching transcript for video ID: {video_id}...")
        transcript = ytt_api.fetch(video_id)
        
        # Print the first few lines of the transcript to verify
        print("\nTranscript fetched successfully! First 5 entries:")
        for entry in transcript[:5]:
            print(entry)
            
        return transcript

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
    else:
        # Default video ID if none provided (e.g., a short video or the one from the example)
        print("No video ID provided. Usage: python fetch_transcript.py <video_id>")
        print("Using default video ID: jNQXAC9IVRw (Me at the zoo)")
        video_id = "Adl5_lJfkEE"

    fetch_transcript(video_id)
