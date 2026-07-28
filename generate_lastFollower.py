import os
import requests

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ["GITHUB_REPOSITORY_OWNER"]

OUTPUT = "followers-3d.svg"

query = """
query($login:String!){
  user(login:$login){
    followers(first:3){
      nodes{
        login
        avatarUrl(size:128)
        url
      }
    }
  }
}
"""

response = requests.post(
    "https://api.github.com/graphql",
    json={
        "query": query,
        "variables": {
            "login": USERNAME
        }
    },
    headers={
        "Authorization": f"Bearer {TOKEN}"
    }
)

response.raise_for_status()

followers = response.json()["data"]["user"]["followers"]["nodes"]

svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
width="900"
height="260">

<defs>

<filter id="shadow">
    <feDropShadow dx="0" dy="8" stdDeviation="8"
    flood-color="#00ffe7"
    flood-opacity="0.35"/>
</filter>

<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#0d1117"/>
    <stop offset="100%" stop-color="#161b22"/>
</linearGradient>

<style>
text {{
fill:white;
font-family:Arial;
}}

.card {{
animation: float 4s ease-in-out infinite;
}}

.card2 {{
animation-delay:.5s;
}}

.card3 {{
animation-delay:1s;
}}

@keyframes float {{
0% {{transform:translateY(0px)}}
50% {{transform:translateY(-8px)}}
100% {{transform:translateY(0px)}}
}}

.avatar {{
filter:url(#shadow);
}}

</style>

</defs>

<rect width="100%" height="100%" fill="url(#bg)" rx="20"/>

<text x="40" y="45"
font-size="28"
font-weight="bold">
Latest Followers
</text>
"""

x = 70

for i, f in enumerate(followers, 1):

    svg += f"""
<g class="card card{i}">
    <circle
        class="avatar"
        cx="{x}"
        cy="130"
        r="45"
        fill="#222"/>

    <image
        href="{f['avatarUrl']}"
        x="{x-45}"
        y="85"
        width="90"
        height="90"
        clip-path="circle(45px at 45px 45px)"
    />

    <text
        x="{x}"
        y="205"
        text-anchor="middle"
        font-size="16">
        @{escape(f['login'])}
    </text>
</g>
"""
    x += 260

svg += "</svg>"

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(svg)

print("Generated followers-3d.svg")
