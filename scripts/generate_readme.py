import os
import re
import time
import yaml

from openai import OpenAI

from badges import build_badge_groups, render_badge_groups, validate_badge_content
from github_data import GITHUB_USERNAME, get_profile, get_repositories
from prompts import SYSTEM_PROMPT, build_prompt


CONFIG_FILE = "config/profile.yml"
README_FILE = "README.md"
AI_RETRY_COUNT = 3

# Section yang diisi AI.
AI_SECTIONS = ("ABOUT", "TECHSTACK", "PROJECTS")

# Section yang di-generate dari file SVG (bukan AI).
SVG_SECTIONS = ("STATS", "STREAK", "ACTIVITY")


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


def extract_ai_content(response, section):
    if not response.choices:
        raise RuntimeError(
            f"AI tidak mengembalikan choices untuk section {section}. "
            f"Response: {response}"
        )

    message = response.choices[0].message

    if not message or not message.content:
        raise RuntimeError(
            f"AI tidak menghasilkan content untuk section {section}. "
            f"Response: {response}"
        )

    return message.content


def generate_section(
    client,
    section,
    current_content,
    config,
    github_profile,
    repositories,
    verified_badges=None,
    max_featured_projects=None,
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
        verified_badges=verified_badges,
        max_featured_projects=max_featured_projects,
    )

    last_error = None

    for attempt in range(1, AI_RETRY_COUNT + 1):
        try:
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

            content = extract_ai_content(response, section)
            return clean_markdown(content)

        except Exception as error:
            last_error = error

            if attempt == AI_RETRY_COUNT:
                break

            print(
                f"AI gagal membuat AUTO:{section} "
                f"(percobaan {attempt}/{AI_RETRY_COUNT}). Mencoba lagi..."
            )
            time.sleep(attempt * 2)

    raise RuntimeError(
        f"AI gagal membuat content untuk section {section} "
        f"setelah {AI_RETRY_COUNT} percobaan."
    ) from last_error


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


def centered_image(src, alt, width=495):
    return (
        '<p align="center">\n'
        f'  <img src="{src}" alt="{alt}" width="{width}"/>\n'
        '</p>'
    )


def generate_stats_section():
    return centered_image("assets/github-stats.svg", "GitHub Statistics")


def generate_streak_section():
    return (
        '<p align="center">\n'
        '  <img\n'
        f'    src="https://streak-stats.demolab.com/?user={GITHUB_USERNAME}'
        '&theme=tokyonight"\n'
        '    alt="GitHub Contribution Streak"\n'
        '    width="495"\n'
        '  />\n'
        '</p>'
    )


def generate_activity_section():
    return centered_image(
        "assets/github-activity.svg",
        "GitHub Contribution Activity",
    )


SECTION_GENERATORS = {
    "STATS": generate_stats_section,
    "STREAK": generate_streak_section,
    "ACTIVITY": generate_activity_section,
}


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

    readme_config = config.get("readme") or {}
    max_featured_projects = readme_config.get("max_featured_projects")

    print("Loading existing README...")
    readme = load_readme()

    print("Fetching GitHub profile...")
    github_profile = get_profile()

    print("Fetching repositories...")
    repositories = get_repositories()

    print(
        f"Found {len(repositories)} repositories."
    )

    print("Building tech stack badges...")
    badge_groups = build_badge_groups(config, repositories)
    verified_badges = render_badge_groups(badge_groups)
    print(
        f"Prepared {len(badge_groups)} badge groups "
        f"({sum(len(g['badges']) for g in badge_groups)} badges)."
    )

    client = get_ai_client()

    updated_readme = readme

    for section in AI_SECTIONS:

        print(
            f"Updating AUTO:{section}..."
        )

        current_content = get_section(
            updated_readme,
            section,
        )

        if section == "TECHSTACK" and not badge_groups:
            print(
                "Tidak ada badge pada config tech_stack; "
                "isi AUTO:TECHSTACK dibiarkan seperti sekarang."
            )
            continue

        new_content = generate_section(
            client=client,
            section=section,
            current_content=current_content,
            config=config,
            github_profile=github_profile,
            repositories=repositories,
            verified_badges=(
                verified_badges if section == "TECHSTACK" else None
            ),
            max_featured_projects=max_featured_projects,
        )

        if section == "TECHSTACK" and not validate_badge_content(
            new_content,
            badge_groups,
        ):
            print(
                "Output AI untuk AUTO:TECHSTACK tidak sesuai daftar badge; "
                "memakai badge hasil generate kode."
            )
            new_content = verified_badges

        updated_readme = update_section(
            updated_readme,
            section,
            new_content,
        )

    for section in SVG_SECTIONS:
        print(f"Updating AUTO:{section}...")

        new_content = SECTION_GENERATORS[section]()

        updated_readme = update_section(
            updated_readme,
            section,
            new_content,
        )

    save_readme(updated_readme)

    print("README data successfully updated.")


if __name__ == "__main__":
    main()
