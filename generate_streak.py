import os
import requests
from datetime import date, timedelta

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER")

OUTPUT = "github-streak.svg"


query = """
query($login:String!){
  user(login:$login){
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            contributionCount
            date
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
        "variables": {
            "login": USERNAME
        },
    },
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
    },
)

response.raise_for_status()

data = response.json()


days = []

for week in data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
    for day in week["contributionDays"]:
        days.append(
            {
                "date": day["date"],
                "count": day["contributionCount"]
            }
        )


# Calculate current streak
streak = 0

for day in reversed(days):
    if day["count"] > 0:
        streak += 1
    else:
        break


# Calculate longest streak
longest = 0
current = 0

for day in days:
    if day["count"] > 0:
        current += 1
        longest = max(longest, current)
    else:
        current = 0


total_contributions = sum(
    d["count"] for d in days
)


# SVG card
width = 495
height = 195


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

.big {
    font-family: Arial, sans-serif;
    font-size: 42px;
    font-weight: bold;
    fill: #00ff41;
}

.label {
    font-family: Arial, sans-serif;
    font-size: 14px;
    fill: #c9d1d9;
}

.small {
    font-family: Arial, sans-serif;
    font-size: 13px;
    fill: #8b949e;
}

</style>
""",

# background
'<rect width="100%" height="100%" rx="10" fill="#0d1117"/>',

# title
f'<text x="{width/2-100}" y="40" class="title">GitHub Streak</text>',

# fire icon
f'<text x="{width/2-100}" y="95" font-size="45">🔥</text>',

# streak number
f'<text x="{width/2}" y="95" class="big">{streak}</text>',

f'<text x="{width/2}" y="120" class="label">day streak</text>',


f'<text x="40" y="160" class="small">'
f'Longest streak: {longest} days'
f'</text>',


f'<text x="260" y="160" class="small">'
f'Total contributions: {total_contributions}'
f'</text>',


"</svg>"
]


with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))


print(
    f"Generated {OUTPUT}: "
    f"{streak} current streak, "
    f"{longest} longest streak"
)
