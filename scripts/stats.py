"""Gera assets/stats.svg e assets/langs.svg com dados públicos da API do GitHub.
Roda pela GitHub Action (.github/workflows/stats.yml) todo dia e a cada push."""
import json, os, urllib.request
from collections import Counter

USER = os.environ.get("GH_USER", "limmuz")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
COR = {"bg": "#0B1F4B", "titulo": "#7DD3FC", "texto": "#DBEAFE", "icone": "#38BDF8", "borda": "#1D4ED8"}
CORES_LING = {"JavaScript": "#f1e05a", "Python": "#3572A5", "HTML": "#e34c26", "CSS": "#663399", "TypeScript": "#3178c6",
              "Java": "#b07219", "PHP": "#4F5D95", "C#": "#178600", "Shell": "#89e051", "Batchfile": "#C1F12E", "Jupyter Notebook": "#DA5B0B"}

def api(path, accept="application/vnd.github+json"):
    req = urllib.request.Request("https://api.github.com" + path, headers={"Accept": accept, "User-Agent": "stats-readme"})
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

repos = [r for r in api(f"/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
estrelas = sum(r["stargazers_count"] for r in repos)
ling = Counter()
for r in repos:
    if r["name"].lower() == USER.lower():
        continue
    for k, v in api(f"/repos/{USER}/{r['name']}/languages").items():
        ling[k] += v
def total(q, accept="application/vnd.github+json"):
    try:
        return api(q, accept)["total_count"]
    except Exception:
        return 0
commits = total(f"/search/commits?q=author:{USER}&per_page=1")
prs = total(f"/search/issues?q=author:{USER}+type:pr&per_page=1")
user = api(f"/users/{USER}")

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;")

linhas = [("Repositórios públicos", len(repos)), ("Commits", commits), ("Pull requests", prs),
          ("Linguagens usadas", len(ling))]
W, H = 440, 200
txt = "".join(f'<text x="30" y="{82 + i*28}" class="l">{esc(a)}</text><text x="{W-30}" y="{82 + i*28}" class="v" text-anchor="end">{b}</text>'
              for i, (a, b) in enumerate(linhas))
stats = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>.t{{font:600 18px 'Segoe UI',Helvetica,Arial,sans-serif;fill:{COR["titulo"]}}}.l{{font:400 14px 'Segoe UI',Helvetica,Arial,sans-serif;fill:{COR["texto"]}}}.v{{font:700 14px 'Segoe UI',Helvetica,Arial,sans-serif;fill:{COR["icone"]}}}</style>
<rect width="{W}" height="{H}" rx="8" fill="{COR["bg"]}"/><rect x="0" y="0" width="5" height="{H}" rx="2" fill="{COR["borda"]}"/>
<text x="30" y="40" class="t">Estatísticas no GitHub</text>{txt}</svg>'''

top = ling.most_common(6); soma = sum(v for _, v in top) or 1
x = 30; barra = ""; leg = ""
for i, (nome, v) in enumerate(top):
    w = (W - 60) * v / soma; cor = CORES_LING.get(nome, "#8b949e")
    barra += f'<rect x="{x:.1f}" y="62" width="{w:.1f}" height="10" fill="{cor}"/>'; x += w
    cx, cy = 30 + (i % 2) * 190, 102 + (i // 2) * 26
    leg += f'<circle cx="{cx+5}" cy="{cy-5}" r="5" fill="{cor}"/><text x="{cx+16}" y="{cy}" class="l">{esc(nome)} {100*v/soma:.1f}%</text>'
langs = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>.t{{font:600 18px 'Segoe UI',Helvetica,Arial,sans-serif;fill:{COR["titulo"]}}}.l{{font:400 13px 'Segoe UI',Helvetica,Arial,sans-serif;fill:{COR["texto"]}}}</style>
<rect width="{W}" height="{H}" rx="8" fill="{COR["bg"]}"/><rect x="0" y="0" width="5" height="{H}" rx="2" fill="{COR["borda"]}"/>
<text x="30" y="40" class="t">Linguagens mais usadas</text>
<clipPath id="b"><rect x="30" y="62" width="{W-60}" height="10" rx="5"/></clipPath><g clip-path="url(#b)">{barra}</g>{leg}</svg>'''

os.makedirs("assets", exist_ok=True)
open("assets/stats.svg", "w", encoding="utf-8").write(stats)
open("assets/langs.svg", "w", encoding="utf-8").write(langs)
print(linhas, top)
