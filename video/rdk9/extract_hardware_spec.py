"""Extract readable text and tables from an RDKE hardware specification PDF.

Usage:
    python extract_hardware_spec.py hardware-spec.pdf
    python extract_hardware_spec.py hardware-spec.pdf --output hardware-spec.json

Requires the pdfplumber package: python -m pip install pdfplumber
Also requires the `pdftotext` command to be available on PATH.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def clean(value: object) -> str:
    text = "" if value is None else str(value)
    text = re.sub(r"\s+", " ", text.replace("\u00ad", "")).strip()
    return text


def pdftotext(pdf_path: Path, page_number: int) -> str:
    result = subprocess.run(
        [
            "pdftotext",
            "-layout",
            "-f",
            str(page_number),
            "-l",
            str(page_number),
            str(pdf_path),
            "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def extract(pdf_path: Path) -> dict:
    try:
        import pdfplumber
    except ImportError as exc:
        raise SystemExit(
            "pdfplumber is required. Install it with: python -m pip install pdfplumber"
        ) from exc

    sections = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = pdftotext(pdf_path, page_number)
            lines = [clean(line) for line in text.splitlines() if clean(line)]
            tables = []
            for table in page.extract_tables() or []:
                rows = [[clean(cell) for cell in row] for row in table if row]
                rows = [row for row in rows if any(row)]
                if rows:
                    tables.append(rows)
            if lines or tables:
                sections.append({
                    "page": page_number,
                    "text": lines,
                    "tables": tables,
                })

    return {
        "schemaVersion": "1.0",
        "sourcePdf": pdf_path.name,
        "status": "extracted",
        "pageCount": len(sections),
        "profiles": [],
        "sections": sections,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path, default=Path("hardware-spec.json"))
    args = parser.parse_args()
    if not args.pdf.exists():
        raise SystemExit(f"PDF not found: {args.pdf}")
    payload = extract(args.pdf)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"Extracted {payload['pageCount']} pages from {args.pdf} to {args.output}")


if __name__ == "__main__":
    main()
