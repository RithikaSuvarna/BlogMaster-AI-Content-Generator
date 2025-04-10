import streamlit as st
import google.generativeai as genai
import requests
from apiKey import google_gemini_api_key, unsplash_api_key  # Store your Unsplash API key securely

# Configure Google Gemini API
genai.configure(api_key=google_gemini_api_key)

generation_config = {
    "temperature": 0.9,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Setting up the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# Set app to wide mode
st.set_page_config(layout="wide")

# Title of the app
st.title('BlogMaster: AI-Powered Blog Generation Assistant')

# Sidebar for user input
with st.sidebar:
    st.title("Input your Blog Details")
    st.subheader("Enter Details of the Blog You want to generate")

    # Blog title
    Blog_title = st.text_input("Blog Title")

    # Keywords input
    keywords = st.text_area("Keywords (comma-separated)")

    # Number of words
    num_words = st.slider("Number of Words", min_value=250, max_value=1000, step=100)

    # Number of images
    num_images = st.number_input("Number of images", min_value=1, max_value=5, step=1)

    # Language selection
    language = st.selectbox("Choose the language for the blog", ["English", "Spanish", "French", "German", "Hindi"])

    # Submit button
    submit_button = st.button("Generate Blog")

    # Blog translation
    st.subheader("Translate Existing Blog")
    blog_to_translate = st.text_area("Paste the blog content you want to translate")
    translate_to_language = st.selectbox("Translate to", ["English", "Spanish", "French", "German", "Hindi"])
    translate_button = st.button("Translate Blog")

def fetch_unsplash_images(query, num_images):
    """Fetch images from Unsplash based on the query."""
    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {unsplash_api_key}"}
    params = {"query": query, "per_page": num_images}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return [photo['urls']['regular'] for photo in data['results']]
    else:
        st.error("Failed to fetch images from Unsplash.")
        return []

if submit_button:
    # Generate blog content
    prompt_parts = [
        f"Generate a comprehensive, engaging blog post relevant to the given title \"{Blog_title}\" and keywords \"{keywords}\". "
        f"The blog should be approximately {num_words} words in length, suitable for an online audience, and written in {language}. "
        f"Ensure the content is original, informative, and maintains a consistent tone throughout.\n"
    ]
    response = model.generate_content(prompt_parts)
    st.title("Your Blog Post:")
    st.write(response.text)

    # Fetch and display images from Unsplash
    if keywords:
        query = Blog_title
        image_urls = fetch_unsplash_images(query, num_images)
        for idx, image_url in enumerate(image_urls):
            st.image(image_url, caption=f"Image {idx + 1}")

if translate_button:
    if blog_to_translate.strip():
        translation_prompt = [
            f"Translate the following blog content to {translate_to_language}:\n{blog_to_translate}\n"
        ]
        translation_response = model.generate_content(translation_prompt)
        st.title("Translated Blog:")
        st.write(translation_response.text)
    else:
        st.error("Please paste a blog to translate.")
