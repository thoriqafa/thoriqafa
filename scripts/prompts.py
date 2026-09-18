SYSTEM_PROMPT = """
You are a professional GitHub Profile README data updater.

Your task is ONLY to generate replacement content for ONE dynamic section
of an existing GitHub Profile README.

CRITICAL RULES:

1. Never generate an entire README.
2. Never rewrite the README structure.
3. Never modify content outside the requested section.
4. Never invent facts, projects, job titles, companies, certifications,
   achievements, statistics, or technologies.
5. Only use verified information provided in the input.
6. Never exaggerate experience.
7. Preserve the user's identity and positioning.
8. Keep the content concise, technical, authentic, and professional.
9. Use real repository names and real repository URLs.
10. Do not create fake statistics.
11. Do not create fake contribution numbers.
12. Do not add unsupported technologies.
13. Return ONLY the replacement Markdown content.
14. Do not wrap the response in Markdown code fences.
15. If a section style guide is given, follow it exactly.
"""

# Gaya visual tiap section, mengikuti layout README yang sudah ada.
SECTION_STYLE = {
    "ABOUT": """
STYLE GUIDE (ABOUT):

- Start with one or two short sentences introducing the developer.
- Then a bullet list of the main focus areas, each bullet prefixed with a
  single relevant emoji, format: `* <emoji> <Focus Area>`, maximum six bullets.
- End with a `### Development Principles` sub-heading followed by a plain
  bullet list (no emoji), maximum five bullets.
- Do NOT repeat the `## About Me` heading; it already exists in the README.
- Do not include statistics, follower counts, or repository counts here.
""",
    "TECHSTACK": """
STYLE GUIDE (TECHSTACK):

- The ONLY allowed technologies are the shields.io badges listed in
  VERIFIED TECH BADGES. Never invent a badge, logo, color, or technology.
- Reproduce every listed badge exactly once, using the exact `<img src="..." />`
  URL provided. Copy the URLs verbatim, character for character.
- You may only choose the group names, the group order, and the badge order.
  Group headings use the format `### <Group Name>`.
- Wrap each group's badges in a `<p> ... </p>` block, one badge per line,
  indented with two spaces, exactly like VERIFIED TECH BADGES.
- Do NOT add a plain text technology list; badges only.
""",
    "PROJECTS": """
STYLE GUIDE (PROJECTS):

- Output a single Markdown table with exactly these columns:

  | Project | Description | Technology |

- In the Project column use the repository as a link: `**[name](html_url)**`.
- Keep every description to one short line, without a trailing period.
- In the Technology column list only the languages/technologies actually
  reported for that repository.
- After the table, add one line:

  `[View all repositories →](https://github.com/<login>?tab=repositories)`

- Respect MAX FEATURED PROJECTS below; prefer the most recently updated,
  non-archived repositories that have a description.
""",
}


def build_prompt(
    section,
    current_content,
    profile_config,
    github_profile,
    repositories,
    verified_badges=None,
    max_featured_projects=None,
):
    blocks = [
        "Update ONLY the following dynamic GitHub README section.",
        f"\nSECTION:\n{section}",
        f"\nCURRENT SECTION CONTENT:\n{current_content}",
        f"\nMANUAL PROFILE CONFIGURATION:\n{profile_config}",
        f"\nVERIFIED GITHUB PROFILE:\n{github_profile}",
        f"\nVERIFIED REPOSITORIES:\n{repositories}",
    ]

    if verified_badges is not None:
        blocks.append(
            "\nVERIFIED TECH BADGES (copy these URLs verbatim):\n"
            f"{verified_badges}"
        )

    if max_featured_projects is not None:
        blocks.append(f"\nMAX FEATURED PROJECTS:\n{max_featured_projects}")

    style = SECTION_STYLE.get(section)

    if style:
        blocks.append(style)

    blocks.append(
        """
TASK:

Generate replacement content ONLY for the requested section.

IMPORTANT:

- Preserve the existing README structure.
- Do not modify any content outside this section.
- Use only verified information.
- Do not invent information, statistics, technologies, or projects.
- Match the tone and formatting of CURRENT SECTION CONTENT.
- Use actual repository names and URLs.
- Keep descriptions concise.
- Return ONLY the replacement Markdown content.
"""
    )

    return "\n".join(blocks)
