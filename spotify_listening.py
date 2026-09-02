import os
import html
import requests
import base64

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

SVG_PATH = "spotify.svg"


def get_image_as_base64(url):
    if not url:
        return None

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "image/jpeg")
        encoded = base64.b64encode(response.content).decode("utf-8")

        return f"data:{content_type};base64,{encoded}"

    except requests.RequestException as e:
        print(f"Could not download album artwork: {e}")
        return None


def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"

    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(url, data=data)
    response.raise_for_status()

    return response.json()["access_token"]


def track_to_dict(track, is_playing=False):
    return {
        "song": track.get("name", "Unknown"),
        "artist": ", ".join(
            artist["name"]
            for artist in track.get("artists", [])
        ),
        "album": track.get("album", {}).get("name", ""),
        "image": (
            track.get("album", {})
            .get("images", [{}])[0]
            .get("url")
        ),
        "progress_ms": 0,
        "duration_ms": track.get("duration_ms", 0),
        "is_playing": is_playing,
    }


def get_current_playing():
    token = get_spotify_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # First try to get the currently playing track
    url = "https://api.spotify.com/v1/me/player/currently-playing"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        track = data.get("item")

        if track:
            return track_to_dict(
                track,
                is_playing=data.get("is_playing", False)
            )

    elif response.status_code != 204:
        print(f"Spotify currently-playing API error: {response.status_code}")

    # Nothing currently playing.
    # Get the most recently played track instead.
    print("Nothing currently playing. Checking recently played...")

    recent_url = "https://api.spotify.com/v1/me/player/recently-played"

    recent_response = requests.get(
        recent_url,
        headers=headers,
        params={"limit": 1}
    )

    if recent_response.status_code != 200:
        print(
            f"Spotify recently-played API error: "
            f"{recent_response.status_code}"
        )
        return None

    recent_data = recent_response.json()
    items = recent_data.get("items", [])

    if not items:
        return None

    track = items[0].get("track")

    if not track:
        return None

    return track_to_dict(track, is_playing=False)


def escape(value):
    return html.escape(str(value or ""), quote=True)


def generate_svg(track):
    if track:
        song = escape(track["song"])
        artist = escape(track["artist"])
        album = escape(track["album"])

        # Download album artwork and embed it directly into the SVG
        image = get_image_as_base64(track["image"])

        # Currently playing vs. last played
        status = "NOW PLAYING" if track["is_playing"] else "LAST PLAYED"

        image_element = ""

        if image:
            image_element = f"""
<image
    x="25"
    y="25"
    width="130"
    height="130"
    preserveAspectRatio="xMidYMid slice"
    clip-path="url(#cover)"
    href="{image}"
/>
"""

        svg = f"""<svg
    width="700"
    height="180"
    viewBox="0 0 700 180"
    xmlns="http://www.w3.org/2000/svg">

<defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#1DB954"/>
        <stop offset="100%" stop-color="#191414"/>
    </linearGradient>

    <clipPath id="cover">
        <rect
            x="25"
            y="25"
            width="130"
            height="130"
            rx="12"
        />
    </clipPath>
</defs>

<!-- Background -->
<rect
    width="700"
    height="180"
    rx="20"
    fill="url(#bg)"
/>

<!-- Album artwork -->
{image_element}

<!-- Status -->
<text
    x="180"
    y="55"
    font-family="Arial, Helvetica, sans-serif"
    font-size="14"
    font-weight="bold"
    fill="#ffffff"
    opacity="0.8">
    {status}
</text>

<!-- Song -->
<text
    x="180"
    y="90"
    font-family="Arial, Helvetica, sans-serif"
    font-size="27"
    font-weight="bold"
    fill="#ffffff">
    {song[:40]}
</text>

<!-- Artist -->
<text
    x="180"
    y="120"
    font-family="Arial, Helvetica, sans-serif"
    font-size="18"
    fill="#ffffff"
    opacity="0.9">
    {artist[:50]}
</text>

<!-- Album -->
<text
    x="180"
    y="148"
    font-family="Arial, Helvetica, sans-serif"
    font-size="14"
    fill="#ffffff"
    opacity="0.65">
    {album[:55]}
</text>

<!-- Spotify indicator -->
<circle
    cx="650"
    cy="35"
    r="12"
    fill="#1DB954"
/>

<circle
    cx="650"
    cy="35"
    r="5"
    fill="#ffffff"
/>

</svg>
"""

    else:
        # Only shown if Spotify has no recently played track either
        svg = """<svg
    width="700"
    height="180"
    viewBox="0 0 700 180"
    xmlns="http://www.w3.org/2000/svg">

<defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#191414"/>
        <stop offset="100%" stop-color="#333333"/>
    </linearGradient>
</defs>

<rect
    width="700"
    height="180"
    rx="20"
    fill="url(#bg)"
/>

<text
    x="350"
    y="82"
    text-anchor="middle"
    font-family="Arial, Helvetica, sans-serif"
    font-size="22"
    font-weight="bold"
    fill="#ffffff">
    No Spotify history available
</text>

<text
    x="350"
    y="115"
    text-anchor="middle"
    font-family="Arial, Helvetica, sans-serif"
    font-size="14"
    fill="#ffffff"
    opacity="0.6">
    Spotify
</text>

</svg>
"""

    directory = os.path.dirname(SVG_PATH)

    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(SVG_PATH, "w", encoding="utf-8") as file:
        file.write(svg)

    print(f"SVG written to {SVG_PATH}")


if __name__ == "__main__":
    current = get_current_playing()

    if current:
        status = "currently playing" if current["is_playing"] else "last played"

        print(
            f"{status.capitalize()}: "
            f"{current['song']} by {current['artist']}"
        )
    else:
        print("No Spotify track available.")

    generate_svg(current)
