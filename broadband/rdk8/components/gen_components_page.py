# If not stated otherwise in this file or this component's LICENSE file the
# following copyright and licenses apply:
#
# Copyright 2023 RDK Management
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generate components/index.html from ethwan-router-components.json, using
the same shared site shell (topnav + hero banner) as every other page —
unlike full-list.html or the other gen_*.py outputs in this folder, this one
now goes through layout.py's render_page()/render_hero()/render_topnav()
instead of a standalone hand-authored <style> block.

components/index.html sits one directory below the repo root, so this script
passes path_prefix="../" to render_page() — that's what makes the logo, nav
links, and search index fetch resolve correctly from inside components/.

Usage:
    python3 gen_components_page.py --json ethwan-router-components.json --out index.html

Run this whenever ethwan-router-components.json changes (i.e. after
extract_components.py / build_site.py step 4), so the page stays in sync
with the .xlsx it's derived from.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from layout import render_hero, render_page  # noqa: E402

FULL_DETAILS_URL = "full-list.html"

# Same fixed/rotating palettes as gen_simple_html.py, kept in sync so the
# type/category pill colors look identical to the rest of the components
# tooling (full-list.html, any other gen_simple_html.py output).
TIER_COLORS = {
    "gold":  {"bg": "#fef3c7", "fg": "#92400e"},
    "blue":  {"bg": "#dbeafe", "fg": "#1e40af"},
    "gray":  {"bg": "#f3f4f6", "fg": "#374151"},
    "green": {"bg": "#d1fae5", "fg": "#065f46"},
}
CATEGORY_PALETTE = [
    {"bg": "#d1fae5", "fg": "#065f46"},
    {"bg": "#fde2e2", "fg": "#991b1b"},
    {"bg": "#fef3c7", "fg": "#92400e"},
    {"bg": "#dbeafe", "fg": "#1e40af"},
    {"bg": "#ede9fe", "fg": "#5b21b6"},
    {"bg": "#e0f2fe", "fg": "#075985"},
    {"bg": "#fce7f3", "fg": "#9d174d"},
    {"bg": "#e5e7eb", "fg": "#374151"},
]


# Fixed style for the Layer pill (always Middleware for all RDK-B components)
LAYER_STYLE = {"bg": "#f0fdf4", "fg": "#166534"}


def category_color(category: str) -> dict:
    idx = int(hashlib.md5(category.encode("utf-8")).hexdigest(), 16) % len(CATEGORY_PALETTE)
    return CATEGORY_PALETTE[idx]


def esc(s) -> str:
    return html.escape("" if s is None else str(s))


def build_body(data: dict) -> str:
    subtitle = data.get("subtitle", "")
    schema_version = data["schemaVersion"]
    generated_at = data["generatedAt"]
    tiers = {t["id"]: t for t in data.get("tiers", [])}
    components = sorted(data["components"], key=lambda c: (c["tier"] != "common-core", c["name"].lower()))

    legend_html = "".join(
        f'<span class="pill" style="background:{TIER_COLORS[t["color"]]["bg"]};color:{TIER_COLORS[t["color"]]["fg"]}">{esc(t["label"])}</span>'
        for t in tiers.values()
    )

    # Unique categories and tier labels for filter dropdowns
    categories  = sorted({c["category"] or "Uncategorized" for c in components})
    tier_labels = sorted({tiers.get(c["tier"], {"label": c["tier"]})["label"] for c in components})

    rows_html = []
    for c in components:
        tier = tiers.get(c["tier"], {"label": c["tier"], "color": "gray"})
        tier_style = TIER_COLORS[tier["color"]]
        cat_style = category_color(c["category"] or "Uncategorized")
        url = c.get("url")
        repos = [u for u in [url, *c.get("supportingUrls", [])] if u]
        if repos:
            url_cell = '<div style="display:flex;flex-direction:column;gap:4px;">' + "".join(
                f'<a href="{esc(u)}" target="_blank" rel="noopener" style="font-size:0.86rem;">{esc(u)}</a>'
                for u in repos
            ) + '</div>'
        else:
            url_cell = '<span class="muted">—</span>'
        # data-* attrs drive JS filtering; layer is always Middleware
        rows_html.append(f'''<tr data-name="{esc(c["name"].lower())}" data-category="{esc(c["category"] or "Uncategorized")}" data-type="{esc(tier["label"])}">
          <td>{esc(c["name"])}</td>
          <td><span class="pill" style="background:{cat_style["bg"]};color:{cat_style["fg"]};border-radius:8px;line-height:1.5;">{esc(c["category"] or "Uncategorized")}</span></td>
          <td><span class="pill" style="background:{LAYER_STYLE["bg"]};color:{LAYER_STYLE["fg"]};border-radius:8px;line-height:1.5;">Middleware</span></td>
          <td><span class="pill" style="background:{tier_style["bg"]};color:{tier_style["fg"]}">{esc(tier["label"])}</span></td>
          <td>{url_cell}</td>
        </tr>''')

    # Dropdown options
    cat_options  = '<option value="">All categories</option>' + "".join(
        f'<option value="{esc(c)}">{esc(c)}</option>' for c in categories)
    type_options = '<option value="">All types</option>' + "".join(
        f'<option value="{esc(t)}">{esc(t)}</option>' for t in tier_labels)

    filter_bar = f"""
  <div class="comp-filter-bar">
    <input id="comp-search" type="text" placeholder="Search components" autocomplete="off">
    <select id="comp-cat">{cat_options}</select>
    <select id="comp-type">{type_options}</select>
    <span id="comp-count" class="comp-count"></span>
  </div>"""

    filter_css = """
<style>
  .comp-filter-bar {
    display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
    margin-bottom: 20px;
  }
  .comp-filter-bar input {
    padding: 9px 14px; border: 2px solid var(--border); border-radius: 8px;
    font-family: inherit; font-size: 0.9rem; min-width: 200px;
    transition: border-color 0.15s;
  }
  .comp-filter-bar input:focus { outline: none; border-color: var(--middleware); }
  .comp-filter-bar select {
    padding: 9px 32px 9px 14px; border: 2px solid var(--border); border-radius: 8px;
    font-family: inherit; font-size: 0.9rem; background: #fff;
    appearance: none; -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%235b6472' stroke-width='1.8' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: right 12px center;
    cursor: pointer; transition: border-color 0.15s;
  }
  .comp-filter-bar select:focus { outline: none; border-color: var(--middleware); }
  .comp-count { font-size: 0.84rem; color: var(--muted); margin-left: 4px; }
</style>"""

    filter_script = """
<script>
(function () {
  const searchEl = document.getElementById('comp-search');
  const catEl    = document.getElementById('comp-cat');
  const typeEl   = document.getElementById('comp-type');
  const countEl  = document.getElementById('comp-count');
  const rows     = Array.from(document.querySelectorAll('#comp-tbody tr'));

  function filter() {
    const q    = searchEl.value.trim().toLowerCase();
    const cat  = catEl.value;
    const type = typeEl.value;
    let visible = 0;
    rows.forEach(tr => {
      const show = (!q    || tr.dataset.name.includes(q))
                && (!cat  || tr.dataset.category === cat)
                && (!type || tr.dataset.type === type);
      tr.style.display = show ? '' : 'none';
      if (show) visible++;
    });
    countEl.textContent = visible + ' of ' + rows.length + ' components';
  }

  searchEl.addEventListener('input', filter);
  catEl.addEventListener('change', filter);
  typeEl.addEventListener('change', filter);
  filter();
})();
</script>"""

    lede = subtitle or "Every RDK-B component for this device profile — repo, category, layer, and type."
    return f'''
{render_hero("Core RDK Components", "RDK-B EthWAN WiFi Router Components", lede, compact=True, visual_key="components")}

{filter_css}

<section class="tight-top">
  <p style="color:var(--muted); font-size:0.85rem; margin:0 0 14px;">
    Schema version: {esc(schema_version)} &nbsp;|&nbsp; Generated: {esc(generated_at)}
  </p>
  <div style="margin-bottom:18px;">{legend_html}</div>
  {filter_bar}
  <table class="def-table">
    <thead><tr><th>Name</th><th>Category</th><th>Layer</th><th>Type</th><th>Repositories</th></tr></thead>
    <tbody id="comp-tbody">{"".join(rows_html)}</tbody>
  </table>
  <p style="margin-top:18px; font-size:0.86rem;">
    For the full interactive workbook view, see the <a href="{FULL_DETAILS_URL}">detailed version</a>.
  </p>
</section>
{filter_script}
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="ethwan-router-components.json")
    ap.add_argument("--out", default="index.html")
    args = ap.parse_args()

    data = json.loads(Path(args.json).read_text(encoding="utf-8"))
    body = build_body(data)
    head_extra = f"<title>{esc(data['title'])} — RDK-B Core Broadband</title>"
    html_out = render_page("components", head_extra, body, path_prefix="../")
    Path(args.out).write_text(html_out, encoding="utf-8")
    print(f"Wrote {args.out} ({len(data['components'])} components)")


if __name__ == "__main__":
    main()
