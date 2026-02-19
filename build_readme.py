#!/usr/bin/env python3
"""
Self-updating GitHub Profile README generator.
Fetches all repos via GitHub API, categorizes MVPs, and generates README.md.

Usage:
    python build_readme.py
    # or with auth for higher rate limits:
    GITHUB_TOKEN=ghp_xxx python build_readme.py
"""

import os
import re
import json
import requests
from datetime import datetime, timezone

USERNAME = "malikmuhammadsaadshafiq-dev"
API_BASE = "https://api.github.com"

# ─── Featured Products (curated) ───────────────────────────────────────────────

FEATURED = [
    {
        "name": "AI-Surrrogate-2.0",
        "desc": "Your AI twin \u2014 a humanoid MCP-based clone for meetings and conversations",
        "tag": "AI Agent",
    },
    {
        "name": "mvp-meetingcontext",
        "desc": "Auto-generates meeting briefings by analyzing attendees' LinkedIn & company news",
        "tag": "SaaS",
    },
    {
        "name": "mvp-humancheck",
        "desc": "Browser extension that highlights AI-generated text and surfaces authentic human discussions",
        "tag": "Chrome Extension",
    },
    {
        "name": "mvp-splitsnap",
        "desc": "OCR-powered receipt scanner that instantly calculates fair bill splits with tax & tip",
        "tag": "Mobile App",
    },
    {
        "name": "mvp-subredditscout",
        "desc": "Find high-intent Reddit threads for authentic brand engagement before they trend",
        "tag": "SaaS",
    },
    {
        "name": "mvp-schemaflow",
        "desc": "Interactive JSON-to-TypeScript visualizer with editable node diagrams",
        "tag": "Web App",
    },
]

# Known MVP repos that don't start with "mvp-"
KNOWN_MVP_REPOS = {"AI-Surrrogate-2.0"}

# Repos to skip entirely
SKIP_REPOS = {USERNAME}  # the profile repo itself

# Category tag patterns
TAG_PATTERNS = {
    "SaaS": re.compile(r"\[SaaS\]", re.IGNORECASE),
    "Chrome Extension": re.compile(r"\[Chrome Extension\]", re.IGNORECASE),
    "Mobile App": re.compile(r"\[Mobile App\]", re.IGNORECASE),
    "Web App": re.compile(r"\[Web App\]", re.IGNORECASE),
    "CLI Tool": re.compile(r"\[CLI\]", re.IGNORECASE),
    "API": re.compile(r"\[API\]", re.IGNORECASE),
}


def get_headers():
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_all_repos():
    """Fetch all public repos with pagination."""
    repos = []
    page = 1
    headers = get_headers()
    while True:
        url = f"{API_BASE}/users/{USERNAME}/repos?per_page=100&page={page}&type=public"
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    return repos


def is_mvp_repo(repo):
    """Check if a repo is an MVP product."""
    name = repo["name"]
    if name in SKIP_REPOS:
        return False
    if repo.get("fork", False):
        return False
    if name.startswith("mvp-"):
        return True
    if name in KNOWN_MVP_REPOS:
        return True
    return False


def extract_tag(description):
    """Extract [Tag] from description, return (tag, clean_description)."""
    if not description:
        return None, ""
    for tag_name, pattern in TAG_PATTERNS.items():
        match = pattern.search(description)
        if match:
            clean = pattern.sub("", description).strip().lstrip("- ").strip()
            return tag_name, clean
    return None, description


def categorize_repos(repos):
    """Categorize MVP repos by type."""
    categories = {
        "SaaS": [],
        "Chrome Extension": [],
        "Mobile App": [],
        "Web App": [],
        "CLI Tool": [],
        "API": [],
        "Other": [],
    }

    mvp_repos = []
    for repo in repos:
        if not is_mvp_repo(repo):
            continue
        mvp_repos.append(repo)
        desc = repo.get("description") or ""
        tag, clean_desc = extract_tag(desc)
        repo["_tag"] = tag or "Other"
        repo["_clean_desc"] = clean_desc or desc or "No description"
        if tag and tag in categories:
            categories[tag].append(repo)
        else:
            categories["Other"].append(repo)

    # Sort each category alphabetically
    for cat in categories:
        categories[cat].sort(key=lambda r: r["name"].lower())

    return categories, mvp_repos


def get_latest_ships(mvp_repos, count=6):
    """Get the N most recently created MVP repos."""
    sorted_repos = sorted(
        mvp_repos,
        key=lambda r: r.get("created_at", ""),
        reverse=True,
    )
    return sorted_repos[:count]


def build_readme(repos):
    """Generate the complete README.md content."""
    total_repo_count = len(repos)
    categories, mvp_repos = categorize_repos(repos)
    total_mvp_count = len(mvp_repos)
    latest_ships = get_latest_ships(mvp_repos, 6)

    saas_count = len(categories["SaaS"])
    ext_count = len(categories["Chrome Extension"])
    mobile_count = len(categories["Mobile App"])
    web_count = len(categories["Web App"])
    cli_count = len(categories["CLI Tool"])
    api_count = len(categories["API"])
    other_count = len(categories["Other"])

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = []

    REPO_URL = f"https://github.com/{USERNAME}/{USERNAME}"

    # ── Section 1: Animated Header ──
    lines.append('<div align="center">\n')
    lines.append(f'<img src="{REPO_URL}/raw/main/assets/header.svg" width="800" alt="Saad Shafiq - MVP Factory" />\n')
    lines.append(f"**{total_mvp_count}+ products shipped.** Most of them before lunch.\n")
    lines.append("</div>\n")

    # ── Divider ──
    lines.append(f'<img src="{REPO_URL}/raw/main/assets/divider.svg" width="800" />\n')

    # ── Section 2: Live Activity Indicator ──
    lines.append('<div align="center">\n')
    lines.append(f'<img src="{REPO_URL}/raw/main/assets/activity.svg" width="800" alt="Pipeline Active — Researching + Building 24/7" />\n')
    lines.append("</div>\n")

    # ── Section 3: Stats Dashboard ──
    lines.append('<div align="center">\n')
    lines.append(f'<img src="{REPO_URL}/raw/main/assets/stats.svg" width="800" alt="{total_mvp_count}+ Products | 220+ Posts/Cycle | 87% Rejected | 5 AI Agents | 30m Cycles" />\n')
    lines.append("</div>\n")

    # ── Section 4: Stats Badges ──
    lines.append('<div align="center">\n')
    lines.append(
        f"![Products Shipped](https://img.shields.io/badge/Products_Shipped-{total_mvp_count}+-2563eb?style=for-the-badge&labelColor=1e1e2e)"
    )
    lines.append(
        f"&nbsp;&nbsp;\n"
        f"![SaaS](https://img.shields.io/badge/SaaS-{saas_count}-0ea5e9?style=flat-square)\n"
        f"![Extensions](https://img.shields.io/badge/Extensions-{ext_count}-f59e0b?style=flat-square)\n"
        f"![Mobile](https://img.shields.io/badge/Mobile-{mobile_count}-10b981?style=flat-square)\n"
        f"![Web Apps](https://img.shields.io/badge/Web_Apps-{web_count}-8b5cf6?style=flat-square)\n"
    )
    lines.append("</div>\n")

    # ── Divider ──
    lines.append(f'<img src="{REPO_URL}/raw/main/assets/divider.svg" width="800" />\n')

    # ── Section 4: Latest Ships ──
    lines.append("### Latest Ships\n")
    lines.append("| Product | Type | What It Does |")
    lines.append("|---------|------|-------------|")
    for repo in latest_ships:
        name = repo["name"]
        tag = repo["_tag"]
        desc = repo["_clean_desc"]
        # Truncate long descriptions
        if len(desc) > 100:
            desc = desc[:97] + "..."
        url = f"https://github.com/{USERNAME}/{name}"
        lines.append(f"| [**{name}**]({url}) | `{tag}` | {desc} |")
    lines.append("")
    lines.append(f"<sub>Auto-updated from GitHub API. Last refresh: {now_utc}</sub>\n")

    # ── Divider ──
    lines.append(f'<img src="{REPO_URL}/raw/main/assets/divider.svg" width="800" />\n')

    # ── Section 5.5: AI Squadron ──
    lines.append('<div align="center">\n')
    lines.append('<h3>AI Squadron</h3>\n')
    lines.append(f'<img src="{REPO_URL}/raw/main/assets/agents.svg" width="800" alt="AI Squadron — 5 agents collaborating: PM, Research, Validation, Frontend, Backend" />\n')
    lines.append(f'<br/>\n')
    lines.append(f'<img src="{REPO_URL}/raw/main/assets/pipeline.svg" width="800" alt="Decoupled Pipeline: Loop 1 Research+Validate every 30m | Loop 2 Build+Deploy every 20m" />\n')
    lines.append("</div>\n")

    # ── Divider ──
    lines.append(f'<img src="{REPO_URL}/raw/main/assets/divider.svg" width="800" />\n')

    # ── Section 5.6: Tech Stack ──
    lines.append('<div align="center">\n')
    lines.append('<h3>Tech Stack</h3>\n')
    lines.append(f'<img src="{REPO_URL}/raw/main/assets/tech-stack.svg" width="800" alt="Languages: TypeScript 95%, JavaScript 88%, Python 72%, Solidity 60% | Frameworks: React, Next.js, Node.js, Tailwind, Claude Code, Kimi K2.5" />\n')
    lines.append("</div>\n")

    # ── Divider ──
    lines.append(f'<img src="{REPO_URL}/raw/main/assets/divider.svg" width="800" />\n')

    # ── Section 5.7: GitHub Stats ──
    lines.append('<div align="center">\n')
    lines.append('<h3>GitHub Stats</h3>\n')
    lines.append(f'<a href="https://github.com/{USERNAME}">\n')
    lines.append(f'<img src="https://github-readme-streak-stats.herokuapp.com?user={USERNAME}&theme=github-dark-blue&hide_border=true&background=0D1117&ring=7c3aed&fire=ec4899&currStreakLabel=c9d1d9&sideLabels=8b949e&dates=6e7681" width="49%" alt="GitHub Streak" />\n')
    lines.append("</a>\n")
    lines.append(f'<a href="https://github.com/{USERNAME}">\n')
    lines.append(f'<img src="https://github-readme-stats.vercel.app/api/top-langs/?username={USERNAME}&layout=compact&theme=github_dark&hide_border=true&bg_color=0D1117&title_color=7c3aed&text_color=c9d1d9&langs_count=8" width="38%" alt="Top Languages" />\n')
    lines.append("</a>\n")
    lines.append("</div>\n")

    # ── Divider ──
    lines.append(f'<img src="{REPO_URL}/raw/main/assets/divider.svg" width="800" />\n')

    # ── Section 5: Featured Products ──
    lines.append("### Featured\n")
    lines.append("| | |")
    lines.append("|:--|:--|")
    # Pair them up in 2-column grid
    for i in range(0, len(FEATURED), 2):
        left = FEATURED[i]
        right = FEATURED[i + 1] if i + 1 < len(FEATURED) else None

        left_link = f"[**{left['name']}**](https://github.com/{USERNAME}/{left['name']})"
        left_desc = left["desc"]
        left_tag = f"`{left['tag']}`"

        if right:
            right_link = f"[**{right['name']}**](https://github.com/{USERNAME}/{right['name']})"
            right_desc = right["desc"]
            right_tag = f"`{right['tag']}`"
        else:
            right_link = ""
            right_desc = ""
            right_tag = ""

        lines.append(f"| {left_link} | {right_link} |")
        lines.append(f"| {left_desc} | {right_desc} |")
        lines.append(f"| {left_tag} | {right_tag} |")

    lines.append("")

    # ── Section 6: Full Catalog (collapsible) ──
    lines.append(
        f"<details>\n<summary><strong>Full Product Catalog ({total_mvp_count} products)</strong></summary>\n<br>\n"
    )

    catalog_order = [
        ("SaaS", saas_count),
        ("Chrome Extension", ext_count),
        ("Mobile App", mobile_count),
        ("Web App", web_count),
        ("CLI Tool", cli_count),
        ("API", api_count),
        ("Other", other_count),
    ]

    for cat_name, count in catalog_order:
        cat_repos = categories[cat_name]
        if not cat_repos:
            continue
        # Pluralize category names for headers
        header_names = {
            "SaaS": "SaaS",
            "Chrome Extension": "Chrome Extensions",
            "Mobile App": "Mobile Apps",
            "Web App": "Web Apps",
            "CLI Tool": "CLI Tools",
            "API": "APIs",
            "Other": "Other",
        }
        header = header_names.get(cat_name, cat_name)
        lines.append(f"**{header}** ({count})\n")
        for repo in cat_repos:
            name = repo["name"]
            desc = repo["_clean_desc"]
            url = f"https://github.com/{USERNAME}/{name}"
            lines.append(f"- [{name}]({url}) \u2014 {desc}")
        lines.append("")

    lines.append("</details>\n")

    # ── Section 8: Activity Graph ──
    lines.append('<div align="center">\n')
    lines.append(f'<a href="https://github.com/{USERNAME}">\n')
    lines.append(f'<img src="https://github-readme-activity-graph.vercel.app/graph?username={USERNAME}&theme=github-dark&hide_border=true&bg_color=0D1117&color=c9d1d9&line=7c3aed&point=ec4899&area=true&area_color=7c3aed" width="98%" alt="Contribution Graph" />\n')
    lines.append("</a>\n")
    lines.append("</div>\n")

    # ── Section 9: Tech Badges ──
    lines.append('<div align="center">\n')
    lines.append(
        "![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)\n"
        "![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)\n"
        "![Next.js](https://img.shields.io/badge/Next.js-000?style=flat-square&logo=next.js&logoColor=white)\n"
        "![Node.js](https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=node.js&logoColor=white)\n"
        "![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)\n"
        "![TailwindCSS](https://img.shields.io/badge/Tailwind-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)\n"
        "![Claude](https://img.shields.io/badge/Claude_Code-191919?style=flat-square&logo=anthropic&logoColor=white)\n"
        "![Vercel](https://img.shields.io/badge/Vercel-000?style=flat-square&logo=vercel&logoColor=white)\n"
        "![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)\n"
        "![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)\n"
    )
    lines.append("</div>\n")

    # ── Section 10: Animated Footer ──
    lines.append('<div align="center">\n')
    lines.append(f'<img src="{REPO_URL}/raw/main/assets/footer.svg" width="800" alt="Why ship one product when you can ship a hundred?" />\n')
    lines.append("</div>\n")

    return "\n".join(lines)


def main():
    print(f"Fetching repos for {USERNAME}...")
    repos = fetch_all_repos()
    print(f"Found {len(repos)} total public repos")

    readme = build_readme(repos)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    # Print summary
    mvp_count = sum(1 for r in repos if is_mvp_repo(r))
    print(f"MVP repos: {mvp_count}")
    print(f"README.md generated ({len(readme)} bytes)")


if __name__ == "__main__":
    main()
