#!/usr/bin/env python3
import os
import sys
from datetime import datetime, timedelta

from github_data import get_stats_data

ASSETS_DIR = "assets"
STATS_SVG = os.path.join(ASSETS_DIR, "github-stats.svg")
STREAK_SVG = os.path.join(ASSETS_DIR, "github-streak.svg")
ACTIVITY_SVG = os.path.join(ASSETS_DIR, "github-activity.svg")

COLORS = {
    "bg": "#0d1117",
    "card_bg": "#161b22",
    "border": "#30363d",
    "text_primary": "#e6edf3",
    "text_secondary": "#8b949e",
    "text_muted": "#6e7681",
    "accent": "#58a6ff",
    "accent_hover": "#79c0ff",
    "green_1": "#0e2819",
    "green_2": "#003d19",
    "green_3": "#006d32",
    "green_4": "#26a641",
    "star": "#ffd700",
    "fork": "#58a6ff",
    "commit": "#d2a8ff",
    "pr": "#3fb950",
    "issue": "#f85149",
}

def format_number(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n/1_000:.1f}k".replace(".0k", "k")
    return str(n)

def escape_xml(text):
    return text

def generate_stats_svg(data):
    username = data["username"]
    stats = [
        ("Total Stars", format_number(data["total_stars"]), COLORS["star"]),
        ("Total Forks", format_number(data["total_forks"]), COLORS["fork"]),
        ("Followers", format_number(data["followers"]), COLORS["accent"]),
        ("Following", format_number(data["following"]), COLORS["text_secondary"]),
        ("Repositories", format_number(data["total_repos"]), COLORS["commit"]),
        ("Contributions", format_number(data["total_contributions"]), COLORS["green_4"]),
        ("Commits", format_number(data["total_commits"]), COLORS["commit"]),
        ("Pull Requests", format_number(data["total_prs"]), COLORS["pr"]),
        ("Issues", format_number(data["total_issues"]), COLORS["issue"]),
    ]

    card_width = 495
    card_height = 195
    padding = 20
    row_height = 35
    col_width = (card_width - padding * 2 - 15) // 3

    svg = f'''<svg width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GitHub Statistics for {username}">
  <defs>
    <linearGradient id="statsBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{COLORS['card_bg']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0d1117;stop-opacity:1" />
    </linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="{card_width}" height="{card_height}" rx="12" fill="url(#statsBg)" stroke="{COLORS['border']}" stroke-width="1"/>
  <rect x="0" y="0" width="{card_width}" height="48" rx="12" fill="{COLORS['bg']}" stroke="none"/>
  <text x="24" y="32" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="16" font-weight="600" fill="{COLORS['text_primary']}">📊 {escape_xml(username)}'s GitHub Stats</text>
'''

    for i, (label, value, color) in enumerate(stats):
        col = i % 3
        row = i // 3
        x = padding + col * (col_width + 7.5)
        y = 60 + row * row_height

        svg += f'''  <g transform="translate({x}, {y})">
    <rect width="{col_width}" height="30" rx="6" fill="{COLORS['bg']}" stroke="{COLORS['border']}" stroke-width="0.5"/>
    <text x="12" y="20" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="11" font-weight="400" fill="{COLORS['text_secondary']}">{escape_xml(label)}</text>
    <text x="{col_width - 12}" y="20" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="13" font-weight="600" fill="{color}" text-anchor="end">{escape_xml(value)}</text>
  </g>
'''

    svg += f'''  <text x="{card_width - 12}" y="{card_height - 10}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="9" fill="{COLORS['text_muted']}" text-anchor="end">Updated {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC</text>
</svg>'''

    return svg

def generate_streak_svg(data):
    current = data["current_streak"]
    longest = data["longest_streak"]

    card_width = 495
    card_height = 140
    padding = 24

    svg = f'''<svg width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GitHub Contribution Streak for {data['username']}">
  <defs>
    <linearGradient id="streakBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{COLORS['card_bg']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0d1117;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="fireGradient" x1="0%" y1="100%" x2="0%" y2="0%">
      <stop offset="0%" style="stop-color:#ff6b35;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#ffd700;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#fff;stop-opacity:1" />
    </linearGradient>
    <filter id="fireGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="{card_width}" height="{card_height}" rx="12" fill="url(#streakBg)" stroke="{COLORS['border']}" stroke-width="1"/>
  <rect x="0" y="0" width="{card_width}" height="48" rx="12" fill="{COLORS['bg']}" stroke="none"/>
  <text x="24" y="32" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="16" font-weight="600" fill="{COLORS['text_primary']}">🔥 Contribution Streak</text>

  <g transform="translate({padding}, 65)">
    <text x="0" y="24" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="12" font-weight="500" fill="{COLORS['text_secondary']}">Current Streak</text>
    <text x="0" y="54" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="36" font-weight="700" fill="url(#fireGradient)" filter="url(#fireGlow)">{current}</text>
    <text x="0" y="76" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="11" fill="{COLORS['text_muted']}">days</text>
  </g>

  <g transform="translate({card_width // 2 + 10}, 65)">
    <text x="0" y="24" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="12" font-weight="500" fill="{COLORS['text_secondary']}">Longest Streak</text>
    <text x="0" y="54" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="36" font-weight="700" fill="{COLORS['accent']}">{longest}</text>
    <text x="0" y="76" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="11" fill="{COLORS['text_muted']}">days</text>
  </g>

  <text x="{card_width - 12}" y="{card_height - 10}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="9" fill="{COLORS['text_muted']}" text-anchor="end">Updated {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC</text>
</svg>'''

    return svg

def generate_activity_svg(data):
    days = data["contribution_days"]
    if not days:
        return generate_empty_activity_svg(data["username"])

    days_sorted = sorted(days, key=lambda d: d["date"])
    date_to_count = {d["date"]: d["count"] for d in days_sorted}

    today = datetime.utcnow().date()
    start_date = today - timedelta(days=364)

    weeks = []
    current_week = []
    check_date = start_date

    while check_date <= today:
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
        date_str = check_date.isoformat()
        count = date_to_count.get(date_str, 0)
        current_week.append((date_str, count))
        check_date += timedelta(days=1)
    if current_week:
        weeks.append(current_week)

    max_count = max(d["count"] for d in days_sorted) if days_sorted else 1

    def get_color(count):
        if count == 0:
            return COLORS["green_1"]
        elif count <= max_count * 0.25:
            return COLORS["green_2"]
        elif count <= max_count * 0.5:
            return COLORS["green_3"]
        elif count <= max_count * 0.75:
            return COLORS["green_3"]
        else:
            return COLORS["green_4"]

    cell_size = 11
    cell_gap = 2
    left_padding = 40
    top_padding = 30
    week_count = len(weeks)

    svg_width = left_padding + week_count * (cell_size + cell_gap) + 20
    svg_height = top_padding + 7 * (cell_size + cell_gap) + 60

    months = []
    month_positions = {}
    for week_idx, week in enumerate(weeks):
        for day_idx, (date_str, _) in enumerate(week):
            dt = datetime.fromisoformat(date_str)
            if day_idx == 0:
                month_key = dt.strftime("%b")
                if month_key not in month_positions:
                    x = left_padding + week_idx * (cell_size + cell_gap) + cell_size // 2
                    month_positions[month_key] = x

    svg = f'''<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GitHub Contribution Activity for {data['username']}">
  <defs>
    <linearGradient id="activityBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{COLORS['card_bg']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0d1117;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="{svg_width}" height="{svg_height}" rx="12" fill="url(#activityBg)" stroke="{COLORS['border']}" stroke-width="1"/>
  <rect x="0" y="0" width="{svg_width}" height="48" rx="12" fill="{COLORS['bg']}" stroke="none"/>
  <text x="24" y="32" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="16" font-weight="600" fill="{COLORS['text_primary']}">📈 Contribution Activity</text>
'''

    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, label in enumerate(day_labels):
        y = top_padding + i * (cell_size + cell_gap) + cell_size - 2
        svg += f'''  <text x="36" y="{y}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="9" fill="{COLORS['text_muted']}" text-anchor="end">{label}</text>
'''

    for month, x in month_positions.items():
        svg += f'''  <text x="{x}" y="{top_padding - 6}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="9" fill="{COLORS['text_secondary']}" text-anchor="middle">{month}</text>
'''

    for week_idx, week in enumerate(weeks):
        for day_idx, (date_str, count) in enumerate(week):
            x = left_padding + week_idx * (cell_size + cell_gap)
            y = top_padding + day_idx * (cell_size + cell_gap)
            color = get_color(count)
            svg += f'''  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{color}" data-date="{date_str}" data-count="{count}"/>
'''

    legend_x = left_padding
    legend_y = svg_height - 35
    legend_labels = ["Less", "More"]
    legend_colors = [COLORS["green_1"], COLORS["green_2"], COLORS["green_3"], COLORS["green_4"]]

    svg += f'''  <text x="{legend_x}" y="{legend_y}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="10" fill="{COLORS['text_secondary']}">Less</text>
'''
    for i, color in enumerate(legend_colors):
        x = legend_x + 45 + i * 14
        svg += f'''  <rect x="{x}" y="{legend_y - 8}" width="10" height="10" rx="2" fill="{color}"/>
'''
    svg += f'''  <text x="{legend_x + 45 + 4 * 14 + 5}" y="{legend_y}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="10" fill="{COLORS['text_secondary']}">More</text>
  <text x="{svg_width - 12}" y="{svg_height - 10}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="9" fill="{COLORS['text_muted']}" text-anchor="end">Updated {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC</text>
</svg>'''

    return svg

def generate_empty_activity_svg(username):
    card_width = 495
    card_height = 200

    return f'''<svg width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="No contribution data available">
  <defs>
    <linearGradient id="emptyBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{COLORS['card_bg']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0d1117;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="{card_width}" height="{card_height}" rx="12" fill="url(#emptyBg)" stroke="{COLORS['border']}" stroke-width="1"/>
  <rect x="0" y="0" width="{card_width}" height="48" rx="12" fill="{COLORS['bg']}" stroke="none"/>
  <text x="24" y="32" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="16" font-weight="600" fill="{COLORS['text_primary']}">📈 Contribution Activity</text>
  <text x="{card_width/2}" y="{card_height/2}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="14" fill="{COLORS['text_secondary']}" text-anchor="middle" dominant-baseline="middle">No contribution data available</text>
  <text x="{card_width - 12}" y="{card_height - 10}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="9" fill="{COLORS['text_muted']}" text-anchor="end">Updated {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC</text>
</svg>'''

def save_svg(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {path}")

def main():
    print("Fetching GitHub data...")
    data = get_stats_data()

    print("Generating GitHub Statistics SVG...")
    stats_svg = generate_stats_svg(data)
    save_svg(STATS_SVG, stats_svg)

    print("Generating Contribution Streak SVG...")
    streak_svg = generate_streak_svg(data)
    save_svg(STREAK_SVG, streak_svg)

    print("Generating Contribution Activity SVG...")
    activity_svg = generate_activity_svg(data)
    save_svg(ACTIVITY_SVG, activity_svg)

    print("All charts generated successfully!")

if __name__ == "__main__":
    main()