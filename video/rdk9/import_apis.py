"""Import Northbound and Southbound API workbooks into JSON."""
from __future__ import annotations

import argparse
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent

NAMESPACE = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "relationships": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

def _column_index(coordinate: str) -> int:
    index = 0
    for character in coordinate:
        if not character.isalpha():
            break
        index = index * 26 + ord(character.upper()) - ord("A") + 1
    return index - 1


def read_excel_rows(workbook_path: Path) -> list[list[str]]:
    """Read the first worksheet from an XLSX without external dependencies."""
    with zipfile.ZipFile(workbook_path) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared_strings = [
                "".join(node.text or "" for node in item.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"))
                for item in shared_root.findall("main:si", NAMESPACE)
            ]

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in relationships}
        sheet = workbook.find("main:sheets/main:sheet", NAMESPACE)
        if sheet is None:
            raise ValueError(f"{workbook_path.name} has no worksheets")
        relationship_id = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        worksheet_path = targets[relationship_id].lstrip("/")
        worksheet_path = worksheet_path if worksheet_path.startswith("xl/") else "xl/" + worksheet_path
        worksheet = ET.fromstring(archive.read(worksheet_path))

        rows = []
        for row in worksheet.findall(".//main:sheetData/main:row", NAMESPACE):
            values: dict[int, str] = {}
            for cell in row.findall("main:c", NAMESPACE):
                value = cell.find("main:v", NAMESPACE)
                raw = "" if value is None else value.text or ""
                if cell.attrib.get("t") == "inlineStr":
                    raw = "".join(node.text or "" for node in cell.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"))
                elif cell.attrib.get("t") == "s" and raw:
                    raw = shared_strings[int(raw)]
                values[_column_index(cell.attrib.get("r", "A1"))] = raw
            rows.append([values.get(index, "") for index in range(max(values, default=-1) + 1)])
    return rows


def convert_excel_to_json(
    workbook_path: Path,
    output_path: Path,
    field_mapping: dict[str, tuple[str, ...]],
    optional_fields: set[str] | None = None,
) -> int:
    """Convert any first-sheet XLSX table into a JSON ``apis`` array."""
    if not workbook_path.exists():
        return 0

    rows = read_excel_rows(workbook_path)
    if not rows:
        raise ValueError(f"{workbook_path.name} has no data rows")
    headers = [str(value).strip().lower() for value in rows[0]]
    positions = {}
    optional_fields = optional_fields or set()
    for field, field_aliases in field_mapping.items():
        position = next((headers.index(alias) for alias in field_aliases if alias in headers), None)
        if position is None and field not in optional_fields:
            raise ValueError(f"{workbook_path.name} is missing a column for {field}")
        positions[field] = position

    records = []
    for row in rows[1:]:
        record = {
            field: row[position].strip() if position is not None and position < len(row) and row[position] else ""
            for field, position in positions.items()
        }
        if any(record.values()):
            records.append(record)

    source = json.loads(output_path.read_text(encoding="utf-8"))
    source["apis"] = records
    output_path.write_text(json.dumps(source, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return len(records)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path, help="Input XLSX workbook")
    parser.add_argument("output", type=Path, help="Output JSON file")
    parser.add_argument(
        "--map",
        dest="mappings",
        action="append",
        required=True,
        metavar="JSON_FIELD=EXCEL_COLUMN",
        help="Map a JSON field to an Excel header; repeat for each field",
    )
    args = parser.parse_args()
    mapping = {}
    for value in args.mappings:
        field, separator, column = value.partition("=")
        if not separator or not field.strip() or not column.strip():
            parser.error(f"Invalid mapping {value!r}; expected JSON_FIELD=EXCEL_COLUMN")
        mapping[field.strip()] = (column.strip().lower(),)
    count = convert_excel_to_json(args.workbook, args.output, mapping)
    print(f"Imported {count} API records from {args.workbook.name}")


if __name__ == "__main__":
    main()
