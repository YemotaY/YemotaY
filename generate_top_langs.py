import os
import requests

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER")
README = "README.md"

query = """
query($login:String!){
  user(login:$login){
    repositories(first:100, ownerAffiliations: OWNER, isFork:false){
      nodes{
        languages(first:10, orderBy:{field:SIZE,direction:DESC}){
          edges{
            size
            node{
              name
            }
          }
        }
      }
    }
  }
}
"""

response = requests.post(
    "https://api.github.com/graphql",
    json={
        "query": query,
        "variables": {"login": USERNAME},
    },
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
    },
)

response.raise_for_status()

data = response.json()

languages = {}

repos = data["data"]["user"]["repositories"]["nodes"]

for repo in repos:
    for lang in repo["languages"]["edges"]:
        name = lang["node"]["name"]
        size = lang["size"]
        languages[name] = languages.get(name, 0) + size

total = sum(languages.values())

ranking = sorted(
    languages.items(),
    key=lambda x: x[1],
    reverse=True,
)

lines = [
    "## Top Languages\n",
]

for name, size in ranking[:10]:
    percent = size / total * 100
    lines.append(f"- **{name}** — {percent:.2f}%")

stats = "\n".join(lines)

with open(README, "r", encoding="utf-8") as f:
    readme = f.read()

start = "<!-- TOP_LANGUAGES_START -->"
end = "<!-- TOP_LANGUAGES_END -->"

new = (
    readme.split(start)[0]
    + start
    + "\n"
    + stats
    + "\n"
    + end
    + readme.split(end)[1]
)

with open(README, "w", encoding="utf-8") as f:
    f.write(new)

print("README updated.")
