"""RDKE southbound API list generator."""
from build import build_api
from import_apis import convert_excel_to_json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build_southbound() -> None:
    convert_excel_to_json(
        ROOT / "Southbound-apis.xlsx",
        ROOT / "southbound-apis.json",
        {
            "halInterface": ("hal interface", "interface", "header", "api"),
            "version": ("version", "release", "tag", "release/tag version"),
            "source": ("source", "reference", "url"),
        },
    )
    build_api(
        data_file="southbound-apis.json",
        output_file="southbound-apis.html",
        active="southbound",
        title="Southbound API Specifications",
        description="The Hardware Abstraction Layer (HAL) between middleware and the vendor layer — standardized interfaces that abstract hardware differences.",
        columns=["HAL interface", "Version", "Source"],
        fields=["halInterface", "version", "source"],
        link_field="source",
        search_placeholder="Search Southbound APIs",
        empty_message="No Southbound APIs have been loaded.",
        sort_field="halInterface",
        draft_note="This page contains an evolving list of Southbound API components. The current list is a draft and will continue to be updated.",
    )

if __name__ == "__main__":
    build_southbound()
