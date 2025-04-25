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

st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 MoD's CS8740 Movie Recommender")

movie_input = st.text_input("Enter a Movie Title:")

selected_movie_idx = None
if movie_input:
    movie_input = movie_input.strip().lower()
    matches = movies[movies['normalized_title'] == movie_input]

    if matches.empty:
        matches = movies[movies['normalized_title'].str.contains(movie_input, na=False)]

    if matches.empty:
        title_list = movies['normalized_title'].tolist()
        close_matches = get_close_matches(movie_input, title_list, n=5, cutoff=0.6)
        match_options = movies[movies['normalized_title'].isin(close_matches)]
        if not match_options.empty:
            display_titles = match_options['title'] + ' (' + match_options['release_year'].fillna('N/A').astype(str) + ')'
            selected_title = st.selectbox("Did you mean one of these?", display_titles.tolist())
            selected_movie_idx = match_options[match_options['title'] == selected_title.split(' (')[0]].index[0]
    else:
        selected_movie_idx = matches.index[0]

    if selected_movie_idx is not None:
        similar = top_similar_movies.get(selected_movie_idx, [])
        recommendations = []
        for sim_idx, score in similar[:5]:
            movie = movies.loc[sim_idx].copy()
            movie['similarity_score'] = round(score, 3)
            recommendations.append(movie)

        if not recommendations:
            st.warning("❌ No recommendations found.")
        else:
            st.subheader("Top Recommendations")
            for movie in recommendations:
                cols = st.columns([1, 4])
                poster_url = f"https://image.tmdb.org/t/p/original/{movie['poster_path']}" if pd.notna(movie['poster_path']) else None
                if poster_url:
                    try:
                        response = requests.get(poster_url)
                        if response.status_code == 200:
                            image = Image.open(BytesIO(response.content))
                            cols[0].image(image, width=120)
                        else:
                            cols[0].write("[Image not available]")
                    except:
                        cols[0].write("[Image not available]")
                else:
                    cols[0].write("[Image not available]")

                cols[1].markdown(f"**{movie['title']}**")
                cols[1].markdown(f"⭐ Rating: {movie.get('vote_average', 'N/A')}")
                overview = movie.get('overview', 'Overview not available.')
                cols[1].markdown(f"📝 {overview}")

                if pd.notna(movie.get('imdb_id')):
                    imdb_link = f"https://www.imdb.com/title/{movie['imdb_id']}"
                    cols[1].markdown(f"[🔗 View on IMDb]({imdb_link})", unsafe_allow_html=True)
    else:
        st.warning("❌ Movie not found in dataset.")
