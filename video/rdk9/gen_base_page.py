"""RDKE RDK9 home-page generator."""
from build import ROOT, cards, esc, hero, load, shell


def platform_metric_cards(items: list[list[str]], links: list[str], metrics: list[int]) -> str:
    return '<div class="grid">' + ''.join(
        f'<a class="card" style="display:block;text-decoration:none;color:inherit" href="{esc(links[index])}"><strong style="display:block;min-height:44px;font-size:2.4rem;color:#2457d6">{metrics[index]}</strong><h3>{esc(item[0])}</h3><p>{esc(item[1])}</p></a>'
        for index, item in enumerate(items)
    ) + '</div>'


def build_home() -> None:
    content = load("home-content.json")
    components = load("components.json")
    northbound = load("northbound-apis.json")
    southbound = load("southbound-apis.json")

    body = hero("", content["title"], content["description"], content["badges"])
    title_html = '<h1 style="font-size:clamp(1.9rem,3.6vw,3.5rem)">' + esc(content["title"]) + '</h1>'
    subtitle_html = '<div class="hero-subtitle" style="font-size:.95rem;font-weight:600;line-height:1;color:#b8df63;margin:0">Powering Next-Generation Entertainment Experiences</div>'
    intro_html = '<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px;line-height:1"><div style="display:inline-flex;align-items:center;padding:5px 12px;border:1px solid #b8df63;border-radius:999px;color:#b8df63;font:700 .72rem/1 JetBrains Mono,monospace;letter-spacing:.14em">RDKE</div><div style="font-size:.95rem;font-weight:600;line-height:1;color:#b8df63">RDK9 for Video</div>' + subtitle_html + '</div>'
    body = body.replace(title_html, intro_html + title_html, 1)

    why = content["why"]
    body += f'<section class="section"><div class="eyebrow">RDKE overview</div><h2>Why choose RDK-E?</h2><p class="lede">{esc(why["description"])}</p>{cards(why["cards"])}</section>'
    body += f'<section class="section alt"><div class="eyebrow">Architecture</div><h2>RDKE architecture</h2><div style="display:grid;gap:0;max-width:1000px">{"".join(f"<article class=\"card\" style=\"border-left-color:{color};border-radius:0\"><h3>{esc(layer[0])}</h3><p>{esc(layer[1])}</p></article>" for layer, color in zip(why["cards"][:3], ("#29b6e8", "#7ac943", "#f5a623")))}</div></section>'
    body += f'<section class="section alt"><div class="eyebrow">Upcoming Release</div><h2 style="font-family:Space Grotesk,Inter,sans-serif;letter-spacing:0">RDK9 release</h2><p class="lede">{esc(content["release_overview"])}</p></section>'

    links = ["component-registry.html", "northbound-apis.html", "southbound-apis.html"]
    metrics = [len(components.get("components", [])), len(northbound.get("apis", [])), len(southbound.get("apis", []))]
    body += f'<section class="section"><div class="eyebrow">Core RDK platform</div><h2>Explore the Core RDK platform</h2><p class="lede">Explore the RDK9 platform building blocks and standardized interfaces connecting applications, middleware, and the vendor layer.</p>{platform_metric_cards(content["architecture"]["cards"][:3], links, metrics)}</section>'

    footer = "Copyright © 2026 RDK Management, LLC"
    (ROOT / "index.html").write_text(shell("RDKE. Core RDK Entertainment Platform", "home", body, footer), encoding="utf-8")


if __name__ == "__main__":
    build_home()
