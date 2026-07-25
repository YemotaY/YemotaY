#!/usr/bin/env python3
"""Generate assets/live-monitor.svg for the profile README.

Run by GitHub Actions on a schedule so the "Live Monitoring" panel
in the README updates automatically. Everything shown is derived from
real timestamps / pseudo-metrics, not static text.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import os

REPO_START = dt.date(2024, 1, 1)  # adjust to your first commit date
TASKS = [
    "Refactoring parser...",
    "Training tiny model...",
    "Garbage collecting...",
    "Compiling Rust (again)...",
    "Debugging heisenbug...",
    "Writing tests I promised...",
    "Optimizing hot loop...",
    "Reading logs at 3AM...",
]


def bar(pct: int, width: int = 10) -> str:
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


def deterministic(seed: str, lo: int, hi: int) -> int:
    """Stable-per-hour pseudo value so the SVG changes each run but is reproducible."""
    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    return lo + (h % (hi - lo + 1))


def main() -> None:
    now = dt.datetime.now(dt.timezone.utc)
    hour_seed = now.strftime("%Y-%m-%d-%H")

    cpu = deterministic("cpu" + hour_seed, 35, 95)
    temp = deterministic("temp" + hour_seed, 55, 82)
    task = TASKS[deterministic("task" + hour_seed, 0, len(TASKS) - 1)]
    uptime = (now.date() - REPO_START).days

    lines = [
        ("CPU Usage", f"{bar(cpu)}  {cpu}%"),
        ("Status", "Building AI"),
        ("Temperature", f"{temp}°C"),
        ("Current Task", task),
        ("Uptime", f"{uptime} days"),
        ("Last Sync", now.strftime("%Y-%m-%d %H:%M UTC")),
    ]

    row_h = 34
    pad = 24
    height = pad * 2 + row_h * len(lines) + 30
    width = 460

    rows = []
    y = pad + 40
    for label, value in lines:
        rows.append(
            f'<text x="{pad}" y="{y}" class="label">{label}</text>'
            f'<text x="{width - pad}" y="{y}" class="value" text-anchor="end">{escape(value)}</text>'
        )
        y += row_h

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" role="img">
  <style>
    .bg {{ fill: #0d1117; }}
    .frame {{ fill: none; stroke: #30363d; stroke-width: 1; }}
    .title {{ fill: #58a6ff; font: bold 16px 'JetBrains Mono', Consolas, monospace; }}
    .label {{ fill: #8b949e; font: 13px 'JetBrains Mono', Consolas, monospace; }}
    .value {{ fill: #3fb950; font: 13px 'JetBrains Mono', Consolas, monospace; }}
  </style>
  <rect class="bg" x="0" y="0" width="{width}" height="{height}" rx="10" />
  <rect class="frame" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" />
  <text x="{pad}" y="{pad + 12}" class="title">◉ LIVE SYSTEM MONITOR</text>
  {''.join(rows)}
</svg>
"""

    os.makedirs("assets", exist_ok=True)
    with open("assets/live-monitor.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Wrote assets/live-monitor.svg")


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


if __name__ == "__main__":
    main()
