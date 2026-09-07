import os
import re
import yaml

from openai import OpenAI

from github_data import get_profile, get_repositories
from prompts import SYSTEM_PROMPT, build_prompt


CONFIG_FILE = "config/profile.yml"
README_FILE = "README.md"


# ============================================================
# CONFIG
# ============================================================

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


# ============================================================
# AI
# ============================================================

def get_ai_client():
    api_key = os.environ.get("API_KEY_AI")

    if not api_key:
        raise RuntimeError("API_KEY_AI belum tersedia.")

    base_url = os.environ.get(
        "AI_BASE_URL",
        "https://router.thour.my.id/v1"
    )

    return OpenAI(
        api_key=api_key,
        base_url=base_url,
    )


def generate_section(
    client,
    section,
    current_content,
    config,
    github_profile,
    repositories,
):
    model = os.environ.get(
        "AI_MODEL",
        "myminebos"
    )

    prompt = build_prompt(
        section=section,
        current_content=current_content,
        profile_config=config,
        github_profile=github_profile,
        repositories=repositories,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            f"AI tidak menghasilkan content untuk section {section}."
        )

    return clean_markdown(content)


# ============================================================
# MARKDOWN
# ============================================================

def clean_markdown(content):
    """
    Membersihkan code fence jika AI tetap mengembalikannya.
    """

    content = content.strip()

    patterns = (
        "```markdown",
        "```md",
        "```",
    )

    for prefix in patterns:
        if content.startswith(prefix):
            content = content[len(prefix):].strip()
            break

    if content.endswith("```"):
        content = content[:-3].strip()

    return content


def get_section(readme, section):
    """
    Mengambil isi di antara:

    <!-- AUTO:SECTION:START -->
    ...
    <!-- AUTO:SECTION:END -->
    """

    start_marker = f"<!-- AUTO:{section}:START -->"
    end_marker = f"<!-- AUTO:{section}:END -->"

    pattern = (
        re.escape(start_marker)
        + r"(.*?)"
        + re.escape(end_marker)
    )

    match = re.search(
        pattern,
        readme,
        re.DOTALL,
    )

    if not match:
        print(
            f"Section AUTO:{section} belum ada di README; menggunakan content kosong."
        )
        return ""

    return match.group(1).strip()


def update_section(readme, section, new_content):
    """
    Mengganti HANYA isi section tertentu.
    """

    start_marker = f"<!-- AUTO:{section}:START -->"
    end_marker = f"<!-- AUTO:{section}:END -->"

    pattern = (
        re.escape(start_marker)
        + r".*?"
        + re.escape(end_marker)
    )

    replacement = (
        f"{start_marker}\n"
        f"{new_content.strip()}\n"
        f"{end_marker}"
    )

    updated_readme, count = re.subn(
        pattern,
        replacement,
        readme,
        count=1,
        flags=re.DOTALL,
    )

    if count == 0:
        separator = "\n\n" if readme.strip() else ""
        return (
            readme.rstrip()
            + separator
            + f"{start_marker}\n"
            + f"{new_content.strip()}\n"
            + f"{end_marker}\n"
        )

    return updated_readme


# ============================================================
# README UPDATE
# ============================================================

def load_readme():
    if not os.path.exists(README_FILE):
        raise RuntimeError(
            f"{README_FILE} tidak ditemukan."
        )

    with open(
        README_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


def save_readme(content):
    with open(
        README_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(content.rstrip() + "\n")


# ============================================================
# MAIN
# ============================================================

def main():

    print("Loading profile configuration...")
    config = load_config()

    print("Loading existing README...")
    readme = load_readme()

    print("Fetching GitHub profile...")
    github_profile = get_profile()

    print("Fetching repositories...")
    repositories = get_repositories()

    print(
        f"Found {len(repositories)} repositories."
    )

    client = get_ai_client()

    # Section yang boleh diperbarui AI.
    sections = [
        "ABOUT",
        "TECHSTACK",
        "PROJECTS",
    ]

    updated_readme = readme

    for section in sections:

        print(
            f"Updating AUTO:{section}..."
        )

        current_content = get_section(
            updated_readme,
            section,
        )

        new_content = generate_section(
            client=client,
            section=section,
            current_content=current_content,
            config=config,
            github_profile=github_profile,
            repositories=repositories,
        )

        updated_readme = update_section(
            updated_readme,
            section,
            new_content,
        )

    save_readme(updated_readme)

    print("README data successfully updated.")


if __name__ == "__main__":
    main()
