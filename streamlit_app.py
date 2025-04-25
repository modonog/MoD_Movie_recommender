# streamlit_app.py

import streamlit as st
import pandas as pd
import pickle

# Load movie data
df = pd.read_csv("final_Movie_dataset_GIT.csv.gz", compression="gzip")

# Load precomputed similar movies
with open("top_similar_movies.pkl", "rb") as f:
    top_similar = pickle.load(f)

# Convert release_date to year (if not already present)
if 'release_year' not in df.columns and 'release_date' in df.columns:
    df['release_year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year

st.title("🎬 MoD's Movie Recommender")

# Input
movie_input = st.text_input("Enter a movie title:")

if st.button("Recommend"):
    if not movie_input:
        st.warning("Please enter a movie name.")
    else:
        matches = df[df['title'].str.lower() == movie_input.lower()]
        if matches.empty:
            st.error("Movie not found in dataset.")
        else:
            # Pick first match
            selected_movie = matches.iloc[0]
            selected_title = selected_movie['title']
            selected_index = selected_movie.name

            # Fetch recommendations
            recommendations = top_similar.get(selected_index, [])

            if not recommendations:
                st.info("No similar movies found.")
            else:
                st.subheader(f"Recommendations for: **{selected_title}**")

                for sim_index, sim_score in recommendations[:5]:
                    movie = df.iloc[sim_index]
                    title = movie.get("title", "N/A")
                    year = movie.get("release_year", "N/A")
                    rating = movie.get("vote_average", "N/A")
                    overview = movie.get("overview", "Overview not available.")
                    poster_path = movie.get("poster_path")
                    imdb_id = movie.get("imdb_id")

                    # Build Poster URL
                    if pd.notna(poster_path):
                        img_url = f"https://image.tmdb.org/t/p/original/{poster_path}"
                        st.image(img_url, width=150)
                    else:
                        st.text("[Image not available]")

                    st.markdown(f"### {title} ({year})")
                    st.markdown(f"**Rating:** {rating}")
                    st.markdown(f"**Overview:** {overview}")
                    if pd.notna(imdb_id):
                        st.markdown(f"[🔗 IMDb Link](https://www.imdb.com/title/{imdb_id})")

                    st.markdown("---")
