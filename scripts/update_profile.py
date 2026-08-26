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
    items = []

    while url:
        data, link = api(url)

        if not isinstance(data, list):
            return data

        items.extend(data)
        url = None

        if link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.split("<", 1)[1].split(">", 1)[0]
                    break

    return items


def count_authored_commits(repo):
    branch = urllib.parse.quote(repo["default_branch"], safe="")

    url = (
        f"https://api.github.com/repos/{repo['full_name']}/commits"
        f"?author={USERNAME}&sha={branch}&per_page=100"
    )

    try:
        return len(paginate(url))
    except Exception as e:
        print(f"Authored count failed for {repo['full_name']}: {e}")
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
            f"{parent['full_name']}/compare/{base}...{head}"
        )

        return comparison.get("ahead_by", 0)

    except Exception as e:
        print(f"Compare failed for {repo['full_name']}: {e}")
        return 0


def generate_svg(
    original_commits,
    attributed_fork_commits,
    port_commits,
    port_count,
):
    svg = f"""
<svg width="560" height="250" viewBox="0 0 560 250"
xmlns="http://www.w3.org/2000/svg">
<style>
.bg{{fill:#0d1117}}
.border{{fill:none;stroke:#30363d;stroke-width:2}}
.title{{fill:#f0f6fc;font:600 22px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
.big{{fill:#58a6ff;font:700 34px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
.label{{fill:#8b949e;font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
.small{{fill:#c9d1d9;font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
</style>

<rect class="bg" width="560" height="250" rx="12"/>
<rect class="border" x="1" y="1" width="558" height="248" rx="12"/>

<text x="28" y="42" class="title">Development Activity</text>

<text x="28" y="98" class="big">{port_commits}</text>
<text x="28" y="122" class="label">port commits</text>

<text x="210" y="98" class="big">{attributed_fork_commits}</text>
<text x="210" y="122" class="label">GitHub-attributed in forks</text>

<text x="440" y="98" class="big">{original_commits}</text>
<text x="440" y="122" class="label">original-repo</text>

<line x1="28" y1="148" x2="532" y2="148" stroke="#30363d"/>

<text x="28" y="184" class="small">{port_count} active port repositories</text>
<text x="28" y="218" class="label">
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
    attributed_fork_commits,
):
    total_port_commits = sum(p["ahead"] for p in ports)

    rows = "\n".join(
        f"| **{p['label']}** | {p['ahead']} | {p['authored']} |"
        for p in sorted(
            ports,
            key=lambda x: x["ahead"],
            reverse=True,
        )
    )

    return f"""
<div align="center">
<img src="https://raw.githubusercontent.com/{USERNAME}/{USERNAME}/main/assets/development-activity.svg" width="560">
</div>

| Active Port | Port Commits | GitHub Attributed |
|:---|---:|---:|
{rows}
| **Total** | **{total_port_commits}** | **{attributed_fork_commits}** |

<sub>
Port commits are commits currently ahead of each repository's upstream.
GitHub Attributed counts commits GitHub directly associates with my account.
These metrics overlap and are not added together.
</sub>
""".strip()


def update_readme(markdown):
    text = README.read_text(encoding="utf-8")
    block = f"{START}\n{markdown}\n{END}"

    pattern = re.compile(
        re.escape(START) + r".*?" + re.escape(END),
        re.DOTALL,
    )

    if pattern.search(text):
        text = pattern.sub(block, text)
    else:
        text += f"\n\n# Development Activity\n\n{block}\n"

    README.write_text(text, encoding="utf-8")


def main():
    repos = paginate(
        f"https://api.github.com/users/{USERNAME}/repos"
        "?type=owner&sort=updated&direction=desc&per_page=100"
    )

    # Don't count the profile repo itself.
    repos = [
        repo for repo in repos
        if repo["name"].lower() != USERNAME.lower()
    ]

    original_repos = [
        repo for repo in repos
        if not repo.get("fork")
    ]

    fork_repos = [
        repo for repo in repos
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

        authored = count_authored_commits(repo)
        ahead = get_ahead_count(repo)

        ports.append({
            "label": PORT_LABELS[repo["name"]],
            "authored": authored,
            "ahead": ahead,
        })

        print(
            f"{PORT_LABELS[repo['name']]}: "
            f"{ahead} port commits, "
            f"{authored} GitHub-attributed"
        )

    attributed_fork_commits = sum(
        p["authored"] for p in ports
    )

    total_port_commits = sum(
        p["ahead"] for p in ports
    )

    generate_svg(
        original_commits,
        attributed_fork_commits,
        total_port_commits,
        len(ports),
    )

    update_readme(
        generate_markdown(
            ports,
            original_commits,
            attributed_fork_commits,
        )
    )

    print()
    print(f"Port commits: {total_port_commits}")
    print(f"GitHub-attributed fork commits: {attributed_fork_commits}")
    print(f"Original-repo commits: {original_commits}")
    print("Profile stats updated successfully.")


if __name__ == "__main__":
    main()
