#!/usr/bin/env python3

import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

USERNAME = "NyerahMT"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

README = Path("README.md")
ASSETS = Path("assets")
ASSETS.mkdir(exist_ok=True)

PORT_LABELS = {
    "engine-sim-ios": "Engine Simulator iOS",
    "principia": "Principia iOS",
    "fluid-engine-swift": "Fluid Engine Swift",
}

START = "<!-- AUTO-STATS:START -->"
END = "<!-- AUTO-STATS:END -->"


def api(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": f"{USERNAME}-profile-stats",
    }

    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    request = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(request) as response:
        return (
            json.loads(response.read().decode()),
            response.headers.get("Link"),
        )


def paginate(url):
    results = []

    while url:
        data, link = api(url)

        if not isinstance(data, list):
            return data

        results.extend(data)
        url = None

        if link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.split("<", 1)[1].split(">", 1)[0]
                    break

    return results


def count_authored_commits(repo):
    branch = urllib.parse.quote(
        repo["default_branch"],
        safe="",
    )

    url = (
        f"https://api.github.com/repos/{repo['full_name']}/commits"
        f"?author={USERNAME}&sha={branch}&per_page=100"
    )

    try:
        return len(paginate(url))

    except Exception as error:
        print(
            f"Authored count failed for "
            f"{repo['full_name']}: {error}"
        )
        return 0


def get_ahead_count(repo):
    if not repo.get("fork"):
        return 0

    try:
        details, _ = api(
            f"https://api.github.com/repos/{repo['full_name']}"
        )

        parent = details.get("parent")

        if not parent:
            return 0

        base = urllib.parse.quote(
            parent["default_branch"],
            safe="",
        )

        head = urllib.parse.quote(
            f"{USERNAME}:{repo['default_branch']}",
            safe=":",
        )

        comparison, _ = api(
            f"https://api.github.com/repos/"
            f"{parent['full_name']}/compare/"
            f"{base}...{head}"
        )

        return comparison.get("ahead_by", 0)

    except Exception as error:
        print(
            f"Compare failed for "
            f"{repo['full_name']}: {error}"
        )
        return 0


def generate_svg(
    port_commits,
    attributed_commits,
    original_commits,
    port_count,
):
    values = [
        port_commits,
        attributed_commits,
        original_commits,
    ]

    maximum = max(values + [1])

    def height(value):
        if value <= 0:
            return 4

        return 28 + round((value / maximum) * 115)

    def column(
        x,
        value,
        label,
        front,
        top,
        side,
    ):
        h = height(value)

        base_y = 228
        y = base_y - h

        width = 92
        depth_x = 18
        depth_y = 12

        return f"""
<g>
    <polygon
        points="
            {x},{y}
            {x + depth_x},{y - depth_y}
            {x + width + depth_x},{y - depth_y}
            {x + width},{y}
        "
        fill="{top}"
    />

    <polygon
        points="
            {x + width},{y}
            {x + width + depth_x},{y - depth_y}
            {x + width + depth_x},{base_y - depth_y}
            {x + width},{base_y}
        "
        fill="{side}"
    />

    <rect
        x="{x}"
        y="{y}"
        width="{width}"
        height="{h}"
        rx="3"
        fill="{front}"
    />

    <text
        x="{x + width / 2}"
        y="{y - 22}"
        text-anchor="middle"
        class="number"
    >{value}</text>

    <text
        x="{x + width / 2 + 7}"
        y="258"
        text-anchor="middle"
        class="label"
    >{label}</text>
</g>
"""

    svg = f"""
<svg
    width="720"
    height="310"
    viewBox="0 0 720 310"
    xmlns="http://www.w3.org/2000/svg"
>

<defs>
    <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#0d1117"/>
        <stop offset="100%" stop-color="#111827"/>
    </linearGradient>

    <pattern
        id="grid"
        width="22"
        height="22"
        patternUnits="userSpaceOnUse"
    >
        <path
            d="M 22 0 L 0 0 0 22"
            fill="none"
            stroke="#30363d"
            stroke-width="0.55"
            opacity="0.42"
        />
    </pattern>
</defs>

<style>
.title {{
    fill: #f0f6fc;
    font: 700 23px -apple-system, BlinkMacSystemFont,
          "Segoe UI", sans-serif;
}}

.subtitle {{
    fill: #8b949e;
    font: 13px -apple-system, BlinkMacSystemFont,
          "Segoe UI", sans-serif;
}}

.number {{
    fill: #f0f6fc;
    font: 700 27px -apple-system, BlinkMacSystemFont,
          "Segoe UI", sans-serif;
}}

.label {{
    fill: #c9d1d9;
    font: 13px -apple-system, BlinkMacSystemFont,
          "Segoe UI", sans-serif;
}}

.footer {{
    fill: #8b949e;
    font: 12px -apple-system, BlinkMacSystemFont,
          "Segoe UI", sans-serif;
}}
</style>

<rect
    width="720"
    height="310"
    rx="14"
    fill="url(#background)"
/>

<rect
    x="1"
    y="1"
    width="718"
    height="308"
    rx="13"
    fill="none"
    stroke="#30363d"
    stroke-width="2"
/>

<rect
    x="22"
    y="72"
    width="676"
    height="180"
    fill="url(#grid)"
    opacity="0.75"
/>

<text x="26" y="38" class="title">
Development Activity
</text>

<text x="26" y="59" class="subtitle">
Live repository history · {port_count} active ports
</text>

<!-- floor -->
<polygon
    points="56,232 590,232 630,207 96,207"
    fill="#161b22"
    stroke="#30363d"
    stroke-width="1"
/>

{column(
    120,
    port_commits,
    "Port commits",
    "#1f6feb",
    "#79c0ff",
    "#1158c7",
)}

{column(
    310,
    attributed_commits,
    "GitHub attributed",
    "#8957e5",
    "#d2a8ff",
    "#6e40c9",
)}

{column(
    500,
    original_commits,
    "Original repo",
    "#238636",
    "#56d364",
    "#196c2e",
)}

<text
    x="360"
    y="289"
    text-anchor="middle"
    class="footer"
>
Port commits = commits currently ahead of upstream
</text>

</svg>
"""

    (ASSETS / "development-activity.svg").write_text(
        svg.strip(),
        encoding="utf-8",
    )


def generate_markdown(
    ports,
    original_commits,
):
    port_commits = sum(
        port["ahead"]
        for port in ports
    )

    attributed_commits = sum(
        port["authored"]
        for port in ports
    )

    rows = "\n".join(
        f"| **{port['label']}** | "
        f"{port['ahead']} | "
        f"{port['authored']} |"
        for port in sorted(
            ports,
            key=lambda item: item["ahead"],
            reverse=True,
        )
    )

    return f"""
<div align="center">

<img
src="https://raw.githubusercontent.com/{USERNAME}/{USERNAME}/main/assets/development-activity.svg"
width="720"
/>

</div>

| Port | Commits ahead | GitHub attributed |
|:---|---:|---:|
{rows}
| **Total** | **{port_commits}** | **{attributed_commits}** |

<sub>
"Commits ahead" measures development currently added beyond upstream.
"GitHub attributed" counts commits GitHub directly associates with my account.
The two metrics overlap.
</sub>
""".strip()


def update_readme(markdown):
    text = README.read_text(encoding="utf-8")

    block = (
        f"{START}\n"
        f"{markdown}\n"
        f"{END}"
    )

    pattern = re.compile(
        re.escape(START)
        + r".*?"
        + re.escape(END),
        re.DOTALL,
    )

    if pattern.search(text):
        text = pattern.sub(block, text)

    else:
        text += (
            "\n\n# Development Activity\n\n"
            f"{block}\n"
        )

    README.write_text(
        text,
        encoding="utf-8",
    )


def main():
    repos = paginate(
        f"https://api.github.com/users/{USERNAME}/repos"
        "?type=owner"
        "&sort=updated"
        "&direction=desc"
        "&per_page=100"
    )

    repos = [
        repo
        for repo in repos
        if repo["name"].lower() != USERNAME.lower()
    ]

    original_repos = [
        repo
        for repo in repos
        if not repo.get("fork")
    ]

    fork_repos = [
        repo
        for repo in repos
        if repo.get("fork")
    ]

    original_commits = sum(
        count_authored_commits(repo)
        for repo in original_repos
    )

    ports = []

    for repo in fork_repos:
        if repo["name"] not in PORT_LABELS:
            continue

        ports.append(
            {
                "label": PORT_LABELS[repo["name"]],
                "authored": count_authored_commits(repo),
                "ahead": get_ahead_count(repo),
            }
        )

    port_commits = sum(
        port["ahead"]
        for port in ports
    )

    attributed_commits = sum(
        port["authored"]
        for port in ports
    )

    generate_svg(
        port_commits,
        attributed_commits,
        original_commits,
        len(ports),
    )

    markdown = generate_markdown(
        ports,
        original_commits,
    )

    update_readme(markdown)

    print(
        f"Port commits: {port_commits}\n"
        f"GitHub attributed: {attributed_commits}\n"
        f"Original repo commits: {original_commits}\n"
        f"Active ports: {len(ports)}"
    )


if __name__ == "__main__":
    main()
