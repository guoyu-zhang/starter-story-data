import os
import json
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
TRANSCRIPTS_DIR = "transcripts"
SUMMARIES_DIR = "summaries"

# Initialize OpenRouter client
client = AsyncOpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai/api/v1",
)

async def summarize_transcript(transcript, video_id):
    prompt = f"""
    You are a helpful concise assistant that answers questions about YouTube videos by Pat Walls at Starter Story.
    Pat Walls interviews entreprenuers building products. We don't care about pat walls so do not talk much about him.
    Focus on the person being interviewed, which we well refer to as the subject from now on.
    Here is the YouTube video transcript.
    Transcript:
    \"\"\"
    {transcript}
    \"\"\"
    Please answer the following questions, read the questions carefully and make sure you do not duplicate too much information between answers:
    1. Explain briefly who the subject is.
    2. Explain in detail what the subject built.
    3. Explain in one sentence the main strategy used by the subject.
    4. Explain the playbook used by the subject. You should go into some detail here and assume the reader is a complete beginner so you should explain concepts.
    5. Explain the tech stack used by the subject.
    6. What is the advice given by the subject at the end.
    
    you should return the answers in the following template, do not add any extra words or include the question itself in the response:
    
    Question 1.
    Question 2.
    Question 3.
    Question 4.
    Question 5.
    Question 6.
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = await client.chat.completions.create(
                model="xiaomi/mimo-v2-flash:free",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

            content = response.choices[0].message.content
            
            # Validate format
            # We check for at least the first few questions to ensure the structure is correct
            if "Question 1." in content and "Question 2." in content and "Question 3." in content:
                return content
            else:
                print(f"Attempt {attempt + 1} failed validation (missing 'Question X.' format). Retrying...")
                
        except Exception as error:
            print(f"An error occurred during summarization (Attempt {attempt + 1}): {error}")

    return "Failed to generate valid summary after multiple retries."

async def main():
    if not os.path.exists(SUMMARIES_DIR):
        os.makedirs(SUMMARIES_DIR)

    if not os.path.exists(TRANSCRIPTS_DIR):
        print(f"Directory {TRANSCRIPTS_DIR} not found.")
        return

    for filename in os.listdir(TRANSCRIPTS_DIR):
        if filename.endswith(".json"):
            video_id = filename.replace(".json", "")
            summary_filename = f"{SUMMARIES_DIR}/{video_id}_summary.md"
            
            # Check if summary already exists
            if os.path.exists(summary_filename):
                print(f"Summary for {video_id} already exists. Skipping.")
                continue

            filepath = os.path.join(TRANSCRIPTS_DIR, filename)
            with open(filepath, "r") as f:
                data = json.load(f)
                transcript_text = data.get("transcript", "")
            
            if not transcript_text:
                print(f"No transcript found for {video_id}. Skipping.")
                continue

            print(f"Summarizing {video_id}...")
            summary = await summarize_transcript(transcript_text, video_id)
            
            with open(summary_filename, "w") as f:
                f.write(summary)
            print(f"Saved summary to {summary_filename}")

if __name__ == "__main__":
    asyncio.run(main())
