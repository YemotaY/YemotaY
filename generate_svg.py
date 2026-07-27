import os
import requests
import html

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER")

OUTPUT = "top-languages.svg"

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

for repo in data["data"]["user"]["repositories"]["nodes"]:
    for lang in repo["languages"]["edges"]:
        name = lang["node"]["name"]
        size = lang["size"]
        languages[name] = languages.get(name, 0) + size


ranking = sorted(
    languages.items(),
    key=lambda x: x[1],
    reverse=True
)[:10]

total = sum(x[1] for x in ranking)

width = 700
height = 80 + len(ranking) * 45

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
    """
    <style>
      .title {
        font: bold 22px Arial;
        fill: #ffffff;
      }
      .label {
        font: 15px Arial;
        fill: #ffffff;
      }
      .percent {
        font: 14px Arial;
        fill: #aaaaaa;
      }
    </style>
    """,
    '<rect width="100%" height="100%" rx="15" fill="#0d1117"/>',
    '<text x="30" y="40" class="title">Top Languages</text>'
]

y = 80

colors = [
    "#3178c6",
    "#f1e05a",
    "#3572A5",
    "#dea584",
    "#00ADD8",
    "#e34c26",
    "#563d7c",
    "#89e051",
    "#4F5D95",
    "#701516"
]

for index, (name, size) in enumerate(ranking):
    percent = (size / total) * 100
    bar_width = int(percent * 4)

    svg.append(
        f'<text x="30" y="{y}" class="label">{html.escape(name)}</text>'
    )

    svg.append(
        f'<rect x="160" y="{y-15}" width="{bar_width}" height="18" '
        f'rx="5" fill="{colors[index % len(colors)]}"/>'
    )

    svg.append(
        f'<text x="{180 + bar_width}" y="{y}" '
        f'class="percent">{percent:.1f}%</text>'
    )

    y += 45

svg.append("</svg>")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))

print("Generated", OUTPUT)
