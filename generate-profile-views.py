import json
import os

OUTPUT = "profile-views.svg"
COUNT_FILE = "views.json"

if os.path.exists(COUNT_FILE):
    with open(COUNT_FILE) as f:
        data = json.load(f)
else:
    data = {"views": 0}


data["views"] += 1


with open(COUNT_FILE, "w") as f:
    json.dump(data, f)


svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="150" height="20">
<rect width="150" height="20" rx="3" fill="#009dff"/>
<text x="75" y="14"
font-family="Arial"
font-size="11"
fill="white"
text-anchor="middle">
souls watched by {data["views"]}
</text>
</svg>
"""


with open(OUTPUT, "w") as f:
    f.write(svg)


print(f"Generated {OUTPUT}: {data['views']} views")
