import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import pickle
import dotenv

dotenv.load_dotenv()
Client_ID = os.getenv("Spotify_ID")
Client_Secret = os.getenv("Spotify_Secret")
Redirect_URI = "http://localhost:8080/callback/"

def get_spotify_client():
    if os.path.exists("Credentials/spotify_pickle.token"):
        with open("Credentials/spotify_pickle.token","rb") as token_file:
            token_info = pickle.load(token_file) 
        sp_auth = SpotifyOAuth(
            client_id=Client_ID,
            client_secret=Client_Secret,
            redirect_uri=Redirect_URI
        )
        if sp_auth.is_token_expired(token_info):
            token_info = sp_auth.refresh_access_token(token_info["refresh_token"])
            with open("Credentials/spotify_pickle.token", "wb") as token_file:
                pickle.dump(token_info, token_file)
    else:
        # Perform authentication flow if no token exists
        sp_auth = SpotifyOAuth(
            client_id=Client_ID,
            client_secret=Client_Secret,
            redirect_uri=Redirect_URI,
            scope="user-read-playback-state,user-modify-playback-state"
        )
        token_info = sp_auth.get_access_token(as_dict=True)
        with open("Credentials/spotify_pickle.token", "wb") as token_file:
            pickle.dump(token_info, token_file)
    sp = spotipy.Spotify(auth=token_info["access_token"])
    return sp

def search_track(song_name, artist_name=None):
    sp = get_spotify_client()
    query = f"track:{song_name}"
    if artist_name:
        query += f" artist:{artist_name}"
    results = sp.search(q=query, type="track", limit=1)
    
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_uri = track['uri']
        return track_uri#, track['name'], track['artists'][0]['name']
    else:
        return "Track could not be found"
    
def play_music(track_uri=None, playlist_uri=None, device_name=None):
    spotify = get_spotify_client()
    
    # Get list of devices
    devices = spotify.devices()
    if not devices['devices']:
        print("No devices available for playback.")
        return

    # Find the specified device
    device_id = None
    for device in devices['devices']:
        if device_name and device['name'].lower() == device_name.lower():
            device_id = device['id']
            break
    if not device_id:
        device_id = devices['devices'][0]['id']  # Default to the first available device

    # Start playback
    if track_uri:
        spotify.start_playback(device_id=device_id, uris=[track_uri])
        return (f"Playing track: {track_uri} on device: {device_name or devices['devices'][0]['name']}")
    elif playlist_uri:
        spotify.start_playback(device_id=device_id, context_uri=playlist_uri)
        return (f"Playing playlist: {playlist_uri} on device: {device_name or devices['devices'][0]['name']}")
    else:
        return ("No track or playlist URI provided.")