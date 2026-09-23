# Copyright 2024 Comcast Cable Communications Management, LLC
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
#
# SPDX-License-Identifier: Apache-2.0

"""Generator for a simple stub hardware-compatibility.html for RDK8.

The page intentionally contains only the site navigation and Hardware
Compatibility hero. Detailed hardware compatibility content will be added
after the RDK8 build and validation data are ready.

``profiles_dir`` and ``repo_root`` args are retained so the existing build
command works unchanged:
    python3 gen_hwcompat_page.py --profiles-dir docs --repo-root . --out-dir .
"""
from __future__ import annotations

import argparse
from pathlib import Path

from layout import render_hero, render_page


def build_page(profiles_dir: Path, repo_root: Path | None = None) -> str:
    """Build the stub Hardware Compatibility page.

    profiles_dir and repo_root are retained for compatibility with
    existing build commands. They are not used until detailed RDK8 hardware
    compatibility information is published.
    """
    del profiles_dir, repo_root

    body = render_hero(
        "RDK8 Hardware Compatibility",
        "Hardware Compatibility Spec",
        (
            "Minimum CPU, RAM, flash, and required peripheral hardware per "
            "RDK-B device profile, validated against a BPI-R4 "
            "(MT7988/Filogic) reference platform."
        ),
        compact=True,
        visual_key="hwcompat",
    )
    head_extra = "<title>Hardware Compatibility Spec — RDK-B Core Broadband</title>"
    return render_page("hwcompat", head_extra, body)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles-dir", default="docs",
                    help="Reserved for future RDK8 hardware compatibility profile data")
    ap.add_argument("--repo-root", default=".",
                    help="Reserved for backward compatibility with existing invocations")
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()

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
