import os
import yaml

from openai import OpenAI

from github_data import get_profile, get_repositories
from prompts import SYSTEM_PROMPT, build_prompt

CONFIG_FILE = "config/profile.yml"
README_FILE = "README.md"

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def generate_ai_readme(config, github_profile, repositories):
    api_key = os.environ.get("API_KEY_AI")
    if not api_key:
        raise RuntimeError("API_KEY_AI belum tersedia.")

    base_url = os.environ.get("AI_BASE_URL", "https://router.thour.my.id/v1")
    model = os.environ.get("AI_MODEL", "myminebos")

    client = OpenAI(api_key=api_key, base_url=base_url)
    prompt = build_prompt(config, github_profile, repositories)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("AI tidak menghasilkan README.")

    return content.strip()

def clean_markdown(content):
    for prefix in ("```markdown", "```md", "```"):
        if content.startswith(prefix):
            content = content[len(prefix):]
            break
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()

def main():
    print("Loading profile configuration...")
    config = load_config()

    print("Fetching GitHub profile...")
    github_profile = get_profile()

    print("Fetching repositories...")
    repositories = get_repositories()
    print(f"Found {len(repositories)} repositories.")

    print("Generating README with AI...")
    readme = generate_ai_readme(config, github_profile, repositories)
    readme = clean_markdown(readme)

    with open(README_FILE, "w", encoding="utf-8") as file:
        file.write(readme + "\n")

    print("README successfully generated.")

if __name__ == "__main__":
    main()
