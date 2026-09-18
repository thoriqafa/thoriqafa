"""
Katalog badge shields.io untuk section AUTO:TECHSTACK.

Badge selalu dirender dari kode ini, bukan oleh AI, supaya URL-nya valid dan
teknologi yang tidak pernah dipakai tidak bisa muncul begitu saja.

- `BADGE_CATALOG`  : daftar badge yang boleh dipakai (id -> metadata).
- `build_badge_groups()` : gabungkan badge kurasi di config/profile.yml dengan
  bahasa repo GitHub yang belum tercantum.
- `validate_badge_content()` : pastikan output AI hanya memakai badge tersebut.
"""

import re
import sys

SHIELDS_URL = "https://img.shields.io/badge"
BADGE_STYLE = "style=flat-square"

# id -> (label, warna hex, slug logo simple-icons, warna logo)
BADGE_CATALOG = {
    # --- Languages -------------------------------------------------------
    "python": ("Python", "3776AB", "python", "white"),
    "php": ("PHP", "777BB4", "php", "white"),
    "delphi": ("Delphi", "EE1F35", "delphi", "white"),
    "typescript": ("TypeScript", "3178C6", "typescript", "white"),
    "javascript": ("JavaScript", "F7DF1E", "javascript", "black"),
    "java": ("Java", "ED8B00", "openjdk", "white"),
    "cplusplus": ("C++", "00599C", "cplusplus", "white"),
    "csharp": ("C%23", "239120", "csharp", "white"),
    "sql": ("SQL", "4479A1", "mysql", "white"),
    "html": ("HTML", "E34F26", "html5", "white"),
    "css": ("CSS", "1572B6", "css3", "white"),
    "go": ("Go", "00ADD8", "go", "white"),
    "rust": ("Rust", "000000", "rust", "white"),
    "kotlin": ("Kotlin", "7F52FF", "kotlin", "white"),
    "dart": ("Dart", "0175C2", "dart", "white"),
    "ruby": ("Ruby", "CC342D", "ruby", "white"),
    "powershell": ("PowerShell", "5391FE", "powershell", "white"),
    "bash": ("Shell", "4EAA25", "gnubash", "white"),
    "r": ("R", "276DC3", "r", "white"),
    "scala": ("Scala", "DC322F", "scala", "white"),
    "swift": ("Swift", "F05138", "swift", "white"),
    "objectivec": ("Objective-C", "438EFF", "apple", "white"),
    "perl": ("Perl", "39457E", "perl", "white"),
    "lua": ("Lua", "2C2D72", "lua", "white"),
    # --- Frameworks & tools ---------------------------------------------
    "laravel": ("Laravel", "FF2D20", "laravel", "white"),
    "codeigniter": ("CodeIgniter", "EF4223", "codeigniter", "white"),
    "nodejs": ("Node.js", "339933", "node.js", "white"),
    "fastapi": ("FastAPI", "009688", "fastapi", "white"),
    "docker": ("Docker", "2496ED", "docker", "white"),
    "linux": ("Linux", "FCC624", "linux", "black"),
    "git": ("Git", "F05032", "git", "white"),
    "mysql": ("MySQL", "4479A1", "mysql", "white"),
    "postgresql": ("PostgreSQL", "4169E1", "postgresql", "white"),
    "sqlserver": ("SQL_Server", "CC2927", "microsoftsqlserver", "white"),
    "mongodb": ("MongoDB", "47A248", "mongodb", "white"),
    "redis": ("Redis", "DC382D", "redis", "white"),
    "rabbitmq": ("RabbitMQ", "FF6600", "rabbitmq", "white"),
    "nginx": ("Nginx", "009639", "nginx", "white"),
    "bash_tools": ("Bash", "4EAA25", "gnubash", "white"),
    "githubactions": ("GitHub_Actions", "2088FF", "githubactions", "white"),
    "vscode": ("VS_Code", "007ACC", "visualstudiocode", "white"),
    "postman": ("Postman", "FF6C37", "postman", "white"),
    # --- AI & data -------------------------------------------------------
    "ai": ("Artificial_Intelligence", "412991", "openai", "white"),
    "jupyter": ("Jupyter", "F37626", "jupyter", "white"),
    "matlab": ("MATLAB", "0076A8", "mathworks", "white"),
    "tensorflow": ("TensorFlow", "FF6F00", "tensorflow", "white"),
    "pytorch": ("PyTorch", "EE4C2C", "pytorch", "white"),
    "pandas": ("Pandas", "150458", "pandas", "white"),
    "numpy": ("NumPy", "013243", "numpy", "white"),
}

# Nama bahasa dari GitHub API -> id badge di BADGE_CATALOG.
LANGUAGE_TO_BADGE = {
    "python": "python",
    "php": "php",
    "pascal": "delphi",
    "delphi": "delphi",
    "typescript": "typescript",
    "javascript": "javascript",
    "java": "java",
    "c++": "cplusplus",
    "c#": "csharp",
    "html": "html",
    "css": "css",
    "go": "go",
    "rust": "rust",
    "kotlin": "kotlin",
    "dart": "dart",
    "ruby": "ruby",
    "shell": "bash",
    "powershell": "powershell",
    "r": "r",
    "scala": "scala",
    "swift": "swift",
    "objective-c": "objectivec",
    "perl": "perl",
    "lua": "lua",
    "jupyter notebook": "jupyter",
    "matlab": "matlab",
    "plsql": "sql",
    "tsql": "sql",
}


def badge_url(badge_id):
    """Bangun URL shields.io untuk satu id badge. None kalau id tidak dikenal."""
    entry = BADGE_CATALOG.get(badge_id)

    if not entry:
        return None

    label, color, logo, logo_color = entry

    return (
        f"{SHIELDS_URL}/{label}-{color}"
        f"?{BADGE_STYLE}&logo={logo}&logoColor={logo_color}"
    )


def generic_badge_url(label):
    """Fallback untuk bahasa repo yang belum ada di katalog."""
    safe_label = label.strip().replace(" ", "_")
    return f"{SHIELDS_URL}/{safe_label}-555555?{BADGE_STYLE}"


def resolve_language(language):
    """
    Petakan bahasa dari GitHub ke (badge_id, url).

    badge_id bernilai None kalau bahasanya belum ada di katalog, tapi URL tetap
    dihasilkan supaya teknologi yang benar-benar dipakai tidak hilang.
    """
    key = (language or "").strip().lower()
    badge_id = LANGUAGE_TO_BADGE.get(key)

    if badge_id and badge_id in BADGE_CATALOG:
        return badge_id, badge_url(badge_id)

    return None, generic_badge_url(language)


def build_badge_groups(config, repositories):
    """
    Hasilkan grup badge: kurasi dari config/profile.yml dulu, lalu bahasa repo
    yang belum tercantum ditambahkan ke grup `auto_append_group`.
    """
    tech_stack = config.get("tech_stack") or {}
    groups = []
    seen_ids = set()
    seen_urls = set()

    for raw_group in tech_stack.get("groups") or []:
        name = str(raw_group.get("name") or "").strip()

        if not name:
            continue

        badges = []

        for badge_id in raw_group.get("badges") or []:
            url = badge_url(badge_id)

            if not url:
                print(f"Badge '{badge_id}' tidak ada di BADGE_CATALOG; dilewati.")
                continue

            if url in seen_urls:
                continue

            seen_ids.add(badge_id)
            seen_urls.add(url)
            badges.append(url)

        groups.append({"name": name, "badges": badges})

    if tech_stack.get("auto_append_languages", True):
        target_name = tech_stack.get("auto_append_group") or "Languages"
        languages = sorted({
            (repo.get("language") or "").strip()
            for repo in repositories or []
            if (repo.get("language") or "").strip()
        })

        for language in languages:
            badge_id, url = resolve_language(language)

            if url in seen_urls or (badge_id and badge_id in seen_ids):
                continue

            target = next(
                (group for group in groups if group["name"] == target_name),
                None,
            )

            if target is None:
                target = {"name": target_name, "badges": []}
                groups.append(target)

            target["badges"].append(url)
            seen_urls.add(url)

            if badge_id:
                seen_ids.add(badge_id)

    return [group for group in groups if group["badges"]]


def render_badge_groups(groups):
    """Render grup badge menjadi markdown section AUTO:TECHSTACK."""
    blocks = []

    for group in groups:
        lines = [f"### {group['name']}", "", "<p>"]
        lines.extend(f'  <img src="{url}" />' for url in group["badges"])
        lines.append("</p>")
        blocks.append("\n".join(lines))

    return "\n\n".join(blocks)


def allowed_badge_urls(groups):
    return {url for group in groups for url in group["badges"]}


SHIELDS_ANY_URL = re.compile(r"https://img\.shields\.io/[^\"')\s>]+")


def validate_badge_content(content, groups):
    """
    Terima output AI hanya kalau URL badge-nya persis sama dengan hasil kode:
    tidak ada badge karangan, dan tidak ada badge yang hilang.
    """
    allowed = allowed_badge_urls(groups)

    if not allowed:
        return True

    found = set(SHIELDS_ANY_URL.findall(content or ""))

    if found == allowed:
        return True

    missing = sorted(allowed - found)
    unknown = sorted(found - allowed)

    if missing:
        print(f"AI menghilangkan {len(missing)} badge: {missing}", file=sys.stderr)

    if unknown:
        print(f"AI menambah badge tak dikenal: {unknown}", file=sys.stderr)

    return False
