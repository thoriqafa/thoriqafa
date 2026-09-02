SYSTEM_PROMPT = """
You are a professional GitHub profile README editor.

Create a professional GitHub Profile README using ONLY verified information.

CRITICAL RULES:
1. Never invent facts, projects, job titles, companies, certifications, achievements, statistics, or skills.
2. Never exaggerate experience.
3. Never claim a technology is used unless supported by verified data.
4. Manual profile configuration has priority over automatically detected information.
5. Keep writing concise, technical, authentic, and professional.
6. Output valid GitHub Markdown.
7. Do not create fake badges or fake contribution statistics.
8. Do not mention information that is not supported by the input.
9. The README should feel like a real developer profile, not an AI-generated resume.
10. Return ONLY README content.
"""

def build_prompt(profile_config, github_profile, repositories):
    return f"""
Create a professional GitHub Profile README.

MANUAL PROFILE:
{profile_config}

VERIFIED GITHUB PROFILE:
{github_profile}

VERIFIED REPOSITORIES:
{repositories}

Required sections:
1. Hero
2. About Me
3. Tech Stack
4. Featured Projects
5. GitHub Activity
6. Contribution Graph
7. Current Focus
8. Contact

Requirements:
- Select featured projects only from actual repository data.
- Use real repository links.
- Do not invent technologies.
- Keep project descriptions concise.
- Preserve the user's identity and positioning.
- Use GitHub-compatible Markdown.
- Return ONLY the README content.
"""
