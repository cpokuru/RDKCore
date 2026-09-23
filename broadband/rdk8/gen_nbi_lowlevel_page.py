"""Generator for north-bound-lowlevel-apis.html (RDK8 stub).

Full Low Level API content (IPC matrix, rbus Doxygen, USP UDS links)
is available on the RDK9 site. This RDK8 page is intentionally empty —
just the hero, no content below it.

Usage:
    python3 gen_nbi_lowlevel_page.py --out-dir .
"""
from __future__ import annotations

import argparse
from pathlib import Path

from layout import render_hero, render_page


def build_page() -> str:
    body = render_hero(
        "North Bound APIs",
        "RDK8 List of North Bound Low Level APIs",
        "Low-level IPC interfaces (rbus, USP UDS) between RDK-B components and apps. "
        "Full content available on the RDK9 site.",
        compact=True,
        visual_key="nbi",
    )
    head_extra = "<title>North Bound Low Level APIs — RDK-B Core Broadband</title>"
    return render_page("nbi-lowlevel", head_extra, body)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate stub north-bound-lowlevel-apis.html")
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "north-bound-lowlevel-apis.html"
    path.write_text(build_page(), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
