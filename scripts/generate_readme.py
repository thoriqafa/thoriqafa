import os
import json
import subprocess
from pathlib import Path

from openai import OpenAI


# =========================
# AI Router Client
# =========================

client = OpenAI(
    api_key=os.environ["API_KEY_AI"],
    base_url=os.environ.get("AI_BASE_URL", "https://router.thour.my.id/v1"),
)
model = os.environ.get("AI_MODEL", "gemini-2.5-flash")


# =========================
# GitHub Username
# =========================

username = "thoriqafa"
template_path = Path("README_TEMPLATE.md")


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
# Ambil template acuan
# =========================

readme_template = template_path.read_text(encoding="utf-8")


# =========================
# Prompt AI
# =========================

prompt = f"""
You are an AI portfolio curator for a GitHub profile.

GitHub username:
{username}

Repository data:
{json.dumps(repositories, indent=2)}

Reference template:
```markdown
{readme_template}
```

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

For repository/project sections, only use information that exists in the provided GitHub data.
For personal profile text, badges, links, headings, and visual layout, preserve the owner-provided reference template unless it conflicts with the repository data.

Create a polished Markdown README.

Use the reference template as the main structure and style guide.
You may rename, remove, or repeat sections when the repository data makes it necessary.
Replace placeholders only when the needed information exists in the repository data or the reference template.
Keep owner-provided static profile content from the template.

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
# Generate README dengan AI Router
# =========================

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
)


# =========================
# Ambil hasil AI
# =========================

readme = response.choices[0].message.content


# =========================
# Simpan README
# =========================

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)


print("README generated successfully.")
