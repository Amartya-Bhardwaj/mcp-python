import streamlit as st
from main1 import summarize_youtube_fn1  # <-- your MCP function

st.set_page_config(page_title="🎥 YouTube Summary Tool", layout="wide")

st.title("🎥 YouTube Summary Tool")
st.write("Fetch top YouTube videos for a search query and summarize them.")

# --- Input section ---
query = st.text_input("🔍 Enter your search query", placeholder="e.g. AI news, Python tutorial, Cricket highlights")

max_results = st.slider("Number of videos", min_value=1, max_value=5, value=3)

if st.button("Get Summaries"):
    if not query.strip():
        st.warning("⚠️ Please enter a query.")
    else:
        with st.spinner("Fetching videos & generating summaries..."):
            try:
                # Call your MCP tool function
                # Assume it returns a list of dicts like:
                # [{"title": "...", "url": "...", "summary": "..."}]
                results = summarize_youtube_fn1(query, max_results=max_results)
                print("Lenght of results", len(results))
                st.success("✅ Summaries generated!")
                for idx, video in enumerate(results, 1):
                    with st.container():
                        st.markdown(f"### {idx}. [{video['title']}]({video['url']})")
                        st.write(video["summary"])
                        st.divider()

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
