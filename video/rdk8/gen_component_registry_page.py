"""RDKE Core RDK Components generator."""
import json
from pathlib import Path

from build import ROOT, esc, hero, load, release_panel, shell, status_explainer
from import_apis import convert_excel_to_json


COMPONENT_WORKBOOKS = (
    "RDK8-comonents-catalog-draft.xlsx",
    "RDK8-components-catalog.xlsx",
    "RDK8-comonents-catalog.xlsx",
    "RDK8-components.xlsx",
    "RDK8-component-spec.xlsx",
    "components.xlsx",
)


def find_component_workbook() -> Path | None:
    for filename in COMPONENT_WORKBOOKS:
        workbook = ROOT / filename
        if workbook.exists():
            return workbook
    return next((workbook for workbook in sorted(ROOT.glob("*.xlsx")) if "component" in workbook.stem.casefold()), None)


def load_component_source() -> dict:
    json_path = ROOT / "components.json"
    workbook = find_component_workbook()
    if workbook:
        convert_excel_to_json(
            workbook,
            json_path,
            {
                "name": ("name", "component", "components", "component name"),
                "category": ("category", "component category"),
                "layer": ("layer", "platform layer"),
                "type": ("version", "type"),
                "releaseTag": ("type", "release/tag version", "release", "tag"),
                "url": ("url", "source", "repository", "source repository"),
            },
            optional_fields={"type", "releaseTag", "url"},
            collection_key="components",
        )
    if not json_path.exists():
        raise FileNotFoundError("No component workbook or components.json is available")
    source = load("components.json")
    if workbook:
        for component in source.get("components", []):
            component["type"] = component.get("type") or "core"
            component["releaseTag"] = component.get("releaseTag") or "1.0.0"
        json_path.write_text(json.dumps(source, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return source


def build_components() -> None:
    source = load_component_source()
    records = sorted(source.get("components", []), key=lambda item: str(item.get("name", "")).casefold())
    data = [[item.get("name", ""), item.get("category", ""), item.get("layer", ""), item.get("releaseTag") or "1.0.0", item.get("type") or "core", item.get("url") if isinstance(item.get("url"), str) else (item.get("url") or [""])[0]] for item in records]
    categories = sorted({row[1] for row in data})
    layers = sorted({row[2] for row in data})
    body = hero("RDK8 RELEASE", "RDKE Components Catalog", "Explore the RDK8 Core Components Catalog, connecting application-facing capabilities with middleware and vendor-layer implementations.", include_release=False)
    body += f'''<style>.catalog-stats{{grid-template-columns:repeat(3,minmax(0,1fr))}}.api-controls{{display:flex;align-items:flex-start;gap:20px;flex-wrap:wrap}}.api-controls details[open]{{z-index:10}}.api-controls details[open] dl{{position:absolute!important;left:0!important;right:auto!important;top:calc(100% + 8px)!important;width:min(420px,calc(100vw - 40px))!important;margin:0!important}}.api-controls>.toolbar{{flex:1 1 560px;justify-self:auto;min-width:0}}.catalog-toolbar{{display:grid;grid-template-columns:minmax(220px,2fr) repeat(2,minmax(160px,1fr));gap:12px;margin:0}}.catalog-toolbar input,.catalog-toolbar select{{width:100%;min-width:0;margin:0}}@media(max-width:760px){{.catalog-stats,.catalog-toolbar{{grid-template-columns:1fr}}}}</style><section class="section"><div class="api-controls"><div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">{release_panel("RDK8 catalog state", source)}{status_explainer()}</div><div class="toolbar catalog-toolbar"><input id="search" type="search" placeholder="Search components" aria-label="Search components"><select id="category"><option value="">All categories</option>{''.join(f'<option>{esc(item)}</option>' for item in categories)}</select><select id="layer"><option value="">All layers</option>{''.join(f'<option>{esc(item)}</option>' for item in layers)}</select></div></div><div class="stats catalog-stats"><div class="stat"><strong>{len(data)}</strong><span>Components</span></div><div class="stat"><strong>{len(categories)}</strong><span>Categories</span></div><div class="stat"><strong>{len(layers)}</strong><span>Layers</span></div></div><div class="table-wrap"><table><thead><tr><th>Component</th><th>Category</th><th>Layer</th><th>Type</th><th>Version</th><th>Source</th></tr></thead><tbody id="rows"></tbody></table></div></section>'''
    rows = json.dumps(data, ensure_ascii=True)
    script = f'''<script>const DATA={rows};const esc=s=>{{const d=document.createElement('div');d.textContent=s;return d.innerHTML}};const search=document.querySelector('#search'),category=document.querySelector('#category'),layer=document.querySelector('#layer');function render(){{const q=search.value.toLowerCase();const rows=DATA.filter(c=>(!q||c.join(' ').toLowerCase().includes(q))&&(!category.value||c[1]===category.value)&&(!layer.value||c[2]===layer.value));document.querySelector('#rows').innerHTML=rows.length?rows.map(c=>`<tr><td>${{esc(c[0])}}</td><td><span class="pill">${{esc(c[1])}}</span></td><td>${{esc(c[2])}}</td><td>${{esc(c[3])}}</td><td><span class="pill ${{c[4].toLowerCase()==='core'?'core':''}}">${{esc(c[4])}}</span></td><td><a href="${{esc(String(c[5]).replace(/\\/releases\\/tag\\/[^/]+\\/?$/, ""))}}" target="_blank" rel="noopener">${{esc(String(c[5]).replace(/\\/releases\\/tag\\/[^/]+\\/?$/, ""))}}</a></td></tr>`).join(''):'<tr><td class="empty" colspan="6">No components match the current filters.</td></tr>'}}[search,category,layer].forEach(e=>e.addEventListener('input',render));render()</script>'''
    body = body.replace("<th>Type</th><th>Version</th>", "<th>Version</th><th>Type</th>")
    (ROOT / "component-catalog.html").write_text(shell("RDKE Components Catalog | RDK8", "components", body + script), encoding="utf-8")

if __name__ == "__main__":
    build_components()
