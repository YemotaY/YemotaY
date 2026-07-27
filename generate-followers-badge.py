import os
import requests

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER")

OUTPUT = "followers.svg"


query = """
query($login:String!){
  user(login:$login){
    followers {
      totalCount
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
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }
)

response.raise_for_status()

followers = response.json()["data"]["user"]["followers"]["totalCount"]


svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="120" height="20">
<rect width="120" height="20" rx="3" fill="#009dff"/>
<text x="60" y="14"
font-family="Arial"
font-size="11"
fill="white"
text-anchor="middle">
Frens {followers}
</text>
</svg>
"""


with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(svg)


print(f"Generated {OUTPUT}: {followers} followers")
