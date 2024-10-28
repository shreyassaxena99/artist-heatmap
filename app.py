import pycountry
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import pandas as pd
import plotly.graph_objects as go
import random
import time
import sys

# Spotify API credentials
SPOTIPY_CLIENT_ID = "2cf4725686cb46f1b4b5a240cd1f8e06"
SPOTIPY_CLIENT_SECRET = "749e5d021e3f4a10a4f5c1649399a2f5"
SPOTIPY_REDIRECT_URI = "http://localhost:8888/callback"

# Spotify authorization scope
SCOPE = "user-library-read"

# Set page width to wide
st.set_page_config(layout="wide")

# App title
st.title("Spotify Liked Songs Artist Origin Heatmap")
st.session_state["selected_country"] = None

# Spotify OAuth
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE,
    )
)

# Connect to Spotify
if st.button("Connect to Spotify"):
    st.session_state["token_info"] = sp.auth_manager.get_access_token(as_dict=True)
    if st.session_state["token_info"]:
        st.success("Successfully connected to Spotify!")
    else:
        st.error("Failed to connect to Spotify.")

if "token_info" in st.session_state:
    # Get user's liked songs
    st.session_state["liked_songs"] = []
    total_tracks = sp.current_user_saved_tracks(limit=1)[
        "total"
    ]  # Get the total number of liked songs
    liked_songs_subheader = st.subheader("Fetching liked songs...")
    start = time.time()
    progress_bar = st.progress(0)
    results = sp.current_user_saved_tracks(limit=50)
    st.session_state["liked_songs"].extend(results["items"])
    progress_bar.progress(len(st.session_state["liked_songs"]) / total_tracks)
    if len(st.session_state["liked_songs"]) >= total_tracks:
        st.success("Liked songs fetched successfully!")

    while results["next"]:
        results = sp.next(results)
        st.session_state["liked_songs"].extend(results["items"])
        progress_bar.progress(len(st.session_state["liked_songs"]) / total_tracks)

    print(f"Time taken to gather liked songs: {time.time() - start}")

    progress_bar.empty()
    liked_songs_subheader.empty()

    # Function to get artist information with highest score
    def get_artist_info_batch(artist_names, progress_bar, current_batch, total_batches):
        time.sleep(0.5 + random.uniform(0, 0.5))
        query = " OR ".join([f"artist:{name}" for name in artist_names])
        url = f"https://musicbrainz.org/ws/2/artist/?query={query}&fmt=json"
        response = requests.get(url)
        progress_bar.progress(min((current_batch + 1) / total_batches, 1.0))
        artist_info = []
        if response.status_code == 200:
            data = response.json()
            if "artists" in data:
                artist_dict = {}
                for artist in data["artists"]:
                    name = artist["name"]
                    score = int(artist.get("score", 0))
                    country = artist.get("country", None)
                    if name not in artist_dict or score > artist_dict[name]["score"]:
                        artist_dict[name] = {"country": country, "score": score}
                artist_info = [
                    {"name": name, "country": info["country"]}
                    for name, info in artist_dict.items()
                ]
        return artist_info

    # Get artist information asynchronously
    artist_info_subheader = st.subheader("Fetching artist information...")
    artist_progress_bar = st.progress(0)
    st.session_state["artist_info"] = []
    batch_size = 50  # Number of artists to include in a single batch request

    start = time.time()
    for i in range(0, len(st.session_state["liked_songs"]), batch_size):
        batch_artists = st.session_state["liked_songs"][i : i + batch_size]
        artist_names = [song["track"]["artists"][0]["name"] for song in batch_artists]
        batch_artist_info = get_artist_info_batch(
            artist_names,
            artist_progress_bar,
            i // batch_size,
            len(st.session_state["liked_songs"]) // batch_size,
        )
        st.session_state["artist_info"].extend(batch_artist_info)

    print(f"Time taken to gather artist info: {time.time() - start}")

    # Count the number of artists per country
    if st.session_state["artist_info"]:
        artist_progress_bar.empty()
        artist_info_subheader.empty()
        # Convert country codes to full country names
        country_names = []
        st.session_state["artist_by_country"] = {}
        for info in st.session_state["artist_info"]:
            try:
                country = pycountry.countries.get(alpha_2=info["country"])
                country_name = country.name if country else info["country"]
                country_names.append(country_name)
                if country_name not in st.session_state["artist_by_country"]:
                    st.session_state["artist_by_country"][country_name] = []
                st.session_state["artist_by_country"][country_name].append(info["name"])
            except:
                e = sys.exc_info()[0]
                print(
                    f"artist_info that generated an exception: {info}. exception generated: {e}"
                )

        # Count the number of artists per country
        country_counts = pd.Series(country_names).value_counts().reset_index()
        st.session_state["country_counts"] = country_counts
        country_counts.columns = ["Country", "Count"]
        print(country_counts.head(10))

        # Plot heatmap with transparency, white country outlines, and a bottom legend
        fig = go.Figure(
            go.Choropleth(
                locations=country_counts["Country"],
                locationmode="country names",
                z=country_counts["Count"],
                text=country_counts["Country"],
                colorscale="Viridis",
                marker_line_color="white",
                marker_line_width=1.5,
                marker={"opacity": 0.6},
                showscale=True,
                zmin=0,
                zmax=country_counts["Count"].max(),
            )
        )

        fig.update_layout(
            title_text="Transparent Heatmap of Artists Countries of Origin from Liked Songs Playlist",
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor="white",
                projection_type="natural earth",
                bgcolor="rgba(0,0,0,0)",
                fitbounds="locations",
            ),
            margin=dict(l=0, r=0, t=20, b=20),  # Set margins to reduce gaps
            coloraxis_colorbar=dict(
                title="Number of Artists",
                orientation="h",
                y=-0.3,  # Position the legend below the map
                x=0.5,
                xanchor="center",
            ),
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No artist country information found.")

    def get_artists_by_country():
        if st.session_state["selected_country"]:
            selected_country = st.session_state["selected_country"]
            st.write(f"Artists from {selected_country}:")
            for artist in st.session_state["artist_by_country"][selected_country]:
                st.write(f"- {artist}")

    if st.session_state["country_counts"] is not None:
        # Clickable country list to display artists from that country
        st.session_state["selected_country"] = st.selectbox(
            "Select a country to see the artists:",
            options=st.session_state["country_counts"]["Country"],
            on_change=get_artists_by_country()
        )

else:
    st.warning("Please connect to Spotify to proceed.")

st.caption(
    "Note: Make sure to replace placeholders such as 'your_spotify_client_id', 'your_spotify_client_secret', and 'your_redirect_uri' with your actual Spotify credentials."
)
