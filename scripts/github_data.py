import os
import requests
from datetime import datetime, timedelta, timezone

GITHUB_USERNAME = "thoriqafa"
GITHUB_API = "https://api.github.com"
GITHUB_GRAPHQL = "https://api.github.com/graphql"

def github_headers():
    token = os.environ.get("GH_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def github_graphql_headers():
    token = os.environ.get("GH_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    return headers

def graphql_query(query, variables=None):
    response = requests.post(
        GITHUB_GRAPHQL,
        headers=github_graphql_headers(),
        json={"query": query, "variables": variables or {}},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]

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

def get_contribution_data():
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
        user(login: $username) {
            contributionsCollection(from: $from, to: $to) {
                contributionCalendar {
                    totalContributions
                    weeks {
                        contributionDays {
                            date
                            contributionCount
                            color
                        }
                    }
                }
                totalCommitContributions
                totalPullRequestContributions
                totalIssueContributions
                totalPullRequestReviewContributions
                totalRepositoriesWithContributedCommits
            }
        }
    }
    """
    now = datetime.now(timezone.utc)
    to_date = now.replace(hour=23, minute=59, second=59).isoformat() + "Z"
    from_date = (now - timedelta(days=365)).replace(hour=0, minute=0, second=0).isoformat() + "Z"

    variables = {
        "username": GITHUB_USERNAME,
        "from": from_date,
        "to": to_date,
    }

    data = graphql_query(query, variables)
    user = data.get("user")
    if not user:
        return None

    cc = user.get("contributionsCollection", {})
    calendar = cc.get("contributionCalendar", {})
    weeks = calendar.get("weeks", [])

    days = []
    for week in weeks:
        for day in week.get("contributionDays", []):
            days.append({
                "date": day["date"],
                "count": day["contributionCount"],
                "color": day["color"],
            })

    return {
        "total_contributions": calendar.get("totalContributions", 0),
        "total_commits": cc.get("totalCommitContributions", 0),
        "total_prs": cc.get("totalPullRequestContributions", 0),
        "total_issues": cc.get("totalIssueContributions", 0),
        "total_pr_reviews": cc.get("totalPullRequestReviewContributions", 0),
        "repos_contributed": cc.get("totalRepositoriesWithContributedCommits", 0),
        "days": days,
    }

def calculate_streaks(days):
    if not days:
        return {"current": 0, "longest": 0}

    days_sorted = sorted(days, key=lambda d: d["date"])
    date_to_count = {d["date"]: d["count"] for d in days_sorted}

    today = datetime.now(timezone.utc).date()
    current_streak = 0
    check_date = today

    while True:
        date_str = check_date.isoformat()
        if date_to_count.get(date_str, 0) > 0:
            current_streak += 1
            check_date -= timedelta(days=1)
        else:
            if check_date == today and date_to_count.get(date_str, 0) == 0:
                break
            check_date -= timedelta(days=1)
            if check_date < today - timedelta(days=365):
                break

    longest_streak = 0
    temp_streak = 0

    for d in days_sorted:
        if d["count"] > 0:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0

    return {"current": current_streak, "longest": longest_streak}

def get_stats_data():
    profile = get_profile()
    repos = get_repositories()
    contributions = get_contribution_data()

    total_stars = sum(r["stars"] for r in repos)
    total_forks = sum(r["forks"] for r in repos)

    streaks = {"current": 0, "longest": 0}
    if contributions and contributions.get("days"):
        streaks = calculate_streaks(contributions["days"])

    return {
        "username": GITHUB_USERNAME,
        "total_repos": len(repos),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "followers": profile.get("followers", 0),
        "following": profile.get("following", 0),
        "total_contributions": contributions.get("total_contributions", 0) if contributions else 0,
        "total_commits": contributions.get("total_commits", 0) if contributions else 0,
        "total_prs": contributions.get("total_prs", 0) if contributions else 0,
        "total_issues": contributions.get("total_issues", 0) if contributions else 0,
        "current_streak": streaks["current"],
        "longest_streak": streaks["longest"],
        "contribution_days": contributions.get("days", []) if contributions else [],
    }
