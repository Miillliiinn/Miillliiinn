import os
import requests
import json

USERNAME = "Miillliiinn"
TOKEN = os.environ.get("GH_TOKEN", "")

headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

# ── 1. Fetch all public repos ────────────────────────────────────────────────

repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=public"
repos = requests.get(repos_url, headers=headers).json()

# ── 2. Aggregate bytes per language ─────────────────────────────────────────

totals = {}
for repo in repos:
    if repo.get("fork"):
        continue
    lang_url = repo.get("languages_url")
    if not lang_url:
        continue
    langs = requests.get(lang_url, headers=headers).json()
    for lang, bytes_count in langs.items():
        totals[lang] = totals.get(lang, 0) + bytes_count

if not totals:
    print("No language data found.")
    exit(0)

# ── 3. Sort and keep top 6 ───────────────────────────────────────────────────

sorted_langs = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:6]
max_bytes = sorted_langs[0][1]

# ── 4. Color map ─────────────────────────────────────────────────────────────

COLOR_MAP = {
    "C":          "#a8c4ff",
    "C++":        "#c4a8ff",
    "Python":     "#a8ffdc",
    "JavaScript": "#fff0a8",
    "TypeScript": "#a8e4ff",
    "Shell":      "#ffa8a8",
    "Makefile":   "#d4a8ff",
    "HTML":       "#ffcba8",
    "CSS":        "#a8ffb8",
    "Dockerfile": "#a8d8ff",
    "Go":         "#a8fff0",
    "Rust":       "#ffb8a8",
}
DEFAULT_COLORS = ["#a8c4ff","#c4a8ff","#a8ffdc","#fff0a8","#ffa8a8","#a8d8ff"]

# ── 5. Generate SVG ──────────────────────────────────────────────────────────

ROW_H   = 32
PAD_TOP = 52
WIDTH   = 495
HEIGHT  = PAD_TOP + ROW_H * len(sorted_langs) + 16
BAR_X   = 90
BAR_W   = 340
MAX_BAR = 310

lines = []
lines.append(f'<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">')
lines.append("""  <style>
    .ttl { font: 600 11px 'Segoe UI',monospace; fill: #6b6b8a; letter-spacing: 2px; }
    .lng { font: 500 13px 'Segoe UI',monospace; fill: #e2e2f0; }
    .lbl { font: 400 11px 'Segoe UI',monospace; fill: #6b6b8a; }
  </style>""")

lines.append(f'  <rect width="{WIDTH}" height="{HEIGHT}" rx="10" fill="#0d0d14" stroke="#1e1e2e" stroke-width="1"/>')
lines.append(f'  <text x="24" y="28" class="ttl">LANGUAGES</text>')
lines.append(f'  <line x1="24" y1="36" x2="{WIDTH-24}" y2="36" stroke="#1e1e2e" stroke-width="1"/>')

for i, (lang, count) in enumerate(sorted_langs):
    y_center = PAD_TOP + i * ROW_H + 10
    bar_fill = int((count / max_bytes) * MAX_BAR)
    color = COLOR_MAP.get(lang, DEFAULT_COLORS[i % len(DEFAULT_COLORS)])

    # Shorten long label
    display = lang if len(lang) <= 12 else lang[:11] + "…"

    lines.append(f'  <text x="24" y="{y_center + 4}" class="lng">{display}</text>')
    lines.append(f'  <rect x="{BAR_X}" y="{y_center - 3}" width="{BAR_W}" height="6" rx="3" fill="#1e1e2e"/>')
    lines.append(f'  <rect x="{BAR_X}" y="{y_center - 3}" width="{bar_fill}" height="6" rx="3" fill="{color}"/>')

    # Right label: percentage
    pct = round(count / sum(v for _, v in sorted_langs) * 100, 1)
    lines.append(f'  <text x="{WIDTH - 24}" y="{y_center + 4}" class="lbl" text-anchor="end">{pct}%</text>')

lines.append('</svg>')

svg_content = "\n".join(lines)

with open("langs.svg", "w") as f:
    f.write(svg_content)

print(f"Generated langs.svg with {len(sorted_langs)} languages.")
print(json.dumps({k: v for k, v in sorted_langs}, indent=2))
