from fastmcp import FastMCP
from youtube_search import YoutubeSearch
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel("gemini-2.5-pro")

mcp = FastMCP("Demo 🚀")

@mcp.tool
async def greet_tool(name: str):
    """Greets the given name and says if the person is famous in sports. Also give the sports name in which the person is famous"""
    return (f"Your {name} is famous!")

def get_top_youtube_results(query, max_results=3):
    results = YoutubeSearch(query, max_results=max_results).to_dict()
    videos = []
    for r in results:
        video_id = r["id"]
        title = r["title"]
        link = f"https://www.youtube.com/watch?v={video_id}"
        videos.append({"title": title, "video_id": video_id, "link": link})
    return videos

def get_subtitles(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript])
    except TranscriptsDisabled:
        return None
    

def summarize_with_gemini(text, query):
    prompt = f"Summarize this YouTube video based on subtitles for the topic '{query}':\n\n{text}"
    response = model.generate_content(prompt)
    return response.text


@mcp.tool
def summarize_youtube(query: str, max_results: int = 3) -> str:
    """Finds top 3 YouTube videos and summarizes them using subtitles and Gemini API."""
    videos = get_top_youtube_results(query, max_results)
    print(len(videos))
    result = ""

    for idx, video in enumerate(videos, 1):
        result += f"{idx}. {video['title']} - {video['link']}\n"
        subtitles = get_subtitles(video["video_id"])
        if subtitles:
            summary = summarize_with_gemini(subtitles, query)
            result += f"   Summary: {summary}\n\n"
        else:
            result += "   No subtitles available.\n\n"
    return result


if __name__ == "__main__":
    mcp.run()