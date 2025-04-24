# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 19:43:49 2025
@author: mpodo
"""

import streamlit as st
import pandas as pd
import pickle

# Load data
df = pd.read_csv("final_Movie_dataset_GIT.csv.gz", compression="gzip")

with open("top_similar_movies.pkl", "rb") as f:
    top_similar = pickle.load(f)

st.title("🎥 Movie Recommender")

# Movie input
movie_input = st.text_input("Enter a movie name:")

if st.button("Recommend"):
    if movie_input:
        movie_input_lower = movie_input.lower()

        # Match user input to titles in DataFrame
        matched_titles = [title for title in df['title'] if movie_input_lower in str(title).lower()]

        if matched_titles:
            selected_title = matched_titles[0]
            st.subheader(f"Recommendations for: **{selected_title}**")

            # Get movie ID (row index)
            movie_id = df[df['title'] == selected_title].index[0]

            # Fetch similar movies using the movie ID
            similar_movies = top_similar.get(movie_id, [])

            for sim_id, score in similar_movies:
                if sim_id in df.index:
                    movie_data = df.loc[sim_id]
                    st.markdown(f"**{movie_data['title']}** (Similarity: {score:.2f})")
                    st.image(movie_data['poster_url'], width=150)
                    st.markdown(f"[IMDb Link]({movie_data['imdb_link']})")
        else:
            st.warning("Movie not found in database.")
    else:
        st.warning("Please enter a movie name.")
