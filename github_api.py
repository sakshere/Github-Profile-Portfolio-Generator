"""
GitHub API Client
Handles fetching and processing user data from the GitHub REST API.
"""

import requests
import os
from collections import defaultdict


from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

GITHUB_API_BASE = "https://api.github.com"

# Optional: set GITHUB_TOKEN env variable to avoid rate limiting
# You can also hardcode your token here for testing (uncomment and replace):
# GITHUB_TOKEN = "your_personal_access_token_here"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", None)


def _get_session():
    """Create a requests session with robust retry logic."""
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.headers.update({
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHubPortfolioGenerator/1.0"
    })
    if GITHUB_TOKEN:
        session.headers.update({"Authorization": f"token {GITHUB_TOKEN}"})
    return session


# Global session instance
api_session = _get_session()


def fetch_profile(username):
    """
    Fetch the GitHub user profile.
    Returns a dict with user info or raises an exception.
    """
    url = f"{GITHUB_API_BASE}/users/{username}"
    response = api_session.get(url, timeout=15)

    if response.status_code == 404:
        raise ValueError(f"GitHub user '{username}' not found.")
    if response.status_code == 403:
        raise ConnectionError("GitHub API rate limit exceeded. Try again later or set a GITHUB_TOKEN.")
    response.raise_for_status()

    data = response.json()
    return {
        "username": data.get("login", ""),
        "name": data.get("name") or data.get("login", ""),
        "avatar_url": data.get("avatar_url", ""),
        "bio": data.get("bio") or "A passionate developer.",
        "location": data.get("location") or "Earth",
        "company": data.get("company") or "",
        "blog": data.get("blog") or "",
        "twitter": data.get("twitter_username") or "",
        "public_repos": data.get("public_repos", 0),
        "followers": data.get("followers", 0),
        "following": data.get("following", 0),
        "created_at": data.get("created_at", ""),
        "html_url": data.get("html_url", ""),
    }


def fetch_repos(username, max_repos=100):
    """
    Fetch public repositories for the user.
    Returns a list of repo dicts sorted by stars (descending).
    """
    repos = []
    page = 1
    per_page = min(max_repos, 100)

    while len(repos) < max_repos:
        url = f"{GITHUB_API_BASE}/users/{username}/repos"
        params = {
            "type": "owner",
            "sort": "updated",
            "direction": "desc",
            "per_page": per_page,
            "page": page,
        }
        response = api_session.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()
        if not data:
            break

        for repo in data:
            if repo.get("fork"):
                continue  # Skip forked repos
            repos.append({
                "name": repo.get("name", ""),
                "description": repo.get("description") or "No description provided.",
                "html_url": repo.get("html_url", ""),
                "language": repo.get("language") or "Unknown",
                "stargazers_count": repo.get("stargazers_count", 0),
                "forks_count": repo.get("forks_count", 0),
                "topics": repo.get("topics", []),
                "updated_at": repo.get("updated_at", ""),
                "homepage": repo.get("homepage") or "",
            })

        page += 1
        if len(data) < per_page:
            break

    # Sort by stars descending
    repos.sort(key=lambda r: r["stargazers_count"], reverse=True)
    return repos


def fetch_languages(username, repos=None):
    """
    Aggregate language usage across all repos.
    Returns a dict of {language: percentage} sorted by usage.
    """
    if repos is None:
        repos = fetch_repos(username)

    language_bytes = defaultdict(int)

    for repo in repos[:30]:  # Limit API calls to top 30 repos
        url = f"{GITHUB_API_BASE}/repos/{username}/{repo['name']}/languages"
        try:
            response = api_session.get(url, timeout=10)
            response.raise_for_status()
            langs = response.json()
            for lang, byte_count in langs.items():
                language_bytes[lang] += byte_count
        except (requests.RequestException, ValueError):
            continue  # Skip repos where language fetch fails

    # Convert to percentages
    total_bytes = sum(language_bytes.values())
    if total_bytes == 0:
        return {}

    language_percentages = {}
    for lang, byte_count in sorted(language_bytes.items(), key=lambda x: x[1], reverse=True):
        percentage = round((byte_count / total_bytes) * 100, 1)
        if percentage >= 0.5:  # Only include languages with >= 0.5%
            language_percentages[lang] = percentage

    return language_percentages


def compute_stats(repos):
    """Compute aggregate statistics from repos."""
    total_stars = sum(r["stargazers_count"] for r in repos)
    total_forks = sum(r["forks_count"] for r in repos)
    return {
        "total_repos": len(repos),
        "total_stars": total_stars,
        "total_forks": total_forks,
    }


# Language color mapping for charts
LANGUAGE_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Java": "#b07219",
    "C++": "#f34b7d",
    "C": "#555555",
    "C#": "#178600",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Shell": "#89e051",
    "Lua": "#000080",
    "Scala": "#c22d40",
    "R": "#198CE7",
    "MATLAB": "#e16737",
    "Perl": "#0298c3",
    "Haskell": "#5e5086",
    "Elixir": "#6e4a7e",
    "Clojure": "#db5855",
    "Vue": "#41b883",
    "Jupyter Notebook": "#DA5B0B",
}


def get_language_color(language):
    """Get the color for a programming language, with a fallback."""
    return LANGUAGE_COLORS.get(language, "#858585")


def get_profile_insights(data):
    """
    Analyze profile and repo data to provide actionable insights.
    Returns a list of insight dictionaries.
    """
    profile = data.get("profile", {})
    repos = data.get("repos", [])
    languages = data.get("languages", [])
    stats = data.get("stats", {})

    insights = []

    # 1. Profile Completeness
    if not profile.get("bio") or profile.get("bio") == "A passionate developer.":
        insights.append({
            "type": "warning",
            "title": "Missing Bio",
            "message": "Your bio is empty or generic. A unique bio helps you stand out to recruiters and collaborators.",
            "icon": "user-plus"
        })
    
    if not profile.get("location") or profile.get("location") == "Earth":
        insights.append({
            "type": "info",
            "title": "Update Location",
            "message": "Specifying your location helps in finding local opportunities and networking.",
            "icon": "map-pin"
        })

    if not profile.get("company"):
        insights.append({
            "type": "info",
            "title": "Add Company",
            "message": "Adding your current company or 'Freelance' status adds professional credibility.",
            "icon": "briefcase"
        })

    # 2. Repository Health
    if stats.get("total_repos", 0) < 5:
        insights.append({
            "type": "warning",
            "title": "Expand Your Portfolio",
            "message": "You have fewer than 5 public repositories. Consider showcasing more of your side projects or experiments.",
            "icon": "folder-plus"
        })

    # 3. Technical Diversity
    if len(languages) < 3:
        insights.append({
            "type": "info",
            "title": "Broaden Your Skills",
            "message": "You primarily use 1-2 languages. Learning a new language or framework can expand your problem-solving toolkit.",
            "icon": "code"
        })

    # 4. Success Recognition
    if stats.get("total_stars", 0) > 10:
        insights.append({
            "type": "success",
            "title": "Rising Star",
            "message": f"Great job! You've earned {stats['total_stars']} stars across your repositories.",
            "icon": "star"
        })
    
    # 5. Summary Insight
    if len(insights) == 0:
        insights.append({
            "type": "success",
            "title": "Profile looking sharp!",
            "message": "Your GitHub profile is well-maintained and provides a great overview of your work.",
            "icon": "check-circle"
        })

    return insights


def process_data(username):
    """
    Main function: fetches and processes all GitHub data for a user.
    Returns a complete data dict ready for template rendering.
    """
    profile = fetch_profile(username)
    repos = fetch_repos(username)
    languages = fetch_languages(username, repos)
    stats = compute_stats(repos)

    # Build language data with colors for charts
    language_chart_data = []
    for lang, pct in languages.items():
        language_chart_data.append({
            "name": lang,
            "percentage": pct,
            "color": get_language_color(lang),
        })

    data = {
        "profile": profile,
        "repos": repos[:12],  # Top 12 repos for the portfolio
        "languages": language_chart_data,
        "stats": stats,
        "all_repos_count": len(repos),
    }

    # Add insights based on the processed data
    data["insights"] = get_profile_insights(data)

    return data
