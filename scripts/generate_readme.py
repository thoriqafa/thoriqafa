import os
import json
import subprocess

from google import genai


# =========================
# Gemini Client
# =========================

client = genai.Client(
    api_key=os.environ["API_KEY_AI"]
)


# =========================
# GitHub Username
# =========================

username = "thoriqafa"


# =========================
# Ambil daftar repository
# =========================

result = subprocess.run(
    [
        "gh",
        "repo",
        "list",
        username,
        "--limit",
        "100",
        "--json",
        "name,description,url,stargazerCount,forkCount,primaryLanguage,pushedAt,isArchived"
    ],
    capture_output=True,
    text=True,
    check=True
)

repositories = json.loads(result.stdout)


# =========================
# Buang repository archived
# =========================

repositories = [
    repo
    for repo in repositories
    if not repo["isArchived"]
]


# =========================
# Prompt AI
# =========================

prompt = f"""
You are an AI portfolio curator for a GitHub profile.

GitHub username:
{username}

Repository data:
{json.dumps(repositories, indent=2)}

Create a professional GitHub Profile README.

Your job is to decide what is actually worth displaying.

Consider:

- Most active projects
- Recently updated projects
- Most interesting projects
- Technologies used
- Stars and forks
- Project descriptions
- Overall technical focus
- Projects that best represent the developer

Do NOT invent:

- Projects
- Technologies
- Achievements
- Statistics
- Experience
- Skills

Only use information that exists in the provided GitHub data.

Create a polished Markdown README.

Include only sections that provide value.

Possible sections:

- Introduction
- Current focus
- Featured projects
- Tech stack
- GitHub activity
- What I'm building
- Contact

The README should feel like a professional developer portfolio,
not a generic template.

For featured projects, prioritize projects that are:
1. Recently active
2. Technically interesting
3. Representative of the developer
4. Have useful descriptions
5. Have stars/forks when available

Do not list every repository.

Return ONLY the Markdown content.
"""


# =========================
# Generate README dengan Gemini
# =========================

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)


# =========================
# Ambil hasil AI
# =========================

readme = response.text


# =========================
# Simpan README
# =========================

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)


print("README generated successfully.")