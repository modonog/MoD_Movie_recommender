import streamlit as st
import pandas as pd
import pickle
import requests
from PIL import Image
from io import BytesIO
from difflib import get_close_matches

# Load movie dataset and similarity data
movies = pd.read_csv("final_Movie_dataset_GIT.csv.gz", compression="gzip")
with open("top_similar_movies.pkl", "rb") as f:
    top_similar_movies = pickle.load(f)

# Ensure release_year exists
if 'release_year' not in movies.columns and 'release_date' in movies.columns:
    movies['release_year'] = pd.to_datetime(movies['release_date'], errors='coerce').dt.year

# Normalize title for fuzzy matching
movies['normalized_title'] = movies['title'].str.lower()

# Helper function
def get_recommendations(movie_idx, top_n=5):
    similar = top_similar_movies.get(movie_idx, [])
    recommendations = []
    for sim_idx, score in similar[:top_n]:
        movie = movies.loc[sim_idx].copy()
        movie['similarity_score'] = round(score, 3)
        recommendations.append(movie)
    return pd.DataFrame(recommendations)

def fetch_poster(poster_path):
    if pd.notna(poster_path):
        poster_url = f"https://image.tmdb.org/t/p/original/{poster_path}"
        try:
            response = requests.get(poster_url)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
        except:
            return None
    return None

st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 MoD's CS8740 Movie Recommender")

# Initialize session state for fuzzy match
if "selected_title" not in st.session_state:
    st.session_state.selected_title = None

# Input area
input_col1 = st.container()
with input_col1:
    movie_input = st.text_input("Enter a Movie Title:", key="movie_input")

recommend_clicked = st.button("Recommend")
clear_clicked = st.button("Clear Selection")

if clear_clicked:
    st.session_state.movie_input = ""
    st.session_state.selected_title = None
    st.experimental_rerun()

if recommend_clicked:
    if st.session_state.selected_title:
        # If user already selected from fuzzy list
        selected_movie_row = movies[movies['title'] == st.session_state.selected_title]
        matches = selected_movie_row
        st.session_state.selected_title = None  # Reset after use
    else:
        # Normal search
        movie_input_clean = movie_input.strip().lower()
        matches = movies[movies['normalized_title'] == movie_input_clean]

        if matches.empty:
            matches = movies[movies['normalized_title'].str.contains(movie_input_clean, na=False)]

        if matches.empty:
            title_list = movies['normalized_title'].tolist()
            close_matches = get_close_matches(movie_input_clean, title_list, n=5, cutoff=0.6)
            if close_matches:
                matched_movies = movies[movies['normalized_title'].isin(close_matches)]
                selected_title = st.selectbox("Select the closest match:", matched_movies['title'])
                if selected_title:
                    st.session_state.selected_title = selected_title
                st.stop()

    if matches.empty:
        st.warning("❌ Movie not found in dataset.")
    else:
        selected_movie = matches.iloc[0]

        st.subheader(f"Selected Movie: {selected_movie['title']}")
        cols = st.columns([1, 4])

        poster_image = fetch_poster(selected_movie['poster_path'])
        if poster_image:
            cols[0].image(poster_image, width=150)
        else:
            cols[0].write("[Image not available]")

        overview = selected_movie.get('overview', 'Overview not available.')
        cols[1].markdown(f"📝 {overview}")

        st.subheader("Top Recommendations")
        recommendations = get_recommendations(selected_movie.name)

        for _, movie in recommendations.iterrows():
            rec_cols = st.columns([1, 4])

            # Poster image
            poster_image = fetch_poster(movie['poster_path'])
            if poster_image:
                rec_cols[0].image(poster_image, width=120)
            else:
                rec_cols[0].write("[Image not available]")

            # Movie info
            rec_cols[1].markdown(f"**{movie['title']}")
            rec_cols[1].markdown(f"⭐ Rating: {movie.get('vote_average', 'N/A')}")
            overview = movie.get('overview', 'Overview not available.')
            rec_cols[1].markdown(f"📝 {overview}")

            if pd.notna(movie.get('imdb_id')):
                imdb_link = f"https://www.imdb.com/title/{movie['imdb_id']}"
                rec_cols[1].markdown(f"[🔗 View on IMDb]({imdb_link})", unsafe_allow_html=True)
