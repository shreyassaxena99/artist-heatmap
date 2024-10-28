# Spotify Liked Songs Artist Origin Heatmap

This project is a Streamlit app that allows users to connect their Spotify account, analyze their "Liked Songs" playlist, and display the countries of origin for the artists on an interactive heatmap. The map visualizes the distribution of artists from different countries based on the user's liked songs.

## Features

- *Spotify Integration*: Connect your Spotify account to retrieve your liked songs.

- *Batch API Requests*: Uses the MusicBrainz API to gather country information for artists from the liked songs playlist.

- *Interactive Heatmap*: Visualize artist distribution on a world map using Plotly's Choropleth.

- *Country Artist Information*: Select a country to view the list of artists from that country.

## Setup Instructions

### Prerequisites

Python 3.7 or higher

Spotify Developer account (for API credentials)

### Step 1: Clone the Repository

```
git clone https://github.com/shreyassaxena99/artist-heatmap
cd <repository-directory>
```

### Step 2: Create a Virtual Environment

To create a virtual environment:

```
python -m venv venv
```

Activate the virtual environment:

Windows:

```
venv\Scripts\activate
```
macOS/Linux:

```
source venv/bin/activate
```

### Step 3: Install Dependencies

Install the required dependencies from requirements.txt:

```
pip install -r requirements.txt
```

### Step 4: Set Up Spotify Credentials

Go to the Spotify Developer Dashboard.

Create an application to get your Client ID, Client Secret, and set a Redirect URI.

Replace the placeholder values in the script (`SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI`) with your actual credentials.

### Step 5: Run the Streamlit App

To run the app, use the following command:

```
streamlit run spotify_artist_map.py
```

## Usage

*Connect to Spotify*: Click the "Connect to Spotify" button to authenticate your Spotify account and allow the app to access your liked songs.

*Fetch Liked Songs*: The app will retrieve your liked songs and display a progress bar.

*Fetch Artist Information*: Artist information is then fetched in batches, using the MusicBrainz API to determine the country of origin for each artist.

*View Heatmap*: The countries of origin for artists are displayed on an interactive heatmap.

*Select a Country*: Use the dropdown to select a country and see the list of artists from that country.

## Files in the Repository

`spotify_artist_map.py`: The main script that runs the Streamlit app.

`requirements.txt`: The list of dependencies required to run the app.

## Notes

Ensure that your Spotify credentials (Client ID, Client Secret, Redirect URI) are properly set in the script before running the app.

The MusicBrainz API is used to fetch artist information, and the script implements batching and a delay to prevent rate limiting.

## License

This project is licensed under the MIT License.

## Acknowledgements

Spotify API

MusicBrainz API

Plotly for interactive map visualization