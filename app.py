import streamlit as st
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import spacy
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

load_dotenv()

# Load English tokenizer, tagger, parser, and NER
nlp = spacy.load("en_core_web_sm")

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are Youtube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """


def extract_keywords(text, n_keywords=5):
    doc = nlp(text)
    # Filter out stopwords and punctuation
    keywords = [token.text for token in doc if not token.is_stop and not token.is_punct]
    # Count the frequency of each keyword
    keyword_freq = Counter(keywords)
    # Get the most common keywords
    top_keywords = keyword_freq.most_common(n_keywords)
    return [keyword[0] for keyword in top_keywords]

## getting the transcript data from yt videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except IndexError:
        st.error("Invalid YouTube video URL. Please enter a valid URL.")
    except Exception as e:
        st.error(f"Error: {e}")

## getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

st.title("YouTube Transcript to Detailed Notes Converter")
st.markdown("Convert YouTube video transcripts into detailed notes.")

youtube_link = st.text_input("Enter YouTube Video Link:")

if st.button("Get Detailed Notes"):
    if not youtube_link:
        st.warning("Please enter a YouTube video link.")
    else:
        with st.spinner("Fetching transcript and generating summary..."):
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:
                summary = generate_gemini_content(transcript_text, prompt)
                st.markdown("## Detailed Notes:")
                st.write(summary)
                
                st.markdown("## Key Topics:")
                keywords = extract_keywords(summary)
                
                # Create a word cloud visualization
                wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(keywords))
                
                # Display the word cloud using Matplotlib
                plt.figure(figsize=(10, 5))
                plt.imshow(wordcloud, interpolation="bilinear")
                plt.axis("off")
                st.pyplot(plt)

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.video(f"https://www.youtube.com/watch?v={video_id}")
