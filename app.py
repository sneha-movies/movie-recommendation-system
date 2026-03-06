import streamlit as st
import pickle
import requests
import hashlib
import os

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# ================= SESSION STATE INIT =================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False


# ================= PASSWORD HASH FUNCTION =================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ================= LOAD & SAVE USERS =================
def load_users():
    if os.path.exists("users.pkl"):
        with open("users.pkl", "rb") as f:
            return pickle.load(f)
    return {}


def save_users(users):
    with open("users.pkl", "wb") as f:
        pickle.dump(users, f)


users = load_users()

# ================= SIDEBAR =================
st.sidebar.title("🔐 Account")
menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

# ================= REGISTER =================
if menu == "Register" and not st.session_state["logged_in"]:
    st.title("📝 Registration Page")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Register"):
        if new_user in users:
            st.warning("User already exists!")
        else:
            users[new_user] = hash_password(new_pass)
            save_users(users)
            st.success("Registration Successful! Please Login.")

# ================= LOGIN =================
elif menu == "Login" and not st.session_state["logged_in"]:
    st.title("🔑 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users:
            if users[username] == hash_password(password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Wrong Password")
        else:
            st.error("Username does not exist")

# ================= AFTER LOGIN =================
if st.session_state["logged_in"]:

    # Logout Button
    st.sidebar.success(f"Welcome {st.session_state['username']} 👋")
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

    # Load movie data
    movies = pickle.load(open('movies.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))

    OMDB_API_KEY = "c33ef208"

    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #141E30, #243B55);
    }

    h1 {
        text-align: center;
        color: #FF4B4B;
    }

    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 10px;
        font-size:18px;
    }

    .stSelectbox label {
        font-size:18px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Fetch Poster
    def fetch_movie_data(title):
        url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if data['Response'] == 'True':
            poster = data['Poster'] if data[
                                           'Poster'] != "N/A" else "https://via.placeholder.com/300x450.png?text=No+Image"
            year = data.get("Year", "N/A")
            rating = data.get("imdbRating", "N/A")

            return poster, year, rating
        else:
            return "https://via.placeholder.com/300x450.png?text=No+Image", "N/A", "N/A"


    # Recommend Function
    def recommend(movie):
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]

        movie_list = sorted(
            list(enumerate(distances)),
            reverse=True,
            key=lambda x: x[1]
        )[1:6]

        recommended_movies = []
        posters = []
        years = []
        ratings = []

        for i in movie_list:
            title = movies.iloc[i[0]].title
            poster, year, rating = fetch_movie_data(title)

            recommended_movies.append(title)
            posters.append(poster)
            years.append(year)
            ratings.append(rating)

        return recommended_movies, posters, years, ratings


    # Movie Selection
    selected_movie = st.selectbox("Select a movie", movies['title'].values)

    if st.button("🎥 Recommend Movies"):
        names, posters, years, ratings = recommend(selected_movie)
 
        st.subheader("Recommended Movies")

        cols = st.columns(5)

        for i in range(5):
            with cols[i]:
                st.image(posters[i], use_container_width=True)
                st.markdown(f"**{names[i]}**")
                st.write(f"📅 Year: {years[i]}")
                st.write(f"⭐ IMDb: {ratings[i]}")

    # ================= ABOUT SECTION =================
    st.markdown("---")
    st.subheader("About This Project")
    st.write("""
    This Movie Recommendation System uses Content-Based Filtering.
    Movie metadata such as genres, keywords, cast and overview are converted into vectors 
    using CountVectorizer. Cosine Similarity is then used to find similar movies.

    Posters are fetched dynamically using the OMDb API.
    User authentication is implemented using password hashing (SHA256).
    """)
    st.markdown("---")

    st.markdown(
        """
        <center>
    
        Developed by **Sneha Sunil Banpatte & Rutuja Arun Mulik**  
        BSc Computer Science  
        Eknath Sitaram Divekar College, Varvand  
        Savitribai Phule Pune University (SPPU)
    
        </center>
        """,
        unsafe_allow_html=True
    )