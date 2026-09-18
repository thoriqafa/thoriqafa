#!/usr/bin/env python3
"""
Generate kartu statistik GitHub sebagai SVG.

Semua kartu memakai satu design system yang sama (warna, tipografi, radius,
dan lebar kartu) dan mendukung tema terang/gelap otomatis lewat
`prefers-color-scheme`, sehingga kartu ikut menyesuaikan saat pengunjung
memakai dark mode.

Ukuran tiap kartu sengaja dibuat sama dengan atribut `width` di README supaya
SVG dirender pada skala 1:1 (tidak buram karena diperkecil).
"""

import os
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape

from github_data import get_stats_data


ASSETS_DIR = "assets"
STATS_SVG = os.path.join(ASSETS_DIR, "github-stats.svg")
STREAK_SVG = os.path.join(ASSETS_DIR, "github-streak.svg")
ACTIVITY_SVG = os.path.join(ASSETS_DIR, "github-activity.svg")

STATS_WIDTH = 495
STATS_HEIGHT = 246
STREAK_WIDTH = 495
STREAK_HEIGHT = 152

# Grid activity: 53 kolom x 7 baris, sel 9px + jarak 3px.
ACTIVITY_CELL = 9
ACTIVITY_GAP = 3
ACTIVITY_STEP = ACTIVITY_CELL + ACTIVITY_GAP
ACTIVITY_LEFT = 34
ACTIVITY_COLUMNS = 53
ACTIVITY_WIDTH = ACTIVITY_LEFT + ACTIVITY_COLUMNS * ACTIVITY_STEP - ACTIVITY_GAP + 20

HEADER_HEIGHT = 46
CARD_RADIUS = 12
CARD_PADDING = 24

# Palet GitHub: (light, dark). Dipakai lewat CSS variable.
THEME = {
    "surface-a": ("#ffffff", "#0d1117"),
    "surface-b": ("#f6f8fa", "#161b22"),
    "border": ("#d0d7de", "#30363d"),
    "header": ("#f6f8fa", "#161b22"),
    "text": ("#1f2328", "#e6edf3"),
    "muted": ("#59636e", "#8b949e"),
    "faint": ("#818b98", "#6e7681"),
    "level-0": ("#ebedf0", "#21262d"),
    "level-1": ("#9be9a8", "#0e4429"),
    "level-2": ("#40c463", "#006d32"),
    "level-3": ("#30a14e", "#26a641"),
    "level-4": ("#216e39", "#39d353"),
    "c-star": ("#bf8700", "#d29922"),
    "c-fork": ("#0969da", "#58a6ff"),
    "c-follow": ("#8250df", "#a371f7"),
    "c-repo": ("#1b7c83", "#39c5cf"),
    "c-contrib": ("#1a7f37", "#3fb950"),
    "c-commit": ("#bc4c00", "#f0883e"),
    "c-pr": ("#bf3989", "#db61a2"),
    "c-issue": ("#cf222e", "#f85149"),
}

FONT_STACK = (
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
)

STYLE_RULES = """
      .card-frame { stroke: var(--border); stroke-width: 1; }
      .card-grad-a { stop-color: var(--surface-a); }
      .card-grad-b { stop-color: var(--surface-b); }
      .header-fill { fill: var(--header); }
      .divider { stroke: var(--border); stroke-width: 1; }
      .title { font-family: FONT; font-size: 15px; font-weight: 600; fill: var(--text); }
      .subtitle { font-family: FONT; font-size: 11px; fill: var(--muted); }
      .label { font-family: FONT; font-size: 10px; font-weight: 600; letter-spacing: 0.6px; fill: var(--muted); }
      .value { font-family: FONT; font-size: 19px; font-weight: 700; }
      .metric { font-family: FONT; font-size: 30px; font-weight: 700; }
      .unit { font-family: FONT; font-size: 12px; fill: var(--muted); }
      .axis { font-family: FONT; font-size: 9px; fill: var(--muted); }
      .meta { font-family: FONT; font-size: 9px; fill: var(--faint); }
      .c-star { fill: var(--c-star); }
      .c-fork { fill: var(--c-fork); }
      .c-follow { fill: var(--c-follow); }
      .c-muted { fill: var(--muted); }
      .c-repo { fill: var(--c-repo); }
      .c-contrib { fill: var(--c-contrib); }
      .c-commit { fill: var(--c-commit); }
      .c-pr { fill: var(--c-pr); }
      .c-issue { fill: var(--c-issue); }
      .level-0 { fill: var(--level-0); }
      .level-1 { fill: var(--level-1); }
      .level-2 { fill: var(--level-2); }
      .level-3 { fill: var(--level-3); }
      .level-4 { fill: var(--level-4); }
"""


def utcnow():
    return datetime.now(timezone.utc)


def format_number(number):
    """Angka ringkas untuk kartu statistik (1.2k, 3.4M)."""
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M".replace(".0M", "M")
    if number >= 1_000:
        return f"{number / 1_000:.1f}k".replace(".0k", "k")
    return str(number)


def format_exact(number):
    """Angka lengkap dengan pemisah ribuan, untuk teks yang masih muat."""
    return f"{number:,}"


# ============================================================
# CARD SHELL
# ============================================================

def theme_css():
    light = "\n".join(
        f"        --{name}: {colors[0]};" for name, colors in THEME.items()
    )
    dark = "\n".join(
        f"        --{name}: {colors[1]};" for name, colors in THEME.items()
    )

    return (
        "      :root {\n"
        f"{light}\n"
        "      }\n"
        "      @media (prefers-color-scheme: dark) {\n"
        "        :root {\n"
        f"{dark}\n"
        "        }\n"
        "      }"
    )


def card_open(width, height, aria_label):
    gradient_id = f"card-{width}x{height}"

    return (
        f'<svg width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="{escape(aria_label)}">\n'
        "  <defs>\n"
        f'    <linearGradient id="{gradient_id}" x1="0%" y1="0%" x2="100%" y2="100%">\n'
        '      <stop offset="0%" class="card-grad-a" />\n'
        '      <stop offset="100%" class="card-grad-b" />\n'
        "    </linearGradient>\n"
        "  </defs>\n"
        "  <style>\n"
        f"{theme_css()}\n"
        f"{STYLE_RULES.replace('FONT', FONT_STACK)}"
        "  </style>\n"
        f'  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
        f'rx="{CARD_RADIUS}" fill="url(#{gradient_id})" class="card-frame" />\n'
    )


def card_header(width, height, title, right_text, aria_label):
    """
    Header kartu: sudut atas membulat, sudut bawah rata, plus garis pemisah.
    """
    inner = HEADER_HEIGHT - 1
    svg = card_open(width, height, aria_label)

    svg += (
        f'  <rect x="1" y="1" width="{width - 2}" height="{inner}" '
        f'rx="{CARD_RADIUS - 1}" class="header-fill" />\n'
        f'  <rect x="1" y="{1 + inner // 2}" width="{width - 2}" '
        f'height="{inner - inner // 2}" class="header-fill" />\n'
        f'  <line x1="1" y1="{HEADER_HEIGHT}" x2="{width - 1}" '
        f'y2="{HEADER_HEIGHT}" class="divider" />\n'
        f'  <text x="{CARD_PADDING}" y="30" class="title">'
        f"{escape(title)}</text>\n"
    )

    if right_text:
        svg += (
            f'  <text x="{width - CARD_PADDING}" y="29" class="subtitle" '
            f'text-anchor="end">{escape(right_text)}</text>\n'
        )

    return svg


def card_footer(svg, width, height, update_time=None):
    stamp = (update_time or utcnow()).strftime("%Y-%m-%d %H:%M")
    svg += (
        f'  <text x="{width - CARD_PADDING}" y="{height - 12}" class="meta" '
        f'text-anchor="end">Updated {stamp} UTC</text>\n'
    )
    return svg


# ============================================================
# STATS CARD
# ============================================================

STATS_METRICS = (
    ("Total Stars", "total_stars", "c-star"),
    ("Total Forks", "total_forks", "c-fork"),
    ("Followers", "followers", "c-follow"),
    ("Following", "following", "c-muted"),
    ("Repositories", "total_repos", "c-repo"),
    ("Contributions", "total_contributions", "c-contrib"),
    ("Commits", "total_commits", "c-commit"),
    ("Pull Requests", "total_prs", "c-pr"),
    ("Issues", "total_issues", "c-issue"),
)

STATS_COLUMNS = 3
STATS_ROW_HEIGHT = 54


def generate_stats_svg(data):
    width = STATS_WIDTH
    height = STATS_HEIGHT
    username = data.get("username") or ""

    column_width = (width - CARD_PADDING * 2) / STATS_COLUMNS
    top = HEADER_HEIGHT + 16

    svg = card_header(
        width,
        height,
        "GitHub Statistics",
        f"@{username}" if username else None,
        f"GitHub statistics for {username}",
    )

    for index, (label, key, color_class) in enumerate(STATS_METRICS):
        column = index % STATS_COLUMNS
        row = index // STATS_COLUMNS
        x = CARD_PADDING + column * column_width
        y = top + row * STATS_ROW_HEIGHT

        svg += (
            f'  <text x="{x:.0f}" y="{y + 12}" class="label">'
            f"{escape(label.upper())}</text>\n"
            f'  <text x="{x:.0f}" y="{y + 42}" class="value {color_class}">'
            f"{format_number(data.get(key, 0))}</text>\n"
        )

    svg = card_footer(svg, width, height)
    svg += "</svg>"

    return svg


# ============================================================
# STREAK CARD
# ============================================================

def generate_streak_svg(data):
    width = STREAK_WIDTH
    height = STREAK_HEIGHT

    metrics = (
        ("Current Streak", data.get("current_streak", 0), "days", "c-contrib"),
        ("Longest Streak", data.get("longest_streak", 0), "days", "c-fork"),
        (
            "Total Contributions",
            data.get("total_contributions", 0),
            "",
            "c-follow",
        ),
    )

    column_width = (width - CARD_PADDING * 2) / len(metrics)
    label_y = HEADER_HEIGHT + 28
    value_y = HEADER_HEIGHT + 80

    svg = card_header(
        width,
        height,
        "Contribution Streak",
        "Last 365 days",
        f"Contribution streak for {data.get('username') or 'user'}",
    )

    for index, (label, value, unit, color_class) in enumerate(metrics):
        x = CARD_PADDING + index * column_width

        if index:
            divider_x = CARD_PADDING + index * column_width - 12
            svg += (
                f'  <line x1="{divider_x:.0f}" y1="{label_y - 12}" '
                f'x2="{divider_x:.0f}" y2="{value_y + 10}" class="divider" />\n'
            )

        value_markup = (
            f'<tspan>{format_number(value)}</tspan>'
            f'<tspan class="unit" dx="6">{unit}</tspan>'
        ) if unit else f'<tspan>{format_number(value)}</tspan>'

        svg += (
            f'  <text x="{x:.0f}" y="{label_y}" class="label">'
            f"{escape(label.upper())}</text>\n"
            f'  <text x="{x:.0f}" y="{value_y}" class="metric {color_class}">'
            f"{value_markup}</text>\n"
        )

    svg = card_footer(svg, width, height)
    svg += "</svg>"

    return svg


# ============================================================
# ACTIVITY CARD
# ============================================================

WEEKDAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}


def quantile_thresholds(counts):
    """
    Ambang batas intensitas berbasis kuartil dari kontribusi non-nol, supaya
    sebaran warna tetap informatif walau jumlah kontribusinya kecil.
    """
    non_zero = sorted(count for count in counts if count > 0)

    if not non_zero:
        return None

    length = len(non_zero)

    return (
        non_zero[length // 4],
        non_zero[length // 2],
        non_zero[(3 * length) // 4],
    )


def intensity_level(count, thresholds):
    if count <= 0 or not thresholds:
        return 0

    for level, threshold in enumerate(thresholds, start=1):
        if count <= threshold:
            return level

    return 4


def build_weeks(days_by_date, end_date, start_date):
    """
    Susun grid 53 kolom x 7 baris yang sejajar dengan hari Minggu, jadi baris
    ke-0 selalu Minggu dan label hari tidak pernah bergeser.
    """
    days_since_sunday = (end_date.weekday() + 1) % 7
    last_sunday = end_date - timedelta(days=days_since_sunday)
    first_sunday = last_sunday - timedelta(days=(ACTIVITY_COLUMNS - 1) * 7)

    weeks = []
    cursor = first_sunday

    while cursor <= last_sunday:
        week = []

        for offset in range(7):
            day = cursor + timedelta(days=offset)

            if day < start_date or day > end_date:
                week.append(None)
            else:
                week.append((day, days_by_date.get(day.isoformat(), 0)))

        weeks.append(week)
        cursor += timedelta(days=7)

    return weeks


def month_labels(weeks, minimum_gap=36):
    """
    Label bulan diletakkan pada kolom yang memuat tanggal 1, dan dilewati kalau
    terlalu rapat dengan label sebelumnya supaya tidak bertumpuk.
    """
    labels = []
    last_x = None

    for column, week in enumerate(weeks):
        first_of_month = None

        for entry in week:
            if entry and entry[0].day == 1:
                first_of_month = entry[0]
                break

        if first_of_month is None:
            continue

        x = ACTIVITY_LEFT + column * ACTIVITY_STEP

        if last_x is None or x - last_x >= minimum_gap:
            labels.append((x, first_of_month.strftime("%b")))
            last_x = x

    return labels


def generate_activity_svg(data):
    days = data.get("contribution_days") or []

    if not days:
        return generate_empty_activity_svg(data.get("username"))

    today = utcnow().date()
    start_date = today - timedelta(days=364)
    days_by_date = {entry["date"]: entry["count"] for entry in days}

    thresholds = quantile_thresholds(entry["count"] for entry in days)
    weeks = build_weeks(days_by_date, today, start_date)

    width = ACTIVITY_WIDTH
    grid_top = HEADER_HEIGHT + 24
    grid_height = 7 * ACTIVITY_STEP - ACTIVITY_GAP
    footer_y = grid_top + grid_height + 30
    height = footer_y + 12

    total = data.get("total_contributions", 0)
    suffix = "" if total == 1 else "s"

    svg = card_header(
        width,
        height,
        "Contribution Activity",
        f"{format_exact(total)} contribution{suffix} in the last year",
        f"Contribution activity for {data.get('username') or 'user'}",
    )

    for x, month in month_labels(weeks):
        svg += (
            f'  <text x="{x}" y="{HEADER_HEIGHT + 14}" class="axis" '
            f'text-anchor="start">{escape(month)}</text>\n'
        )

    for row, label in WEEKDAY_LABELS.items():
        y = grid_top + row * ACTIVITY_STEP + ACTIVITY_CELL - 1
        svg += (
            f'  <text x="{ACTIVITY_LEFT - 6}" y="{y}" class="axis" '
            f'text-anchor="end">{label}</text>\n'
        )

    for column, week in enumerate(weeks):
        for row, entry in enumerate(week):
            if entry is None:
                continue

            day, count = entry
            x = ACTIVITY_LEFT + column * ACTIVITY_STEP
            y = grid_top + row * ACTIVITY_STEP
            level = intensity_level(count, thresholds)

            svg += (
                f'  <rect x="{x}" y="{y}" width="{ACTIVITY_CELL}" '
                f'height="{ACTIVITY_CELL}" rx="2" class="level-{level}">'
            )

            if count:
                plural = "s" if count != 1 else ""
                svg += (
                    "<title>"
                    f"{count} contribution{plural} "
                    f"on {day.strftime('%b')} {day.day}, {day.year}"
                    "</title>"
                )

            svg += "</rect>\n"

    svg += (
        f'  <text x="{ACTIVITY_LEFT}" y="{footer_y}" class="axis">Less</text>\n'
    )

    legend_x = ACTIVITY_LEFT + 34

    for level in range(5):
        svg += (
            f'  <rect x="{legend_x + level * 14}" y="{footer_y - 9}" '
            f'width="10" height="10" rx="2" class="level-{level}" />\n'
        )

    svg += (
        f'  <text x="{legend_x + 5 * 14 + 4}" y="{footer_y}" class="axis">'
        "More</text>\n"
    )

    svg = card_footer(svg, width, height)
    svg += "</svg>"

    return svg


def generate_empty_activity_svg(username):
    width = ACTIVITY_WIDTH
    height = 150

    svg = card_header(
        width,
        height,
        "Contribution Activity",
        "No data",
        f"No contribution activity available for {username}",
    )

    svg += (
        f'  <text x="{width / 2:.0f}" y="{HEADER_HEIGHT + 58}" '
        'class="subtitle" text-anchor="middle">'
        "No contribution data available</text>\n"
    )

    svg = card_footer(svg, width, height)
    svg += "</svg>"

    return svg


# ============================================================
# ENTRY POINT
# ============================================================

def save_svg(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"Saved: {path}")


def main():
    print("Fetching GitHub data...")
    data = get_stats_data()

    print("Generating GitHub Statistics card...")
    save_svg(STATS_SVG, generate_stats_svg(data))

    print("Generating Contribution Streak card...")
    save_svg(STREAK_SVG, generate_streak_svg(data))

    print("Generating Contribution Activity card...")
    save_svg(ACTIVITY_SVG, generate_activity_svg(data))

    print("All charts generated successfully!")


if __name__ == "__main__":
    main()
