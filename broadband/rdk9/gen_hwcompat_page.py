"""Generate the Hardware Compatibility placeholder page.

The page intentionally contains only the site navigation and Hardware
Compatibility hero. Detailed hardware compatibility content will be added
after the RDK9 build and validation data are ready.

Usage:
    python3 gen_hwcompat_page.py --profiles-dir docs --out-dir .
"""
from __future__ import annotations

import argparse
from pathlib import Path

from layout import render_hero, render_page


def build_page(profiles_dir: Path, repo_root: Path | None = None) -> str:
    """Build the temporary Hardware Compatibility landing page.

    ``profiles_dir`` and ``repo_root`` are retained for compatibility with
    existing build commands. They are not used until detailed RDK9 hardware
    compatibility information is published.
    """
    del profiles_dir, repo_root

    body = render_hero(
        "Hardware Compatibility",
        "Hardware Compatibility Spec",
        (
            "Minimum CPU, RAM, flash, and required peripheral hardware per "
            "RDK-B device profile, validated against a BPI-R4 "
            "(MT7988/Filogic) reference platform."
        ),
        compact=True,
        visual_key="hwcompat",
    )

    head_extra = (
        "<title>Hardware Compatibility Spec — RDK-B Core Broadband</title>"
    )
    return render_page("hwcompat", head_extra, body)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profiles-dir",
        default="docs",
        help="Reserved for future RDK9 hardware compatibility profile data",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Reserved for backward compatibility with existing invocations",
    )
    parser.add_argument("--out-dir", default=".")
    args = parser.parse_args()

    output_dir = Path(args.out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "hardware-compatibility.html"
    output_path.write_text(
        build_page(Path(args.profiles_dir), Path(args.repo_root)),
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
