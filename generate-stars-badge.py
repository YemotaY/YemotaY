import os
import requests

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER")

OUTPUT = "stars.svg"


query = """
query($login:String!){
  user(login:$login){
    repositories(first:100){
      nodes{
        stargazerCount
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
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }
)

response.raise_for_status()

repos = response.json()["data"]["user"]["repositories"]["nodes"]

stars = sum(
    repo["stargazerCount"]
    for repo in repos
)


svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="110" height="20">
<rect width="110" height="20" rx="3" fill="#009dff"/>
<text x="55" y="14"
font-family="Arial"
font-size="11"
fill="white"
text-anchor="middle">
Stars {stars}
</text>
</svg>
"""


with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(svg)


print(f"Generated {OUTPUT}: {stars} stars")
