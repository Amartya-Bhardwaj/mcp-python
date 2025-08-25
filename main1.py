# main.py
from youtube_search import YoutubeSearch
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript
import google.generativeai as genai
import os
import time
from langchain_community.document_loaders import YoutubeLoader

gemini_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel("gemini-2.5-pro")
model = genai.GenerativeModel("gemini-2.0-flash")


def get_top_youtube_results(query, max_results=3):
    results = YoutubeSearch(query, max_results=max_results).to_dict()

    # YoutubeSearch returns a dict with 'videos' key in newer versions
    if isinstance(results, dict) and "videos" in results:
        videos_list = results["videos"]
    elif isinstance(results, list):
        videos_list = results
    else:
        return []

    videos = []
    print(videos_list)
    for r in videos_list:
        video_id = r.get("id") or r.get("idVideo")  # check different possible keys
        title = r.get("title", "Untitled")
        link = f"https://www.youtube.com/watch?v={video_id}"
        videos.append({"title": title, "video_id": video_id, "link": link})

    return videos

def get_top_youtube_results1(query, max_results=3):
    results = YoutubeSearch(query, max_results=max_results).to_dict()

    # Handle both cases: dict with 'videos' OR plain list
    if isinstance(results, dict) and "videos" in results:
        videos_list = results["videos"]
    elif isinstance(results, list):
        videos_list = results
    else:
        print("⚠️ Unexpected YoutubeSearch result format:", results)
        return []

    videos = []
    for idx, r in enumerate(videos_list):
        try:
            video_id = None
            if "id" in r:
                video_id = r["id"]
            elif "idVideo" in r:
                video_id = r["idVideo"]
            elif "url_suffix" in r:
                video_id = r["url_suffix"].replace("/watch?v=", "").split("&")[0]

            title = r.get("title", "Untitled")
            link = f"https://www.youtube.com/watch?v={video_id}" if video_id else "N/A"

            videos.append({"title": title, "video_id": video_id, "link": link})
        except Exception as e:
            print(f"⚠️ Error parsing result {idx}: {r}")
            print(f"Exception: {e}")
    return videos





def get_subtitles(video_id):
    retries = 3
    for attempt in range(retries):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([t["text"] for t in transcript])
        except (TranscriptsDisabled, NoTranscriptFound):
            return None
        except CouldNotRetrieveTranscript as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # exponential backoff: 1s, 2s, 4s
            else:
                return None
            

def get_subtitles1(video_id):
    try:
        subtitles = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return subtitles
    except NoTranscriptFound:
        print(f"⚠️ No subtitles found for video {video_id}")
        return []   # return empty list instead of None
    except Exception as e:
        print(f"⚠️ Error fetching subtitles for {video_id}: {e}")
        return []




def summarize_with_gemini(text, query):
    prompt = f"Summarize this YouTube video based on subtitles for the topic '{query}':\n\n{text}"

    try:
        response = model.generate_content(prompt)
        print("DEBUG Gemini response:", response)
        
        # Safe check for response.text
        if hasattr(response, "text") and response.text:
            return response.text
        # Some SDKs provide candidates
        elif hasattr(response, "candidates") and len(response.candidates) > 0:
            return response.candidates[0].content
        else:
            return "⚠️ Gemini returned no summary."

    except Exception as e:
        # Catch API/network errors
        return f"⚠️ Error generating summary: {str(e)}"



def summarize_youtube_fn(query: str, max_results: int = 3) -> str:
    """Plain callable function for Python / Streamlit."""
    videos = get_top_youtube_results1(query, max_results)
    print("DEBUG videos:", videos)
    print("DEBUG type:", type(videos))
    if len(videos) > 0:
        print("DEBUG first video:", videos[0], type(videos[0]))
    result = ""

    for idx, video in enumerate(videos, 1):
        result += f"{idx}. {video['title']} - {video['link']}\n"
        subtitles = get_subtitles1(video["video_id"])
        if not subtitles:
            print(f"Skipping {video['title']} (no subtitles)")
            continue

        print("DEBUG subtitles type:", type(subtitles))
        if subtitles and isinstance(subtitles, list):
            print("DEBUG first subtitle:", subtitles[0])
        if subtitles:
            summary = summarize_with_gemini(subtitles, query)
            result += f"   Summary: {summary}\n\n"
        else:
            summary = summarize_with_gemini(video["title"], query)
            result += f"   Summary: {summary}\n\n"
        # if subtitles:
        #     summary = summarize_with_gemini(subtitles, query)
        #     result += f"   Summary: {summary}\n\n"
        # else:
        #     result += "   No subtitles available.\n\n"
    return result

def summarize_youtube_fn1(query: str, max_results: int = 3):
    videos = get_top_youtube_results(query, max_results)
    results = []

    for video in videos:
        subtitles = get_subtitles1(video["video_id"])
        if subtitles:
            summary = summarize_with_gemini(subtitles, query)
        else:
            summary = summarize_with_gemini(video["title"], query)

        results.append({
            "title": video["title"],
            "url": video["link"],
            "summary": summary
        })
    return results

