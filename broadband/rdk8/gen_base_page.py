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
    RDKM · © 2026 RDK Central. All rights reserved.
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
    body = f'''
<div class="page-main" style="display:flex; flex-direction:column; height:calc(100vh - 61px); overflow:hidden;">

<div class="hero" style="flex:1; display:flex; align-items:center; justify-content:center; padding:64px 40px;">
  <div class="hero-flex" style="justify-content:center;">
    <div class="hero-inner" style="text-align:center; max-width:none;">
      <h1 style="font-size:clamp(2.4rem,5vw,4rem);">CORE RDK for BROADBAND</h1>
    </div>
  </div>
</div>

</div>

{FOOTER}
'''
    return render_page("about", "<title>CORE RDK for BROADBAND</title>", body, script=TABS_SCRIPT)


# ---------- broadband split-screen home (../index.html) ----------
# RDK9 is "self" (links relative to rdk9/), RDK8 is "../rdk8/"

def build_broadband_home() -> str:
    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CORE RDK for Broadband</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700;800&family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  html, body {
    height: 100%; max-height: 100%;
    font-family: "Inter", -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    overflow: hidden !important;
    margin: 0; padding: 0;
  }

  /* ---- accent bar — in-flow inside .shell ---- */
  .accent-bar {
    height: 4px; width: 100%;
    background: linear-gradient(90deg,
      #29b6e8 0%, #29b6e8 25%,
      #7ac943 25%, #7ac943 50%,
      #f5a623 50%, #f5a623 75%,
      #f0653e 75%, #f0653e 100%
    );
  }

  /* ---- outer shell: accent bar (4px) + split panels + footer (30px) = 100vh exactly ---- */
  .shell {
    display: flex; flex-direction: column;
    height: 100vh; max-height: 100vh; overflow: hidden;
  }

  /* ---- split wrapper ---- */
  .split {
    display: flex;
    flex: 1 1 0; /* fills remaining height between accent bar and footer */
    min-height: 0;
  }

  /* ---- individual panels ---- */
  .panel {
    flex: 1 1 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 48px 48px 40px;
    position: relative;
    overflow: hidden;
    transition: flex 0.35s ease;
  }
  .panel:hover { flex: 1.06 1 50%; }

  /* RDK8 — dark/charcoal */
  .panel-rdk8 {
    background: #080d18;
    border-right: 1px solid rgba(255,255,255,0.06);
  }
  /* RDK9 — deep blue */
  .panel-rdk9 {
    background: linear-gradient(160deg, #0d1f40 0%, #0f2a5c 40%, #102070 100%);
  }

  /* subtle radial glow */
  .panel-rdk8::before {
    content: ""; position: absolute; inset: 0; pointer-events: none;
    background: radial-gradient(ellipse 80% 60% at 50% 60%, rgba(41,182,232,0.07) 0%, transparent 70%);
  }
  .panel-rdk9::before {
    content: ""; position: absolute; inset: 0; pointer-events: none;
    background: radial-gradient(ellipse 80% 60% at 50% 60%, rgba(41,182,232,0.18) 0%, transparent 70%);
  }

  /* divider line */
  .divider {
    width: 1px; background: rgba(255,255,255,0.08); flex: 0 0 1px; align-self: stretch;
    position: relative; z-index: 10;
  }

  /* ---- version badge ---- */
  .version-tag {
    display: inline-block;
    font-family: "Inter", sans-serif; font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase;
    padding: 5px 14px; border-radius: 999px; margin-bottom: 22px;
    position: relative; z-index: 1;
  }
  .panel-rdk8 .version-tag {
    background: rgba(255,255,255,0.07); color: #8cb4d6;
    border: 1px solid rgba(255,255,255,0.1);
  }
  .panel-rdk9 .version-tag {
    background: rgba(41,182,232,0.18); color: #5cd3f8;
    border: 1px solid rgba(41,182,232,0.3);
  }

  /* ---- heading ---- */
  .panel h1 {
    font-family: "Space Grotesk", "Inter", sans-serif;
    font-weight: 800; letter-spacing: -0.025em;
    font-size: clamp(1.6rem, 2.8vw, 2.6rem);
    line-height: 1.1; color: #fff;
    text-align: center; margin-bottom: 14px;
    position: relative; z-index: 1;
  }
  .panel-rdk8 h1 { color: #e8edf6; }
  .panel-rdk9 h1 { color: #fff; }

  /* ---- sub-label ---- */
  .panel .sub {
    font-size: 0.9rem; color: rgba(255,255,255,0.5); text-align: center;
    margin-bottom: 36px; max-width: 320px; line-height: 1.55;
    position: relative; z-index: 1;
  }

  /* ---- links list ---- */
  .links {
    list-style: none; width: 100%; max-width: 340px;
    display: flex; flex-direction: column; gap: 10px;
    position: relative; z-index: 1;
  }
  .links li a {
    display: flex; align-items: center; gap: 12px;
    padding: 13px 18px; border-radius: 10px;
    text-decoration: none; font-size: 0.88rem; font-weight: 600;
    transition: background 0.15s, transform 0.12s;
  }
  .links li a:hover { transform: translateX(3px); }

  .panel-rdk8 .links li a {
    background: rgba(255,255,255,0.04); color: #c8d8ee;
    border: 1px solid rgba(255,255,255,0.07);
  }
  .panel-rdk8 .links li a:hover {
    background: rgba(41,182,232,0.12); color: #fff;
    border-color: rgba(41,182,232,0.25);
  }

  .panel-rdk9 .links li a {
    background: rgba(255,255,255,0.06); color: #d4e8ff;
    border: 1px solid rgba(255,255,255,0.1);
  }
  .panel-rdk9 .links li a:hover {
    background: rgba(41,182,232,0.2); color: #fff;
    border-color: rgba(41,182,232,0.4);
  }

  .links li a .link-icon {
    flex: 0 0 32px; height: 32px; border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
  }
  .panel-rdk8 .links li a .link-icon { background: rgba(41,182,232,0.1); }
  .panel-rdk9 .links li a .link-icon { background: rgba(41,182,232,0.18); }

  .links li a .link-text { flex: 1 1 auto; min-width: 0; }
  .links li a .link-text strong { display: block; font-weight: 600; }
  .links li a .link-text span { display: block; font-size: 0.76rem; font-weight: 400; opacity: 0.55; margin-top: 1px; }

  .links li a .link-arrow { opacity: 0.35; font-size: 0.9rem; transition: opacity 0.12s; }
  .links li a:hover .link-arrow { opacity: 0.8; }

  /* ---- footer strip ---- */
  .footer-strip {
    flex: 0 0 auto;
    background: rgba(8,13,24,0.97);
    border-top: 1px solid rgba(255,255,255,0.07);
    padding: 8px 28px; text-align: center;
    font-size: 0.73rem; color: rgba(255,255,255,0.3);
  }

  /* ---- responsive: stack vertically on small screens ---- */
  @media (max-width: 680px) {
    html, body { overflow: auto !important; }
    .shell { height: auto; max-height: none; overflow: auto; }
    .split { flex-direction: column; flex: none; }
    .panel { padding: 56px 28px 48px; }
    .panel:hover { flex: 1 1 auto; }
    .divider { width: 100%; height: 1px; flex: 0 0 1px; align-self: auto; }
  }
</style>
</head>
<body>

<div class="shell">
<div class="accent-bar" style="position:relative;flex:0 0 4px;height:4px;"></div>

<div class="split">

  <!-- ===== RDK8 panel (dark) ===== -->
  <div class="panel panel-rdk8">
    <div class="version-tag">RDK8</div>
    <h1>CORE RDK<br>for BROADBAND</h1>
    <p class="sub">Stable release — EthWAN Router &amp; Gateway profiles</p>
    <ul class="links">
      <li>
        <a href="rdk8/">
          <span class="link-icon">🏠</span>
          <span class="link-text"><strong>Overview</strong><span>Platform architecture &amp; release notes</span></span>
          <span class="link-arrow">›</span>
        </a>
      </li>
      <li>
        <a href="rdk8/components/">
          <span class="link-icon">🧩</span>
          <span class="link-text"><strong>Components</strong><span>Required &amp; optional component profiles</span></span>
          <span class="link-arrow">›</span>
        </a>
      </li>
      <li>
        <a href="rdk8/north-bound-apis.html">
          <span class="link-icon">⬆️</span>
          <span class="link-text"><strong>North Bound APIs</strong><span>TR-181 &amp; management interfaces</span></span>
          <span class="link-arrow">›</span>
        </a>
      </li>
      <li>
        <a href="rdk8/south-bound-apis.html">
          <span class="link-icon">⬇️</span>
          <span class="link-text"><strong>South Bound APIs</strong><span>HAL interfaces &amp; device abstraction</span></span>
          <span class="link-arrow">›</span>
        </a>
      </li>
    </ul>
  </div>

  <div class="divider"></div>

  <!-- ===== RDK9 panel (blue) ===== -->
  <div class="panel panel-rdk9">
    <div class="version-tag">RDK9</div>
    <h1>CORE RDK<br>for BROADBAND</h1>
    <p class="sub">Latest release — EthWAN Router &amp; next-gen profiles</p>
    <ul class="links">
      <li>
        <a href="rdk9/">
          <span class="link-icon">🏠</span>
          <span class="link-text"><strong>Overview</strong><span>Platform architecture &amp; release notes</span></span>
          <span class="link-arrow">›</span>
        </a>
      </li>
      <li>
        <a href="rdk9/components/">
          <span class="link-icon">🧩</span>
          <span class="link-text"><strong>Components</strong><span>Required &amp; optional component profiles</span></span>
          <span class="link-arrow">›</span>
        </a>
      </li>
      <li>
        <a href="rdk9/north-bound-apis.html">
          <span class="link-icon">⬆️</span>
          <span class="link-text"><strong>North Bound APIs</strong><span>TR-181 &amp; management interfaces</span></span>
          <span class="link-arrow">›</span>
        </a>
      </li>
      <li>
        <a href="rdk9/south-bound-apis.html">
          <span class="link-icon">⬇️</span>
          <span class="link-text"><strong>South Bound APIs</strong><span>HAL interfaces &amp; device abstraction</span></span>
          <span class="link-arrow">›</span>
        </a>
      </li>
    </ul>
  </div>

</div>

<div class="footer-strip">RDKM · © 2026 RDK Central. All rights reserved.</div>
</div><!-- end .shell -->

</body>
</html>

'''


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

    # Also write the broadband split-screen home one level up
    broadband_dir = out_dir.parent
    broadband_dir.mkdir(parents=True, exist_ok=True)
    (broadband_dir / "index.html").write_text(build_broadband_home(), encoding="utf-8")
    print(f"Wrote {broadband_dir / 'index.html'}")


if __name__ == "__main__":
    main()
