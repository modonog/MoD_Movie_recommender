# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 19:43:49 2025

@author: mpodo
"""

#streamlit_app.py
import streamlit as st
import pandas as pd
import pickle

# Load data
df = pd.read_csv("final_Movie_dataset_GIT.csv.zip", compression="gzip")

with open("top_similar_movies.pkl", "rb") as f:
    top_similar = pickle.load(f)

st.title("🎥 Movie Recommender")

# Movie input
movie_input = st.text_input("Enter a movie name:")

if st.button("Recommend"):
    if movie_input:
        movie_input_lower = movie_input.lower()

        matched_titles = [title for title in top_similar if movie_input_lower in title.lower()]

        if matched_titles:
            selected_title = matched_titles[0]  # Just pick the first match
            recommendations = top_similar[selected_title]

            st.subheader(f"Recommendations for: **{selected_title}**")

            for movie in recommendations:
                # You may need to adapt this if you stored only indices or just titles
                movie_row = df[df['title'] == movie]
                if not movie_row.empty:
                    movie_data = movie_row.iloc[0]
                    st.markdown(f"**{movie_data['title']}**")
                    st.image(movie_data['poster_url'], width=150)
                    st.markdown(f"[IMDb Link]({movie_data['imdb_link']})")
        else:
            st.warning("Movie not found in database.")
    else:
        st.warning("Please enter a movie name.")
