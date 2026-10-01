"""RDKE northbound API list generator."""
import json
from build import build_api
from import_apis import convert_excel_to_json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build_northbound() -> None:
    convert_excel_to_json(
        ROOT / "RDK8-northbound-api-spec.xlsx",
        ROOT / "northbound-apis.json",
        {
            "component": ("component", "service", "module", "modules"),
            "name": ("api", "api name", "interface", "methods"),
            "description": ("description", "details", "summary"),
            "reference": ("reference", "source", "url", "repo"),
            "type": ("type",),
            "releaseTag": ("release/tag version", "release", "tag", "version"),
        },
        optional_fields={"description", "reference", "type"},
    )
    json_path = ROOT / "northbound-apis.json"
    source = json.loads(json_path.read_text(encoding="utf-8"))
    source["status"] = "Published"
    source["version"] = "8.0.0"
    for api in source.get("apis", []):
        if not api.get("releaseTag") or api.get("releaseTag") == "???":
            api["releaseTag"] = "8.0.0"
    json_path.write_text(json.dumps(source, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    build_api(
        data_file="northbound-apis.json",
        output_file="northbound-api-spec.html",
        active="northbound",
        title="Northbound API Specifications",
        description="The RDK8 Northbound API Specifications provide a consistent app-facing layer for web and native applications to access RDK8 platform services through Firebolt.",
        columns=["Modules", "Version", "Methods"],
        fields=["component", "releaseTag", "name"],
        link_field=None,
        search_placeholder="Search Northbound APIs",
        empty_message="No Northbound APIs have been loaded.",
        sort_field="component",
        show_version=False,
        show_status_explainer=True,
        draft_note="Phase I - Core Defined: the first Firebolt API specification release is published for development preview and early validation of RDK8's standardized, versioned app API layer.",
    )

if __name__ == "__main__":
    build_northbound()
