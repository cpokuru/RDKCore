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

"""Render index.html (About Core RDK Broadband) for CoreRDK-Broadband-Specification.

Two source files, two different sections of the same page:

  - docs/about-content.json  -> the About section (definition, goals/challenges,
    RDK Ready program, benefits). Hand-curated from the Core RDK Broadband
    deck (a slide layout, not a structured doc, so — like FIVE_TIER below —
    it isn't a good fit for automatic extraction). Update this file by hand
    when the deck changes.

  - docs/spec-content.json   -> the Architecture section (five-tier model,
    production/vendor-test layering, test suite ownership). Unchanged from
    before — still produced by extract_spec_content.py from the spec PDF.

architecture-standards.html and technical-governance.html are separate,
empty static stub pages (see gen_stub_pages.py) — not touched by this script.

Usage:
    python3 gen_base_page.py docs/spec-content.json docs/about-content.json --out-dir .
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from layout import esc, render_hero, render_page, render_quicklinks, render_tabs, TABS_SCRIPT, ICONS

COMPONENTS_URL = "components/"
COMPONENTS_FULL_URL = "components/full-list.html"
SPEC_WIKI_URL = "https://wiki.rdkcentral.com/spaces/RDK/pages/498925914/RDK9+Core+RDK+Broadband+Specification+Approved+by+TAB"

FOOTER = """
<footer>
  <div class="footer-links">
    <a href="{components_url}">Components — profiles<span>Required / optional components per device profile</span></a>
    <a href="{components_full_url}">Components — full workbook<span>Interactive component list, all profiles</span></a>
    <a href="{spec_wiki_url}">RDK9 Core RDK Broadband Spec<span>TAB-approved specification (wiki)</span></a>
    <a href="https://github.com/rdkcentral">rdkcentral on GitHub<span>Component source repositories</span></a>
  </div>
  <div class="footer-meta">
    RDKM · © 2026 RDK Central. All rights reserved. Generated from {source_pdf}.
  </div>
</footer>
""".format(components_url=COMPONENTS_URL, components_full_url=COMPONENTS_FULL_URL,
           spec_wiki_url=SPEC_WIKI_URL, source_pdf="{source_pdf}")


# ---------- About section renderers (from about-content.json) ----------

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def render_goals(goals: list[dict]) -> str:
    out = []
    for g in goals:
        anchor = slugify(g["title"])
        out.append(f'''
    <div class="card" id="{anchor}" style="margin-bottom:16px; scroll-margin-top:140px;">
      <h3>{esc(g["title"])}</h3>
      <p><strong style="color:var(--ink);">Goal —</strong> {esc(g["goal"])}</p>
      <p style="margin-bottom:0;"><strong style="color:var(--amber-fg);">Challenge —</strong> {esc(g["challenge"])}</p>
    </div>''')
    return "\n".join(out)


def render_rdk_ready(items: list[dict]) -> str:
    out = []
    for it in items:
        out.append(f'''
    <div class="card">
      <h3>{esc(it["title"])}</h3>
      <p style="margin-bottom:0;">{esc(it["body"])}</p>
    </div>''')
    return f'<div class="two-col">{"".join(out)}</div>'


def render_benefits(groups: list[dict]) -> str:
    cols = []
    for g in groups:
        items_html = "".join(f'<li>{esc(i)}</li>' for i in g["items"])
        cols.append(f'''
    <div class="card" style="height:100%; box-sizing:border-box;">
      <h3>{esc(g["category"])}</h3>
      <ul style="margin:0; padding-left:18px; font-size:0.92rem; color:var(--muted);">{items_html}</ul>
    </div>''')
    return f'<div style="display:flex; gap:20px; flex-wrap:wrap; align-items:stretch;">' + \
        "".join(f'<div style="flex:1; min-width:220px;">{c}</div>' for c in cols) + '</div>'


# ---------- Architecture section renderers (from spec-content.json, unchanged) ----------

def render_five_tier(tiers: list[dict]) -> str:
    out = []
    for t in sorted(tiers, key=lambda x: -x["tier"]):
        if "split" in t:
            cols = "".join(
                f'<div class="split-col"><h4>{esc(c["title"])}</h4><p>{esc(c["text"])}</p></div>'
                for c in t["split"]
            )
            body = f'<div class="body body-split">{cols}</div>'
        else:
            body = f'<div class="body"><h4>{esc(t["layer"])}</h4><p>{esc(t["description"])}</p></div>'
        out.append(f'''
    <div class="tier t{t["tier"]}">
      <div class="num">{t["tier"]}</div>
      {body}
    </div>''')
    return "\n".join(out)


def render_test_suites(rows: list[dict]) -> str:
    out = []
    for r in rows:
        out.append(f'<tr><td class="mono">{esc(r["name"])}</td><td>{esc(r["definition"])}</td><td>{esc(r["owner"])}</td></tr>')
    return "\n".join(out)


# ---------- page: About Core RDK Broadband ----------

def build_about_page(spec: dict, about: dict) -> str:
    body = '''
<div class="hero" style="padding:64px 40px 48px;">
  <div class="hero-flex">
    <div class="hero-inner">
      <h1>CORE RDK for BROADBAND</h1>
    </div>
  </div>
</div>

<footer>
  <div class="footer-meta" style="border-top:none; padding-top:0;">
    RDKM &middot; &copy; 2026 RDK Central. All rights reserved.
  </div>
</footer>
'''
    return render_page("about", "<title>CORE RDK for BROADBAND</title>", body, script=TABS_SCRIPT)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec_json", help="spec-content.json (drives the Architecture section)")
    ap.add_argument("about_json", help="about-content.json (drives the About section)")
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()

    spec = json.loads(Path(args.spec_json).read_text(encoding="utf-8"))
    about = json.loads(Path(args.about_json).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "index.html").write_text(build_about_page(spec, about), encoding="utf-8")
    print(f"Wrote {out_dir / 'index.html'}")


if __name__ == "__main__":
    main()
