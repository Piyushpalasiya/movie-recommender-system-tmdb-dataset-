import streamlit as st
import pickle
import pandas as pd
import requests

def fetch_movie_details(movie_title):
    api_key = 'your_rapidapi_key'  # Replace with your RapidAPI key
    url = "https://imdb8.p.rapidapi.com/title/find"
    querystring = {"q": movie_title}
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "imdb8.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        if 'results' in data and data['results']:
            for result in data['results']:
                if 'title' in result and result['title'].lower() == movie_title.lower():
                    movie_details = {
                        'poster_url': result['image']['url'] if 'image' in result and 'url' in result['image'] else "https://via.placeholder.com/500",
                        'rating': result['ratings']['rating'] if 'ratings' in result and 'rating' in result['ratings'] else "N/A",
                        'genres': ", ".join([genre['text'] for genre in result['genres']]) if 'genres' in result else "N/A"
                    }
                    return movie_details
        return {'poster_url': "https://via.placeholder.com/500", 'rating': "N/A", 'genres': "N/A"}
    except Exception as e:
        st.error(f"Error fetching details for {movie_title}: {e}")
        return {'poster_url': "https://via.placeholder.com/500", 'rating': "N/A", 'genres': "N/A"}

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_movies_details = []
    for i in movies_list:
        movie_title = movies.iloc[i[0]].title
        recommended_movies.append(movie_title)
        movie_details = fetch_movie_details(movie_title)
        recommended_movies_details.append(movie_details)
    return recommended_movies, recommended_movies_details

# Load the movie dictionary and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit page configuration
st.set_page_config(page_title='Movie Recommender System', page_icon=':clapper:', layout='wide')

# Header
st.title('Piyush Movie Recommender System')
st.markdown("""
    Welcome to the Movie Recommender System! Select a movie from the dropdown below to get recommendations for similar movies.
    This app uses a machine learning model to suggest movies you might like based on your selection.
""")

# Sidebar for user selection
with st.sidebar:
    st.header('Select a Movie')
    selected_movie_name = st.selectbox("Choose a movie to get recommendations:", movies['title'].values)
    if st.button('Recommend'):
        with st.spinner('Fetching recommendations...'):
            names, details = recommend(selected_movie_name)
        
        # Display recommendations
        st.header('Recommended Movies')
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.image(details[idx]['poster_url'], use_column_width=True)
                st.markdown(f"**{names[idx]}**")
                st.markdown(f"**Rating:** {details[idx]['rating']}")
                st.markdown(f"**Genres:** {details[idx]['genres']}")

# Main section for additional information and description
st.markdown("## How It Works")
st.markdown("""
    This recommender system is built using a content-based filtering approach. It uses a similarity matrix to find movies that are similar to the one you select. The similarity matrix is precomputed using features such as movie genres, keywords, and cast information.
""")

# Footer
st.markdown("""
    ---
    **Note**: The recommendations are generated based on the data available in the movie dataset. The poster images are fetched using the IMDb API from RapidAPI.
""")
