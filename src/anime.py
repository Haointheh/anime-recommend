import pickle
import streamlit as st
import requests

# ---------------------- CSS ----------------------
st.markdown(
    """
<style>

.stApp {
    background: linear-gradient(135deg, #89CFF0, #ffffff, #4673B4);
    background-attachment: fixed;
}

/* Center Header */
.stHeader {
    font-size: 40px;
    font-family: 'Courier New', Courier, monospace;
    font-weight: bold;
    color: black;
    text-align: center;
    margin-bottom: 25px;
}

/* Glassmorphism Card */
.card {
    background: rgba(255, 255, 255, 0.25);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    backdrop-filter: blur(7px);
    -webkit-backdrop-filter: blur(7px);
    border-radius: 18px;
    padding: 15px;
    text-align: center;
    margin-bottom: 25px;
}

/* Card Title */
.card-title {
    font-size: 18px;
    font-weight: bold;
    color: black;
    margin-top: 10px;
}

/* Hover Animation for Anime Posters */
.anime-image {
    transition: transform 0.3s ease;
    border-radius: 14px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.25);
}

.anime-image:hover {
    transform: scale(1.08);
}

</style>
""",
    unsafe_allow_html=True
)

# ---------------------- Heading ----------------------
st.markdown('<h1 class="stHeader">Anime Recommendation</h1>', unsafe_allow_html=True)


# ---------------------- Functions ----------------------
def fetch_poster(uid):
    url = f"https://api.jikan.moe/v4/anime/{uid}"
    response = requests.get(url)

    if response.status_code != 200:
        return None, None, None, None, None

    data = response.json()

    try:
        poster = data['data']['images']['jpg']['image_url']
        title = data['data']['title']
        score = data['data']['score']
        episodes = data['data']['episodes']
        genres = ', '.join([g['name'] for g in data['data']['genres']])

        return poster, title, score, episodes, genres

    except:
        return None, None, None, None, None


def recommend(selected_anime):
    index = animes[animes['title'] == selected_anime].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    names, posters, details = [], [], []

    for i in distances[1:16]:
        uid = animes.iloc[i[0]].uid
        poster, title, score, episodes, genres = fetch_poster(uid)

        if poster:
            posters.append(poster)
            names.append(title)
            details.append({
                "score": score,
                "episodes": episodes,
                "genres": genres
            })

    return names, posters, details


# ---------------------- Load Data ----------------------
animes = pickle.load(open('artifacts/Alist.pkl', 'rb'))
similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))

# ---------------------- Input ----------------------
anime_list = animes['title'].values
selected_anime = st.selectbox(
    "Type or select a movie to get recommendation",
    anime_list
)


# ---------------------- Show Recommendations ----------------------
if st.button("Show Recommendation"):
    names, posters, details = recommend(selected_anime)

    if names:
        cols = [st.columns(5), st.columns(5), st.columns(5)]

        for i in range(min(len(names), 15)):
            row, col = divmod(i, 5)

            with cols[row][col]:
                st.markdown('<div class="card">', unsafe_allow_html=True)

                # Hover animated poster
                st.markdown(
                    f'<img src="{posters[i]}" class="anime-image" width="100%">',
                    unsafe_allow_html=True
                )

                # Card title
                st.markdown(
                    f'<div class="card-title">{names[i]}</div>',
                    unsafe_allow_html=True
                )

                # Details section
                with st.expander("Details"):
                    st.write(f"⭐ **Score:** {details[i]['score']}/10")
                    st.write(f"🎬 **Episodes:** {details[i]['episodes']}")
                    st.write(f"🏷 **Genres:** {details[i]['genres']}")

                st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.error("No recommendations found.")
