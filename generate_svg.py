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
)[:8]


total = sum(size for _, size in ranking)


# Card dimensions
width = 495
height = 120 + len(ranking) * 32


svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
    """
    <style>
      .title {
        font-family: Arial, sans-serif;
        font-size: 18px;
        font-weight: bold;
        fill: #00ff41;
      }

      .text {
        font-family: Arial, sans-serif;
        font-size: 13px;
        fill: #c9d1d9;
      }

      .percent {
        font-family: Arial, sans-serif;
        font-size: 13px;
        fill: #8b949e;
      }
    </style>
    """,

    # Background
    '<rect width="100%" height="100%" rx="10" fill="#0d1117"/>',

    # Title
    '<text x="30" y="40" class="title">Top Languages</text>'
]


colors = [
    "#00ff41",
    "#3178c6",
    "#f1e05a",
    "#e34c26",
    "#dea584",
    "#563d7c",
    "#00ADD8",
    "#89e051",
]


y = 80

for index, (name, size) in enumerate(ranking):

    percent = (size / total) * 100

    # Bar length
    bar_width = int(percent * 2.5)

    svg.append(
        f'<text x="30" y="{y}" class="text">{html.escape(name)}</text>'
    )

    # Background bar
    svg.append(
        f'<rect x="150" y="{y-12}" width="250" height="12" '
        f'rx="6" fill="#21262d"/>'
    )

    # Filled bar
    svg.append(
        f'<rect x="150" y="{y-12}" width="{bar_width}" height="12" '
        f'rx="6" fill="{colors[index % len(colors)]}"/>'
    )

    svg.append(
        f'<text x="420" y="{y}" class="percent">'
        f'{percent:.1f}%</text>'
    )

    y += 32


svg.append("</svg>")


with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))


print(f"Generated {OUTPUT}")
