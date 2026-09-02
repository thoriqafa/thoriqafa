import os
import json
import subprocess
from openai import OpenAI

client = OpenAI(api_key=os.environ["API_KEY_AI"])

username = "thoriqafa"

# Ambil daftar repository dari GitHub CLI
result = subprocess.run(
    [
        "gh", "repo", "list", username,
        "--limit", "100",
        "--json",
        "name,description,url,stargazerCount,forkCount,primaryLanguage,pushedAt,isArchived"
    ],
    capture_output=True,
    text=True,
    check=True
)

repositories = json.loads(result.stdout)

# Buang repository yang diarsipkan
repositories = [
    repo for repo in repositories
    if not repo["isArchived"]
]

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

Do NOT invent projects, technologies, achievements,
statistics, or experience.

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

Return ONLY the Markdown content.
"""

response = client.responses.create(
    model="gpt-5",
    input=prompt
)

readme = response.output_text

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

print("README generated successfully.")