import streamlit as st
from groq import Groq
import re
import requests
import os
from dotenv import load_dotenv
from prompt import career_path_prompt,career_step_prompt,get_learning_prompt

load_dotenv()  # Load environment variables

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")



client = Groq(api_key=GROQ_API_KEY)

def get_career_path(goal):
    """Generate a career path based on the given career goal."""
    prompt = career_path_prompt.format(goal=goal)

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0
    )
    return response.choices[0].message.content

def get_step_summary(step_name):
    """Retrieve a summary for the given career path step."""
    prompt = career_step_prompt.format(step_name=step_name)
    
    response = client.chat.completions.create(
        model="llama3-8b-8192",  # Or use the model of your choice
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0  # Adjust the temperature for more or less creativity
    )
    
    # Clean up the response to ensure the format is correct
    response_text = response.choices[0].message.content.strip()

    # Remove the unwanted "• ****" and any other unwanted characters
    response_text = re.sub(r'•\s*\*{4}', '', response_text)  # Remove "• ****"
    response_text = re.sub(r'Most Important Skill:\s*Not Available', '', response_text).strip()  # Remove "Most Important Skill"
    
    # Clean up any extra formatting or redundant characters
    response_text = re.sub(r'• What to Learn:', '', response_text).strip()  # Remove "• What to Learn:" line
    return response_text

def extract_step_details(career_path):
    """Extract step details from the given career path text."""
    pattern = r"\*\*(Step \d+:.*?)\*\*"
    steps = re.findall(pattern, career_path)
    step_details = []
    
    for step in steps:
        step_name = step.split(":")[1].strip()  # Remove "Step X:" part
        step_details.append(step_name)
        
    return step_details

def get_books(topic, max_results=10):
    """Fetch book recommendations for the given topic."""
    url = f"https://www.googleapis.com/books/v1/volumes?q={topic}&maxResults={max_results}&orderBy=newest&key={GOOGLE_BOOKS_API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        books = data.get("items", [])
        results = []
        
        for book in books:
            info = book.get("volumeInfo", {})
            title = info.get("title", "No Title")
            authors = ", ".join(info.get("authors", ["Unknown Author"]))
            link = info.get("infoLink", "#")
            thumbnail = info.get("imageLinks", {}).get("thumbnail", "https://via.placeholder.com/128")
            published_date = info.get("publishedDate", "Unknown Date")
            
            results.append({"title": title, "authors": authors, "link": link, "thumbnail": thumbnail, "published_date": published_date})
        
        return results if results else []
    else:
        return []

def rank_books_with_groq(books, topic):
    """Rank the top books related to the given topic using Groq AI."""
    groq_url = "https://api.groq.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = f"Here are some of the latest books related to {topic}. Rank the top 3 best books based on their relevance and usefulness:\n" + \
             "\n".join([f"Title: {book['title']}, Authors: {book['authors']}, Published Date: {book['published_date']}" for book in books])
    
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "system", "content": "Rank the books based on their relevance and usefulness."},
                     {"role": "user", "content": prompt}]
    }
    
    response = requests.post(groq_url, headers=headers, json=payload)
    if response.status_code == 200:
        ranked_books_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No ranking available.")
        ranked_titles = [line.split("Title:")[1].strip() for line in ranked_books_text.split("\n") if "Title:" in line]
        return [book for book in books if book['title'] in ranked_titles][:5]
    return books[:3]

def get_learning_guide(topic):
    """Generate an A-to-Z structured learning guide for the given topic."""
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = get_learning_prompt.format(topic=topic)
    
    data = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}]}
    
    response = requests.post("https://api.groq.com/v1/chat/completions", headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Error fetching learning guide."

# ✅ Function to search for YouTube playlists

def search_youtube_playlists(query, max_results=3):
    """Search for YouTube playlists related to the given query."""
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&maxResults={max_results}&type=playlist&key={YOUTUBE_API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if "items" in data:
            for item in data["items"]:
                playlist_id = item["id"]["playlistId"]
                title = item["snippet"]["title"]
                channel = item["snippet"]["channelTitle"]
                thumbnail = item["snippet"]["thumbnails"]["medium"]["url"]
                playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
                
                results.append({
                    "title": title,
                    "channel": channel,
                    "thumbnail": thumbnail,
                    "url": playlist_url
                })
        return results
    
    except requests.exceptions.RequestException as e:
        return ["Error fetching YouTube playlists."]


st.set_page_config(page_title="Career Path AI Agent", layout="wide")

col1, col2 = st.columns([1, 4])

# 👉 Input Section
with col1:
    st.title(" ")
    goal = st.text_input("Enter your career goal (e.g., Data Scientist)")
    if st.button("Generate Career Path"):
        st.session_state['goal'] = goal

# 👉 Output Section
with col2:
    st.markdown("<h1 style='text-align: center; font-weight: bold;'>CareerWave 🌊</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-weight: bold;'>Your journey, your wave</h3>", unsafe_allow_html=True)

    if 'goal' in st.session_state and st.session_state['goal']:
        tab1, tab2, tab3, tab4  = st.tabs(["Career Path", "Step Details", "Books", "YouTube Playlists"])

        # 👉 First Tab: Display Career Path
        with tab1:
            st.markdown(f"### Career Path for **{st.session_state['goal']}**")
            career_path = get_career_path(st.session_state['goal'])
            
            # Check if the response contains inappropriate content
            st.session_state['career_path'] = career_path
            st.markdown(career_path)

        # 👉 Second Tab: Display Step Summary and Dynamic Details
        with tab2:
            st.markdown("### Step Summary")

            if 'career_path' in st.session_state:
                # Extract step details
                steps = extract_step_details(st.session_state['career_path'])

                if steps:
                    # Loop through each step and request the relevant summary from the LLM
                    for i, step in enumerate(steps):
                        st.markdown(f"#### **Step {i+1}: {step}**")
                        
                        # Get the summary for the step from the LLM
                        step_summary = get_step_summary(step)
                    
                        # Display the 'What to Learn' section
                        #st.markdown(f"**What to Learn**:")
                        # Format the bullet points properly
                        points = step_summary.split("•")
                        for point in points:
                            st.markdown(f"• {point.strip()}")  # Add each point as a bullet
                        
                else:
                    st.warning("No steps extracted. Try regenerating the career path.")
            else:
                st.info("Generate a career path to see step summary.")
        
        with tab3:
            topic = st.session_state['goal']

            if topic:
                books = get_books(topic)
                if books:
                    top_books = rank_books_with_groq(books, topic)
                    for book in top_books:
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.image(book["thumbnail"], width=100)
                        with col2:
                            st.markdown(f"**📘 {book['title']}**")
                            st.markdown(f"👨‍💼 **Authors:** {book['authors']}")
                            st.markdown(f"📅 **Published Date:** {book['published_date']}")
                            st.markdown(f"🔗 [More Info]({book['link']})")
                        st.markdown("---")
                else:
                    st.error("Issue on deploy time but locally perfect work they suggest book.")

        with tab4:            
            topic = st.session_state['goal']
            
            if topic:
                with st.spinner("Generating learning guide and fetching playlists..."):
                                
                    # Get top YouTube playlists
                    playlists = search_youtube_playlists(topic)
                    
                    # Display Playlists
                    st.subheader(f"🎥 Best YouTube Playlists for {topic}")
                    for playlist in playlists:
                        col1, col2 = st.columns([1, 4])
                        
                        with col1:
                            st.image(playlist["thumbnail"], width=160)
                        
                        with col2:
                            st.markdown(f"### [{playlist['title']}]({playlist['url']})")
                            st.write(f"**Channel:** {playlist['channel']}")
                            st.write(f"[Watch Playlist]({playlist['url']})")


# ✅ Footer
st.markdown("---")
st.markdown("Developed by Parth Varecha")
