#!/usr/bin/env python3

import json
import os
import re
import urllib.request
import urllib.parse
from pathlib import Path

USERNAME = "NyerahMT"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

README = Path("README.md")
ASSETS = Path("assets")
ASSETS.mkdir(exist_ok=True)

# Repos we specifically want highlighted as ports.
PORT_LABELS = {
    "principia": "Principia iOS",
    "engine-sim-ios": "Engine Simulator iOS",
    "fluid-engine-swift": "Fluid Engine Swift",
}

START = "<!-- AUTO-STATS:START -->"
END = "<!-- AUTO-STATS:END -->"


def api(url):
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": f"{USERNAME}-profile-stats",
        },
    )

    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        link = response.headers.get("Link")
        return data, link


def paginate(url):
    results = []

    while url:
        data, link = api(url)

        if isinstance(data, list):
            results.extend(data)
        else:
            return data

        next_url = None

        if link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    next_url = part.split("<", 1)[1].split(">", 1)[0]
                    break

        url = next_url

    return results


def count_authored_commits(repo):
    branch = urllib.parse.quote(repo["default_branch"], safe="")

    url = (
        f"https://api.github.com/repos/{repo['full_name']}/commits"
        f"?author={USERNAME}&sha={branch}&per_page=100"
    )

    try:
        commits = paginate(url)
        return len(commits)
    except Exception as e:
        print(f"Could not count commits for {repo['full_name']}: {e}")
        return 0


def get_ahead_count(repo):
    """
    Compare the fork's default branch against the immediate parent repo.
    """

    if not repo.get("fork"):
        return 0

    try:
        details, _ = api(
            f"https://api.github.com/repos/{repo['full_name']}"
        )

        parent = details.get("parent")

        if not parent:
            return 0

        parent_branch = parent["default_branch"]
        fork_branch = repo["default_branch"]

        base = urllib.parse.quote(parent_branch, safe="")
        head = urllib.parse.quote(
            f"{USERNAME}:{fork_branch}",
            safe=":",
        )

        comparison, _ = api(
            f"https://api.github.com/repos/"
            f"{parent['full_name']}/compare/{base}...{head}"
        )

        return comparison.get("ahead_by", 0)

    except Exception as e:
        print(f"Could not compare {repo['full_name']}: {e}")
        return 0


def esc(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def generate_svg(normal_commits, fork_commits, normal_repos, fork_repos):
    total = normal_commits + fork_commits

    svg = f"""
<svg width="520" height="250" viewBox="0 0 520 250"
     xmlns="http://www.w3.org/2000/svg">

<style>
    .bg {{ fill: #0d1117; }}
    .border {{ fill: none; stroke: #30363d; stroke-width: 2; }}
    .title {{ fill: #f0f6fc; font: 600 22px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; }}
    .big {{ fill: #58a6ff; font: 700 32px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; }}
    .label {{ fill: #8b949e; font: 14px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; }}
    .small {{ fill: #c9d1d9; font: 13px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; }}
</style>

<rect class="bg" width="520" height="250" rx="12"/>
<rect class="border" x="1" y="1" width="518" height="248" rx="12"/>

<text x="28" y="42" class="title">Development Activity</text>

<text x="28" y="94" class="big">{normal_commits}</text>
<text x="28" y="118" class="label">normal commits</text>

<text x="195" y="94" class="big">{fork_commits}</text>
<text x="195" y="118" class="label">fork / port commits</text>

<text x="390" y="94" class="big">{total}</text>
<text x="390" y="118" class="label">total authored</text>

<line x1="28" y1="145" x2="492" y2="145"
      stroke="#30363d" stroke-width="1"/>

<text x="28" y="180" class="small">
{normal_repos} original repositories
</text>

<text x="270" y="180" class="small">
{fork_repos} fork repositories
</text>

<text x="28" y="218" class="label">
Calculated directly from GitHub repository history
</text>

</svg>
"""

    (ASSETS / "development-activity.svg").write_text(svg.strip())


def generate_markdown(port_data, normal_commits, fork_commits):
    total = normal_commits + fork_commits

    rows = []

    for item in sorted(
        port_data,
        key=lambda x: x["commits"],
        reverse=True,
    ):
        rows.append(
            f"| **{item['label']}** | "
            f"{item['commits']} | "
            f"{item['ahead']} |"
        )

    table = "\n".join(rows)

    return f"""
<div align="center">

<img src="https://raw.githubusercontent.com/{USERNAME}/{USERNAME}/main/assets/development-activity.svg" width="520">

</div>

<br>

| Active Port | Authored Commits | Ahead of Upstream |
|:---|---:|---:|
{table}

<div align="center">

**{normal_commits}** original-repo commits · **{fork_commits}** fork/port commits · **{total}** total authored commits

<sub>
Commit totals are calculated directly from the default branches of repositories owned by {USERNAME}.
"Ahead of upstream" shows the current divergence of each port from its parent repository.
</sub>

</div>
""".strip()


def update_readme(markdown):
    text = README.read_text()

    block = f"{START}\n{markdown}\n{END}"

    pattern = re.compile(
        re.escape(START) + r".*?" + re.escape(END),
        re.DOTALL,
    )

    if pattern.search(text):
        text = pattern.sub(block, text)
    else:
        text += f"\n\n---\n\n# Development Activity\n\n{block}\n"

    README.write_text(text)


def main():
    repos = paginate(
        "https://api.github.com/user/repos"
        "?affiliation=owner"
        "&visibility=public"
        "&per_page=100"
    )

    # Ignore the profile repository itself so automatic README commits
    # don't inflate the "normal development" number.
    repos = [
        repo
        for repo in repos
        if repo["name"].lower() != USERNAME.lower()
    ]

    normal_repos = [
        repo for repo in repos
        if not repo.get("fork")
    ]

    fork_repos = [
        repo for repo in repos
        if repo.get("fork")
    ]

    normal_commits = sum(
        count_authored_commits(repo)
        for repo in normal_repos
    )

    fork_commits = sum(
        count_authored_commits(repo)
        for repo in fork_repos
    )

    port_data = []

    for repo in fork_repos:
        if repo["name"] not in PORT_LABELS:
            continue

        port_data.append(
            {
                "label": PORT_LABELS[repo["name"]],
                "commits": count_authored_commits(repo),
                "ahead": get_ahead_count(repo),
            }
        )

    generate_svg(
        normal_commits,
        fork_commits,
        len(normal_repos),
        len(fork_repos),
    )

    markdown = generate_markdown(
        port_data,
        normal_commits,
        fork_commits,
    )

    update_readme(markdown)

    print(
        f"Normal commits: {normal_commits}\n"
        f"Fork commits: {fork_commits}\n"
        f"Total: {normal_commits + fork_commits}"
    )


if __name__ == "__main__":
    main()
