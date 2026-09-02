import os
import requests

GITHUB_USERNAME = "thoriqafa"
GITHUB_API = "https://api.github.com"

def github_headers():
    token = os.environ.get("GH_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def get_repositories():
    url = f"{GITHUB_API}/users/{GITHUB_USERNAME}/repos"
    params = {"per_page": 100, "sort": "updated", "direction": "desc"}
    response = requests.get(url, headers=github_headers(), params=params, timeout=30)
    response.raise_for_status()

    repositories = []
    for repo in response.json():
        if repo.get("fork"):
            continue
        repositories.append({
            "name": repo.get("name"),
            "description": repo.get("description"),
            "html_url": repo.get("html_url"),
            "language": repo.get("language"),
            "topics": repo.get("topics", []),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "updated_at": repo.get("updated_at"),
            "created_at": repo.get("created_at"),
            "archived": repo.get("archived", False),
        })
    return repositories

def get_profile():
    url = f"{GITHUB_API}/users/{GITHUB_USERNAME}"
    response = requests.get(url, headers=github_headers(), timeout=30)
    response.raise_for_status()
    data = response.json()
    return {
        "login": data.get("login"),
        "name": data.get("name"),
        "bio": data.get("bio"),
        "company": data.get("company"),
        "location": data.get("location"),
        "blog": data.get("blog"),
        "public_repos": data.get("public_repos"),
        "followers": data.get("followers"),
        "following": data.get("following"),
    }
