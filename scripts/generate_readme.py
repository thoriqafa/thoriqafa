import os
import yaml

from google import genai

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

    client = genai.Client(api_key=api_key)
    prompt = build_prompt(config, github_profile, repositories)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[SYSTEM_PROMPT, prompt],
    )

    if not response.text:
        raise RuntimeError("AI tidak menghasilkan README.")

    return response.text.strip()

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
