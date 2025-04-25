This is for a CS8740 project, a movie recommendation system. 
The system uses the Final_movie_dataset.csv and the precomputed similarities between movies
stored in top_similar_movies.pkl
The GUI then uses these along with data from the csv to show, user ratings of the movie,
the poster images that are used by TMDB and links to the IMDB webpage.

The GUI has the fuzzy logic built in, so that if you mispell a movie name it will give 5 options to chose from.
The model was built using SciKit Learn with using the moving rating and number of ratings to give a weighted score. 
Model is not perfect and could be refined further, it current uses Genre, cast and runtime (bucketed).

The model was ran on the entire database of 60k+ movies and returned the 5 top "best" suggestions.
additional refinement needed. Also the logic excludes suggesting it's own title, this excludes remakes with the same name
this could be handled using the release year of the movie to only exclude itself. 
