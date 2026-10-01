"""RDKE northbound API list generator."""
import json
import re
from build import build_api
from import_apis import convert_excel_to_json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build_northbound() -> None:
    convert_excel_to_json(
        ROOT / "northbound-apis-rdk9-draft.xlsx",
        ROOT / "northbound-apis.json",
        {
            "component": ("component", "service", "module", "modules"),
            "name": ("api", "api name", "interface", "methods"),
            "description": ("description", "details", "summary"),
            "reference": ("reference", "source", "url", "repo"),
            "releaseTag": ("release/tag version", "release", "tag", "version", "api version"),
        },
        optional_fields={"description", "reference"},
    )
    json_path = ROOT / "northbound-apis.json"
    source = json.loads(json_path.read_text(encoding="utf-8"))
    normalized_apis = []
    for api in source.get("apis", []):
        for field in ("component", "name", "releaseTag"):
            api[field] = re.sub(r"\s+", " ", str(api.get(field, ""))).strip()
        api["name"] = re.sub(r"\s+(?=on[A-Z])", "\n", api["name"])
        if api["name"].startswith("on") and normalized_apis:
            normalized_apis[-1]["name"] = f'{normalized_apis[-1]["name"]}\n{api["name"]}'
        else:
            normalized_apis.append(api)
    source["apis"] = normalized_apis
    json_path.write_text(json.dumps(source, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    build_api(
        data_file="northbound-apis.json",
        output_file="northbound-apis.html",
        active="northbound",
        title="Northbound API Specifications",
        description="Standardized APIs the middleware exposes upward to the application layer, giving apps consistent access to device capabilities via Thunder and Firebolt.",
        columns=["Modules", "Version", "Methods"],
        fields=["component", "releaseTag", "name"],
        link_field=None,
        search_placeholder="Search Northbound APIs",
        empty_message="No Northbound APIs have been loaded.",
        sort_field="component",
        draft_note="This page contains an evolving list of Northbound API components. The current list is a draft and will continue to be updated.",
    )

if __name__ == "__main__":
    build_northbound()
