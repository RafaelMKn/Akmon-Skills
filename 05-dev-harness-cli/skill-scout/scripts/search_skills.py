#!/usr/bin/env python3
"""skill-scout: procura, instala e gerencia skills de agente.

Só biblioteca padrão, Python 3.10 ou superior. Não lê credenciais: o acesso ao GitHub
usa o GitHub CLI (`gh`) já autenticado pelo usuário ou, sem ele, a API pública sem token.
Nada que é baixado é executado.
"""
import sys

if sys.version_info < (3, 10):
    sys.exit("skill-scout exige Python 3.10 ou superior.")

import argparse
import datetime
import difflib
import json
import os
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

AUTO_UPDATE_DAYS = 7
INSTALL_DIR = Path.home() / ".skills"
REFERENCES_DIR = Path(__file__).resolve().parent.parent / "references"
ALLOWED_HOSTS = frozenset({"github.com", "raw.githubusercontent.com", "gist.github.com"})
SOURCE_TYPES = ("official", "awesome-list", "community")
DESCRIPTION_MAX = 100
REQUEST_DELAY = 0.3
MAX_FILES = 200
MAX_BYTES = 10 * 1024 * 1024
MAX_DEPTH = 6
DEFAULT_CATEGORY = "geral"
EXIT_OK, EXIT_ERROR, EXIT_APPROVAL = 0, 1, 3

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REPO_URL_RE = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$")


class ScoutError(Exception):
    """Erro esperado, com mensagem pronta para o usuário."""


# ---------------------------------------------------------------- arquivos JSON

def load_json(path: Path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ScoutError(f"Arquivo não encontrado: {path}")
    except (OSError, ValueError) as exc:
        raise ScoutError(f"Não foi possível ler {path}: {exc}")


def save_json(path: Path, data) -> None:
    """Grava de forma atômica (arquivo temporário + rename)."""
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def today() -> str:
    return datetime.date.today().isoformat()


def empty_index() -> dict:
    return {
        "version": "1.0.0",
        "lastUpdated": today(),
        "categories": [{"id": DEFAULT_CATEGORY, "name": "Geral", "description": "Skills sem categoria definida"}],
        "sources": [],
        "skills": [],
    }


# ---------------------------------------------------------------- validação do índice

def _check_keys(obj, required, optional, label, errors):
    if not isinstance(obj, dict):
        errors.append(f"{label}: deve ser um objeto")
        return False
    for key in required:
        if key not in obj:
            errors.append(f"{label}: falta o campo obrigatório '{key}'")
    for key in obj:
        if key not in required and key not in optional:
            errors.append(f"{label}: campo não permitido '{key}'")
    return True


def validate_index(data) -> list:
    """Devolve a lista de problemas (vazia = índice válido). Espelha references/skill-index.schema.json."""
    errors: list = []
    if not _check_keys(data, ("version", "lastUpdated", "sources", "skills"), ("categories", "$schema"), "índice", errors):
        return errors
    if not (isinstance(data.get("version"), str) and SEMVER_RE.match(data["version"])):
        errors.append("índice: 'version' deve ser semver X.Y.Z")
    if not (isinstance(data.get("lastUpdated"), str) and DATE_RE.match(data["lastUpdated"])):
        errors.append("índice: 'lastUpdated' deve ser AAAA-MM-DD")
    for key in ("sources", "skills", "categories"):
        if key in data and not isinstance(data[key], list):
            errors.append(f"índice: '{key}' deve ser uma lista")
    sources, skills, categories = (data.get(k) if isinstance(data.get(k), list) else [] for k in ("sources", "skills", "categories"))
    source_ids = set()
    for i, s in enumerate(sources):
        label = f"sources[{i}]"
        if not _check_keys(s, ("id", "name", "owner", "url", "type", "description"), (), label, errors):
            continue
        if not (isinstance(s.get("id"), str) and NAME_RE.match(s["id"])):
            errors.append(f"{label}: 'id' deve usar minúsculas, números e hífen")
        else:
            source_ids.add(s["id"])
        if not (isinstance(s.get("url"), str) and s["url"].startswith("https://github.com/")):
            errors.append(f"{label}: 'url' deve começar com https://github.com/")
        if s.get("type") not in SOURCE_TYPES:
            errors.append(f"{label}: 'type' deve ser um de {', '.join(SOURCE_TYPES)}")
        for key in ("name", "owner", "description"):
            if key in s and not isinstance(s[key], str):
                errors.append(f"{label}: '{key}' deve ser texto")
    for i, c in enumerate(categories):
        label = f"categories[{i}]"
        if _check_keys(c, ("id", "name", "description"), (), label, errors):
            for key in ("id", "name", "description"):
                if not isinstance(c.get(key), str):
                    errors.append(f"{label}: '{key}' deve ser texto")
    for i, k in enumerate(skills):
        label = f"skills[{i}]"
        if not _check_keys(k, ("name", "source", "path", "categories", "description"), (), label, errors):
            continue
        if not (isinstance(k.get("name"), str) and NAME_RE.match(k["name"])):
            errors.append(f"{label}: 'name' deve usar minúsculas, números e hífen")
        if k.get("source") not in source_ids:
            errors.append(f"{label}: 'source' não corresponde a nenhuma fonte")
        for key in ("path", "description"):
            if not isinstance(k.get(key), str):
                errors.append(f"{label}: '{key}' deve ser texto")
        cats = k.get("categories")
        if not (isinstance(cats, list) and cats and all(isinstance(x, str) for x in cats)):
            errors.append(f"{label}: 'categories' deve ser uma lista não vazia de textos")
    return errors


def load_index(references_dir: Path) -> dict:
    index = load_json(Path(references_dir) / "skill-index.json")
    problems = validate_index(index)
    if problems:
        raise ScoutError("Índice inválido:\n  - " + "\n  - ".join(problems[:10]))
    return index


def index_age_days(index: dict) -> int:
    return (datetime.date.today() - datetime.date.fromisoformat(index["lastUpdated"])).days


# ---------------------------------------------------------------- texto

def shorten(text: str, limit: int = DESCRIPTION_MAX) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def frontmatter_field(text: str, key: str) -> str:
    """Lê um campo de primeiro nível do frontmatter (texto simples, entre aspas ou em bloco > e |)."""
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), len(lines))
    fm = lines[1:end]
    for i, line in enumerate(fm):
        m = re.match(rf"^{re.escape(key)}\s*:\s*(.*)$", line)
        if not m:
            continue
        value = m.group(1).strip()
        following = []
        for nxt in fm[i + 1:]:
            if nxt.strip() == "":
                following.append("")
            elif nxt[:1].isspace():
                following.append(nxt.strip())
            else:
                break
        if value[:1] in (">", "|"):
            return " ".join(x for x in following if x)
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            inner = value[1:-1]
            return inner.replace('\\"', '"').replace("\\\\", "\\") if value[0] == '"' else inner.replace("''", "'")
        return " ".join([value] + [x for x in following if x])
    return ""


def readme_summary(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith(("#", "!", "<", "[", "|", "---")):
            return line
    return ""


def description_from(skill_md: str, readme: str = "") -> str:
    desc = frontmatter_field(skill_md, "description") or readme_summary(readme)
    return shorten(desc)


# ---------------------------------------------------------------- GitHub

class GitHub:
    """Acesso mínimo ao GitHub. Prefere `gh` (autenticação dele); sem `gh`, API pública sem token."""

    def __init__(self, runner=subprocess.run, opener=urllib.request.urlopen, which=shutil.which):
        self.runner, self.opener, self.which = runner, opener, which

    @property
    def has_gh(self) -> bool:
        return self.which("gh") is not None

    def _get(self, endpoint: str, raw: bool = False) -> bytes:
        if self.has_gh:
            cmd = ["gh", "api"] + (["-H", "Accept: application/vnd.github.raw"] if raw else []) + [endpoint]
            try:
                proc = self.runner(cmd, capture_output=True, timeout=60)
            except (OSError, subprocess.SubprocessError) as exc:
                raise ScoutError(f"Falha ao chamar o gh: {exc}")
            if proc.returncode != 0:
                msg = (proc.stderr or b"").decode("utf-8", "replace").strip().splitlines()[:1]
                raise ScoutError(f"GitHub recusou a consulta ({endpoint.split('?')[0]}): {msg[0] if msg else 'erro'}")
            return proc.stdout
        req = urllib.request.Request(
            "https://api.github.com/" + endpoint,
            headers={"User-Agent": "skill-scout", "Accept": "application/vnd.github.raw" if raw else "application/vnd.github+json"},
        )
        try:
            with self.opener(req, timeout=30) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            hint = " (limite de requisições; use gh autenticado)" if exc.code in (403, 429) else ""
            raise ScoutError(f"GitHub respondeu HTTP {exc.code}{hint}")
        except (urllib.error.URLError, OSError) as exc:
            raise ScoutError(f"Falha de rede ao consultar o GitHub: {exc}")

    def api_json(self, endpoint: str):
        try:
            return json.loads(self._get(endpoint))
        except ValueError:
            raise ScoutError("Resposta inesperada do GitHub")

    def list_dir(self, owner: str, repo: str, path: str = "") -> list:
        quoted = urllib.parse.quote(path.strip("/"))
        data = self.api_json(f"repos/{owner}/{repo}/contents/{quoted}".rstrip("/"))
        if not isinstance(data, list):
            raise ScoutError(f"{owner}/{repo}/{path} não é uma pasta")
        return data

    def read_file(self, owner: str, repo: str, path: str) -> bytes:
        return self._get(f"repos/{owner}/{repo}/contents/{urllib.parse.quote(path.strip('/'))}", raw=True)

    def search_code(self, query: str, limit: int = 30) -> list:
        if not self.has_gh:
            raise ScoutError("A busca de código do GitHub exige o gh instalado e autenticado.")
        data = self.api_json(f"search/code?q={urllib.parse.quote(query)}&per_page={limit}")
        return [{"repo": i["repository"]["full_name"], "path": i["path"]} for i in data.get("items", [])]

    def search_repos(self, query: str, limit: int = 10) -> list:
        data = self.api_json(f"search/repositories?q={urllib.parse.quote(query)}&sort=stars&per_page={limit}")
        return [{"nameWithOwner": i["full_name"], "description": i.get("description") or "", "stargazersCount": i.get("stargazers_count", 0)}
                for i in data.get("items", [])]


# ---------------------------------------------------------------- busca e consulta

def skill_key(skill: dict) -> str:
    return f"{skill['source']}/{skill['name']}"


def search_index(index: dict, query: str = "", category: str | None = None, source: str | None = None, starred=()) -> list:
    words = query.split()
    terms = [w.lower() for w in words if not w.startswith("#")]
    tags = [w[1:].lower() for w in words if w.startswith("#") and len(w) > 1]
    found = []
    for skill in index["skills"]:
        cats = [c.lower() for c in skill["categories"]]
        if source and skill["source"] != source:
            continue
        if category and category.lower() not in cats:
            continue
        if tags and not all(t in cats for t in tags):
            continue
        hay = f"{skill['name']} {skill['description']}".lower()
        if not all(t in hay for t in terms):
            continue
        found.append(skill)
    starred = set(starred)
    return sorted(found, key=lambda s: (skill_key(s) not in starred, s["name"].lower(), s["source"]))


def find_skill(index: dict, name: str) -> dict:
    """Aceita `nome` ou `fonte/nome`."""
    name = name.strip().lower()
    matches = [s for s in index["skills"] if name in (s["name"], skill_key(s))]
    if not matches:
        raise ScoutError(f"Skill '{name}' não está no índice. Tente a busca ou --update.")
    if len(matches) > 1:
        raise ScoutError("Nome ambíguo; use fonte/nome: " + ", ".join(skill_key(s) for s in matches))
    return matches[0]


def source_of(index: dict, skill: dict) -> dict:
    return next(s for s in index["sources"] if s["id"] == skill["source"])


def similar_skills(index: dict, name: str, limit: int = 5) -> list:
    others = index["skills"]
    try:
        base = find_skill(index, name)
    except ScoutError as exc:
        if "ambíguo" in str(exc):
            raise
        names = sorted({s["name"] for s in others})
        close = difflib.get_close_matches(name.lower(), names, n=limit, cutoff=0.0)
        return [s for n in close for s in others if s["name"] == n][:limit]
    cats = set(base["categories"])
    scored = [(len(cats & set(s["categories"])), s) for s in others if s is not base]
    scored = [(n, s) for n, s in scored if n > 0]
    scored.sort(key=lambda t: (-t[0], t[1]["name"]))
    return [s for _, s in scored[:limit]]


def web_search_links(query: str) -> list:
    q = urllib.parse.quote_plus(f"{query} SKILL.md")
    return [("Google", f"https://www.google.com/search?q={q}"), ("Bing", f"https://www.bing.com/search?q={q}"),
            ("DuckDuckGo", f"https://duckduckgo.com/?q={q}")]


def recommend(results: list, index: dict, query: str):
    """Critérios na ordem: fonte oficial, relevância para o termo (no nome). Riqueza e atualização não constam do índice."""
    if len(results) < 3:
        return None
    terms = [t.lower() for t in query.split() if not t.startswith("#")]
    rank = {"official": 0, "awesome-list": 1, "community": 2}

    def score(s):
        src = source_of(index, s)
        return (rank[src["type"]], 0 if any(t in s["name"] for t in terms) else 1, s["name"])

    best = min(results, key=score)
    src = source_of(index, best)
    reasons = []
    if src["type"] == "official":
        reasons.append("fonte oficial")
    if any(t in best["name"] for t in terms):
        reasons.append("o nome combina com a busca")
    return best, ", ".join(reasons) or "primeira na ordem de relevância (índice não traz dados de uso nem de atualização)"


# ---------------------------------------------------------------- favoritos

def load_starred(references_dir: Path) -> dict:
    path = Path(references_dir) / "starred-skills.json"
    if not path.exists():
        return {"starred": [], "lastUpdated": today()}
    data = load_json(path)
    if not (isinstance(data, dict) and isinstance(data.get("starred"), list)):
        raise ScoutError("starred-skills.json inválido")
    return data


def set_star(references_dir: Path, index: dict, name: str, on: bool) -> str:
    key = skill_key(find_skill(index, name))
    data = load_starred(references_dir)
    starred = [k for k in data["starred"] if k != key]
    if on:
        starred.append(key)
    data.update(starred=sorted(starred), lastUpdated=today())
    save_json(Path(references_dir) / "starred-skills.json", data)
    return key


# ---------------------------------------------------------------- instalação

def parse_repo_url(url: str) -> tuple:
    m = REPO_URL_RE.match(url or "")
    if not m:
        raise ScoutError(f"URL de repositório inválida (esperado https://github.com/dono/repo): {url}")
    return m.group(1), m.group(2)


def check_host(url: str, extra_hosts=()) -> str:
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    if host not in ALLOWED_HOSTS and host not in {h.lower() for h in extra_hosts}:
        raise ScoutError(f"Host '{host}' não está na lista padrão ({', '.join(sorted(ALLOWED_HOSTS))}). Exige aprovação específica (--allow-host).")
    return host


def safe_relative(path: str) -> str:
    """Caminho do índice: relativo, sem '..', sem barra invertida."""
    if not path or path.startswith("/") or "\\" in path or "\0" in path or any(p in ("", ".", "..") for p in path.split("/")):
        raise ScoutError(f"Caminho de skill inseguro no índice: {path!r}")
    return path


def safe_name(name: str) -> str:
    if name in ("", ".", "..") or "/" in name or "\\" in name or "\0" in name:
        raise ScoutError(f"Nome de arquivo inseguro vindo do GitHub: {name!r}")
    return name


def plan_install(index: dict, name: str, client: GitHub, extra_hosts=()) -> dict:
    skill = find_skill(index, name)
    src = source_of(index, skill)
    owner, repo = parse_repo_url(src["url"])
    check_host(src["url"], extra_hosts)
    path = safe_relative(skill["path"])
    requires = ""
    try:
        requires = frontmatter_field(client.read_file(owner, repo, f"{path}/SKILL.md").decode("utf-8", "replace"), "allowed-tools")
    except ScoutError:
        requires = ""
    return {"skill": skill, "source": src, "owner": owner, "repo": repo, "path": path,
            "url": f"{src['url'].rstrip('/')}/tree/HEAD/{path}", "host": "github.com", "requires": requires}


def _download_tree(client, owner, repo, remote, local: Path, state, depth=0):
    if depth > MAX_DEPTH:
        raise ScoutError("Pasta da skill excede a profundidade máxima permitida")
    local.mkdir(mode=0o755, parents=True, exist_ok=True)
    for entry in client.list_dir(owner, repo, remote):
        name = safe_name(str(entry.get("name", "")))
        kind = entry.get("type")
        if kind == "dir":
            _download_tree(client, owner, repo, f"{remote}/{name}", local / name, state, depth + 1)
        elif kind == "file":
            state["files"] += 1
            state["bytes"] += int(entry.get("size") or 0)
            if state["files"] > MAX_FILES or state["bytes"] > MAX_BYTES:
                raise ScoutError("A skill excede o limite de arquivos ou de tamanho para instalação")
            data = client.read_file(owner, repo, f"{remote}/{name}")
            target = local / name
            target.write_bytes(data)
            os.chmod(target, 0o644)  # nunca executável: nada baixado é executado
        # symlinks e submódulos são ignorados


def install_skill(plan: dict, client: GitHub, install_dir: Path) -> Path:
    install_dir = Path(install_dir).expanduser()
    final = install_dir / plan["skill"]["name"]
    if final.exists():
        raise ScoutError(f"{final} já existe; nada foi alterado. Remova a pasta se quiser reinstalar.")
    install_dir.mkdir(mode=0o755, parents=True, exist_ok=True)
    tmp = install_dir / f".tmp-{plan['skill']['name']}-{os.getpid()}"
    shutil.rmtree(tmp, ignore_errors=True)
    try:
        _download_tree(client, plan["owner"], plan["repo"], plan["path"], tmp, {"files": 0, "bytes": 0})
        if not (tmp / "SKILL.md").is_file():
            raise ScoutError("A pasta baixada não contém SKILL.md; instalação cancelada")
        os.replace(tmp, final)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return final


# ---------------------------------------------------------------- atualização do índice

def _is_skill_dir(client, owner, repo, path) -> bool:
    try:
        return any(e.get("type") == "file" and e.get("name") == "SKILL.md" for e in client.list_dir(owner, repo, path))
    except ScoutError:
        return False


def discover_skill_dirs(client, source: dict, sleep=time.sleep) -> list:
    """Três tentativas, nesta ordem: busca de código no repositório; pasta skills/; subpastas da raiz."""
    owner, repo = parse_repo_url(source["url"])
    try:
        hits = client.search_code(f"filename:SKILL.md repo:{owner}/{repo}")
        paths = sorted({h["path"].rsplit("/", 1)[0] for h in hits if h["path"].endswith("/SKILL.md")})
        if paths:
            return paths
    except ScoutError:
        pass
    sleep(REQUEST_DELAY)
    for base in ("skills", ""):
        try:
            entries = client.list_dir(owner, repo, base)
        except ScoutError:
            continue
        found = []
        for e in entries:
            if e.get("type") == "dir" and not str(e.get("name", "")).startswith("."):
                path = f"{base}/{e['name']}".lstrip("/")
                sleep(REQUEST_DELAY)
                if _is_skill_dir(client, owner, repo, path):
                    found.append(path)
        if found:
            return found
    return []


def update_index(index: dict, client, only_source: str | None = None, sleep=time.sleep) -> tuple:
    """Atualiza o índice a partir das fontes. Falha numa fonte não interrompe as outras."""
    failures = []
    by_key = {skill_key(s): s for s in index["skills"]}
    for src in index["sources"]:
        if only_source and src["id"] != only_source:
            continue
        try:
            owner, repo = parse_repo_url(src["url"])
            paths = discover_skill_dirs(client, src, sleep)
        except ScoutError as exc:
            failures.append(f"{src['id']}: {exc}")
            continue
        if not paths:
            failures.append(f"{src['id']}: nenhuma skill encontrada")
            continue
        for path in sorted(paths, key=lambda p: (p.count("/"), p)):
            name = path.rsplit("/", 1)[-1].lower()
            if not NAME_RE.match(name):
                continue
            key = f"{src['id']}/{name}"
            current = by_key.get(key)
            if current and current["description"] and not current["description"].endswith(" skill"):
                continue  # só entradas novas, sem descrição ou terminando em " skill" são atualizadas
            sleep(REQUEST_DELAY)
            try:
                text = client.read_file(owner, repo, f"{path}/SKILL.md").decode("utf-8", "replace")
                readme = ""
                if not frontmatter_field(text, "description"):
                    try:
                        readme = client.read_file(owner, repo, f"{path}/README.md").decode("utf-8", "replace")
                    except ScoutError:
                        pass
                description = description_from(text, readme)
            except ScoutError as exc:
                failures.append(f"{key}: {exc}")
                continue
            if current:
                current["description"] = description
            else:
                entry = {"name": name, "source": src["id"], "path": path, "categories": [DEFAULT_CATEGORY], "description": description}
                index["skills"].append(entry)
                by_key[key] = entry
    if not any(c["id"] == DEFAULT_CATEGORY for c in index.get("categories", [])) and any(DEFAULT_CATEGORY in s["categories"] for s in index["skills"]):
        index.setdefault("categories", []).append({"id": DEFAULT_CATEGORY, "name": "Geral", "description": "Skills sem categoria definida"})
    index["skills"].sort(key=lambda s: (s["source"], s["name"]))
    index["lastUpdated"] = today()
    return index, failures


def add_source(index: dict, url: str) -> dict:
    owner, repo = parse_repo_url(url)
    sid = re.sub(r"[^a-z0-9-]+", "-", f"{owner}-{repo}".lower()).strip("-")
    if any(s["id"] == sid or s["url"].rstrip("/").lower() == f"https://github.com/{owner}/{repo}".lower() for s in index["sources"]):
        raise ScoutError(f"A fonte {owner}/{repo} já está no índice")
    src = {"id": sid, "name": repo, "owner": owner, "url": f"https://github.com/{owner}/{repo}", "type": "community",
           "description": "Fonte adicionada pelo usuário"}
    index["sources"].append(src)
    return src


# ---------------------------------------------------------------- saída

CONFIDENCE = {"official": "oficial", "awesome-list": "lista curada", "community": "comunidade (por sua conta e risco)"}


def format_table(results: list, index: dict) -> str:
    rows = [("skill", "descrição", "fonte", "confiança")]
    for s in results:
        src = source_of(index, s)
        rows.append((s["name"], s["description"], src["id"], CONFIDENCE[src["type"]]))
    widths = [min(max(len(r[i]) for r in rows), 60) for i in range(4)]
    lines = []
    for n, r in enumerate(rows):
        lines.append("| " + " | ".join(shorten(c, widths[i]).ljust(widths[i]) for i, c in enumerate(r)) + " |")
        if n == 0:
            lines.append("|" + "|".join("-" * (w + 2) for w in widths) + "|")
    return "\n".join(lines)


def stats(index: dict) -> dict:
    cats = {c for s in index["skills"] for c in s["categories"]}
    return {"fontes": len(index["sources"]), "skills": len(index["skills"]), "categorias": len(cats), "indice_de": index["lastUpdated"]}


def check_environment(client: GitHub, runner=subprocess.run) -> list:
    lines = [f"python: {sys.version.split()[0]} (mínimo 3.10)"]
    if client.has_gh:
        try:
            out = runner(["gh", "--version"], capture_output=True, text=True, timeout=15).stdout.split()
            version = out[2] if len(out) > 2 else "?"
            major = int(version.split(".")[0]) if version[:1].isdigit() else 0
            lines.append(f"gh: {version}" + ("" if major >= 2 else " (necessário 2.0 ou superior)"))
            auth = runner(["gh", "auth", "status"], capture_output=True, timeout=15)  # só o código de saída é usado
            lines.append("gh autenticado: " + ("sim" if auth.returncode == 0 else "não (rode 'gh auth login')"))
        except (OSError, subprocess.SubprocessError, ValueError):
            lines.append("gh: instalado, mas não respondeu")
    else:
        lines.append("gh: não encontrado (busca de código e atualização do índice ficam limitadas)")
    return lines


# ---------------------------------------------------------------- CLI

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="search_skills.py", description="Procura, instala e gerencia skills de agente.")
    p.add_argument("query", nargs="?", default="", help="palavras e/ou #categorias")
    p.add_argument("--category", "-c", help="filtra por categoria")
    p.add_argument("--source", "-s", help="filtra por fonte (id)")
    p.add_argument("--external", "-e", action="store_true", help="busca SKILL.md no GitHub")
    p.add_argument("--web", "-w", action="store_true", help="mostra links de busca na web")
    p.add_argument("--list-categories", action="store_true")
    p.add_argument("--list-sources", action="store_true")
    p.add_argument("--list-starred", action="store_true")
    p.add_argument("--add-source", metavar="URL", help="adiciona um repositório GitHub como fonte e sincroniza")
    p.add_argument("--update", action="store_true", help="atualiza o índice a partir das fontes")
    p.add_argument("--info", metavar="SKILL")
    p.add_argument("--install", metavar="SKILL")
    p.add_argument("--install-dir", metavar="DIR", help=f"padrão: {INSTALL_DIR}")
    p.add_argument("--approve", action="store_true", help="aprovação do usuário para instalar (use só depois que ele aprovar)")
    p.add_argument("--allow-host", action="append", default=[], metavar="HOST", help="aprova um host fora da lista padrão (nesta execução)")
    p.add_argument("--similar", metavar="SKILL")
    p.add_argument("--star", metavar="SKILL")
    p.add_argument("--unstar", metavar="SKILL")
    p.add_argument("--stats", action="store_true")
    p.add_argument("--check", action="store_true", help="verifica o ambiente (python, gh)")
    p.add_argument("--no-interactive", action="store_true", help="não faz perguntas no terminal")
    p.add_argument("--json", action="store_true", help="saída da busca em JSON")
    p.add_argument("--references-dir", default=str(REFERENCES_DIR), help=argparse.SUPPRESS)
    return p


def ask(question: str, interactive: bool) -> bool:
    if not interactive:
        return False
    try:
        return input(f"{question} [s/N] ").strip().lower() in ("s", "sim", "y", "yes")
    except EOFError:
        return False


def run(argv=None, client: GitHub | None = None, out=print) -> int:
    args = build_parser().parse_args(argv)
    client = client or GitHub()
    refs = Path(args.references_dir)
    interactive = sys.stdin.isatty() and not args.no_interactive
    try:
        if args.check:
            for line in check_environment(client):
                out(line)
            return EXIT_OK
        index_path = refs / "skill-index.json"
        index = load_index(refs) if index_path.exists() else empty_index()

        if args.add_source:
            src = add_source(index, args.add_source)
            before = len(index["skills"])
            index, failures = update_index(index, client, only_source=src["id"])
            problems = validate_index(index)
            if problems:
                raise ScoutError("O índice resultante seria inválido: " + "; ".join(problems[:3]))
            save_json(index_path, index)
            out(f"Fonte {src['id']} adicionada. Skills: {before} -> {len(index['skills'])}. lastUpdated={index['lastUpdated']}")
            for f in failures:
                out(f"aviso: {f}")
            return EXIT_OK
        if args.update:
            before = len(index["skills"])
            index, failures = update_index(index, client)
            problems = validate_index(index)
            if problems:
                raise ScoutError("O índice resultante seria inválido: " + "; ".join(problems[:3]))
            save_json(index_path, index)
            out(f"Índice atualizado. Skills: {before} -> {len(index['skills'])}. lastUpdated={index['lastUpdated']}")
            for f in failures:
                out(f"falha: {f}")
            return EXIT_OK
        if args.list_categories:
            for c in index.get("categories", []):
                out(f"{c['id']}\t{c['name']}\t{c['description']}")
            return EXIT_OK
        if args.list_sources:
            for s in index["sources"]:
                out(f"{s['id']}\t{s['type']}\t{s['url']}")
            return EXIT_OK
        if args.list_starred:
            for k in load_starred(refs)["starred"]:
                out(k)
            return EXIT_OK
        if args.stats:
            for k, v in stats(index).items():
                out(f"{k}: {v}")
            return EXIT_OK
        if args.star or args.unstar:
            key = set_star(refs, index, args.star or args.unstar, on=bool(args.star))
            out(("Favoritada: " if args.star else "Removida dos favoritos: ") + key)
            return EXIT_OK
        if args.info:
            s = find_skill(index, args.info)
            src = source_of(index, s)
            out(f"{s['name']}\n  descrição: {s['description']}\n  fonte: {src['id']} ({CONFIDENCE[src['type']]})\n  categorias: {', '.join(s['categories'])}\n  caminho: {src['url']}/tree/HEAD/{s['path']}")
            return EXIT_OK
        if args.similar:
            for s in similar_skills(index, args.similar):
                out(f"{skill_key(s)}\t{s['description']}")
            return EXIT_OK
        if args.install:
            plan = plan_install(index, args.install, client, args.allow_host)
            out(f"Instalar: {plan['skill']['name']}\n  origem: {plan['url']}\n  host: {plan['host']}\n  confiança: {CONFIDENCE[plan['source']['type']]}\n"
                f"  ferramentas/permissões exigidas pelo SKILL.md: {plan['requires'] or '(não declaradas)'}\n  Nenhum script será executado.")
            if not (args.approve or ask("Aprova a instalação?", interactive)):
                out("Aprovação necessária: peça ao usuário e repita com --approve.")
                return EXIT_APPROVAL
            dest = install_skill(plan, client, Path(args.install_dir) if args.install_dir else INSTALL_DIR)
            out(f"Instalada em {dest}")
            return EXIT_OK

        # busca
        age = index_age_days(index)
        if age > AUTO_UPDATE_DAYS:
            out(f"Aviso: o índice tem {age} dias (limite {AUTO_UPDATE_DAYS}). Rode --update para renovar.")
        if args.web:
            for name, url in web_search_links(args.query or ""):
                out(f"{name}: {url}")
        starred = set(load_starred(refs)["starred"])
        results = search_index(index, args.query, args.category, args.source, starred)
        if args.json:
            out(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            out(f"{len(index['sources'])} repositórios, {len(index['skills'])} skills pesquisadas; índice de {index['lastUpdated']}")
            out(format_table(results, index) if results else "Nenhum resultado no índice.")
            rec = recommend(results, index, args.query)
            if rec:
                out(f"Recomendação: {rec[0]['name']} ({rec[1]})")
            if any(source_of(index, s)["type"] == "community" for s in results):
                out("Aviso: fontes da comunidade são por sua conta e risco; revise o SKILL.md antes de usar.")
            if results:
                out("Próximos passos:\n  1. --info <skill> para ver detalhes\n  2. --install <skill> (peça aprovação ao usuário)\n  3. --star <skill> para favoritar")
        if args.external:
            try:
                hits = client.search_code(f"filename:SKILL.md {args.query}")
                if hits:
                    out("Resultados externos (GitHub, busca de código):")
                    for h in hits:
                        out(f"  {h['repo']}/{h['path']}")
                else:
                    out("Sem resultados na busca de código; repositórios relacionados:")
                    for r in client.search_repos(f"{args.query} agent skills"):
                        out(f"  {r['nameWithOwner']} ({r['stargazersCount']}★) {shorten(r['description'], 80)}  -> --add-source https://github.com/{r['nameWithOwner']}")
            except ScoutError as exc:
                out(f"Busca externa indisponível: {exc}")
        return EXIT_OK
    except ScoutError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(run())
