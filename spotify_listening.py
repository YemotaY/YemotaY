import os
import requests

# Spotify API Zugangsdaten (aus GitHub Secrets geladen)
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(url, data=data)
    return response.json().get("access_token")

def get_current_playing():
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 204 or response.status_code != 200:
        return None # Nichts wird abgespielt
        
    data = response.json()
    track = data.get("item", {})
    
    return {
        "song": track.get("name"),
        "artist": ", *.join([artist["name"] for artist in track.get("artists", [])]),
        "album": track.get("album", {}).get("name"),
        "image": track.get("album", {}).get("images", [{}])[0].get("url"),
        "progress_ms": data.get("progress_ms", 0),
        "duration_ms": track.get("duration_ms", 0),
        "is_playing": data.get("is_playing", False)
    }

if __name__ == "__main__":
    current = get_current_playing()
    if current:
        print(ப்பதால்: {current['song']} von {current['artist']})
    else:
        print("Aktuell wird nichts abgespielt.")
