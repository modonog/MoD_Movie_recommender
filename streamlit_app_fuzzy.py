# -*- coding: utf-8 -*-
"""
Created on Thu Apr 24 22:27:47 2025

@author: mpodo
"""
import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import pickle
from difflib import get_close_matches

# Load data
movies = pd.read_csv("final_Movie_dataset.csv.gz", compression="gzip")
with open("top_similar_movies.pkl", "rb") as f:
    top_similar_movies = pickle.load(f)

if 'release_year' not in movies.columns and 'release_date' in movies.columns:
    movies['release_year'] = pd.to_datetime(movies['release_date'], errors='coerce').dt.year

def get_recommendations(title, top_n=5):
    title = title.lower()
    title_matches = movies[movies['title'].str.lower() == title]

    if not title_matches.empty:
        idx = title_matches.index[0]
    else:
        all_titles = movies['title'].str.lower().tolist()
        close_matches = get_close_matches(title, all_titles, n=1, cutoff=0.6)
        if not close_matches:
            return pd.DataFrame(), None
        match_title = close_matches[0]
        idx = movies[movies['title'].str.lower() == match_title].index[0]

    similar = top_similar_movies.get(idx, [])
    recommendations = []

    for sim_idx, score in similar[:top_n]:
        movie = movies.loc[sim_idx].copy()
        movie['similarity_score'] = round(score, 3)
        recommendations.append(movie)

    return pd.DataFrame(recommendations), movies.loc[idx]

def display_poster(poster_path, width=120):
    if pd.isna(poster_path):
        st.write("Image not available")
        return
    try:
        img_url = f"https://image.tmdb.org/t/p/original/{poster_path}"
        response = requests.get(img_url, timeout=3)
        img = Image.open(BytesIO(response.content))
        st.image(img, width=width)
    except Exception:
        st.write("Image not available")

st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 MoD's CS8740 Movie Recommender")

movie_input = st.text_input("Enter a movie title to get recommendations:")
if st.button("Recommend") or movie_input:
    if movie_input:
        recs, selected_movie = get_recommendations(movie_input)

        if recs.empty:
            st.warning("No recommendations found. Try a different title.")
        else:
            col1, col2 = st.columns([1, 3])
            with col1:
                display_poster(selected_movie.get('poster_path'))
            with col2:
                st.subheader(f"{selected_movie['title']} ({selected_movie.get('release_year', 'N/A')})")
                st.markdown(f"**Rating:** {selected_movie.get('vote_average', 'N/A')}")
                st.markdown(f"**Overview:** {selected_movie.get('overview', 'N/A')}")
                if pd.notna(selected_movie.get('imdb_id')):
                    imdb_url = f"https://www.imdb.com/title/{selected_movie['imdb_id']}"
                    st.markdown(f"[View on IMDb]({imdb_url})")

            st.markdown("---")
            st.subheader("Recommended Movies")

            for _, row in recs.iterrows():
                rec_col1, rec_col2 = st.columns([1, 3])
                with rec_col1:
                    display_poster(row.get('poster_path'))
                with rec_col2:
                    st.markdown(f"### {row['title']} ({row.get('release_year', 'N/A')})")
                    st.markdown(f"**Rating:** {row.get('vote_average', 'N/A')} | **Similarity Score:** {row.get('similarity_score', 'N/A')}")
                    st.markdown(f"{row.get('overview', 'Overview not available.')}")
                    if pd.notna(row.get('imdb_id')):
                        st.markdown(f"[View on IMDb](https://www.imdb.com/title/{row['imdb_id']})")
                st.markdown("---")

