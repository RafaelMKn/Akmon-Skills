#!/usr/bin/env python3
"""Testes offline do skill-scout (só biblioteca padrão). Rode: python3 scripts/test_search_skills.py"""
import contextlib
import datetime
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_skills as ss  # noqa: E402


class FakeClient:
    """Repositórios em memória: {"dono/repo": {"caminho/arquivo": bytes}}."""

    def __init__(self, repos=None, code_hits=None, has_gh=True):
        self.repos = repos or {}
        self.code_hits = code_hits
        self.has_gh = has_gh
        self.calls = 0

    def list_dir(self, owner, repo, path=""):
        self.calls += 1
        files = self.repos.get(f"{owner}/{repo}")
        if files is None:
            raise ss.ScoutError("repositório inexistente")
        prefix = path.strip("/") + "/" if path.strip("/") else ""
        entries = {}
        for name, data in files.items():
            if not name.startswith(prefix):
                continue
            rest = name[len(prefix):]
            head = rest.split("/", 1)[0]
            if "/" in rest:
                entries[head] = {"name": head, "type": "dir", "path": prefix + head}
            else:
                entries[head] = {"name": head, "type": "file", "path": name, "size": len(data)}
        if not entries:
            raise ss.ScoutError("pasta inexistente")
        return list(entries.values())

    def read_file(self, owner, repo, path):
        files = self.repos.get(f"{owner}/{repo}", {})
        if path not in files:
            raise ss.ScoutError(f"sem arquivo {path}")
        return files[path]

    def search_code(self, query, limit=30):
        if not self.has_gh:
            raise ss.ScoutError("sem gh")
        if self.code_hits is None:
            raise ss.ScoutError("busca indisponível")
        return self.code_hits

    def search_repos(self, query, limit=10):
        return [{"nameWithOwner": "x/y", "description": "d", "stargazersCount": 3}]


def make_index():
    today = datetime.date.today().isoformat()
    return {
        "version": "1.0.0", "lastUpdated": today,
        "categories": [{"id": "dados", "name": "Dados", "description": "d"}, {"id": "docs", "name": "Docs", "description": "d"},
                       {"id": "geral", "name": "Geral", "description": "d"}],
        "sources": [
            {"id": "oficial", "name": "oficial", "owner": "org", "url": "https://github.com/org/oficial", "type": "official", "description": "d"},
            {"id": "comunidade", "name": "comunidade", "owner": "alguem", "url": "https://github.com/alguem/comunidade", "type": "community", "description": "d"},
        ],
        "skills": [
            {"name": "planilhas", "source": "oficial", "path": "skills/planilhas", "categories": ["dados", "docs"], "description": "Analisa planilhas e tabelas"},
            {"name": "pdf-leitor", "source": "oficial", "path": "skills/pdf-leitor", "categories": ["docs"], "description": "Extrai texto de PDF"},
            {"name": "pdf-forms", "source": "comunidade", "path": "pdf-forms", "categories": ["docs"], "description": "Preenche formulários PDF"},
            {"name": "graficos", "source": "comunidade", "path": "graficos", "categories": ["dados"], "description": "Gera gráficos"},
        ],
    }


class IndexValidation(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(ss.validate_index(make_index()), [])
        self.assertEqual(ss.validate_index(ss.empty_index()), [])

    def test_invalid_cases(self):
        def mutate(fn):
            idx = make_index()
            fn(idx)
            return ss.validate_index(idx)
        self.assertTrue(mutate(lambda i: i.update(extra=1)))
        self.assertTrue(mutate(lambda i: i.update(version="1.0")))
        self.assertTrue(mutate(lambda i: i.update(lastUpdated="17/11/2026")))
        self.assertTrue(mutate(lambda i: i["sources"][0].update(url="https://gitlab.com/a/b")))
        self.assertTrue(mutate(lambda i: i["sources"][0].update(type="oficial")))
        self.assertTrue(mutate(lambda i: i["skills"][0].update(source="inexistente")))
        self.assertTrue(mutate(lambda i: i["skills"][0].update(categories=[])))
        self.assertTrue(mutate(lambda i: i["skills"][0].update(name="Nome Ruim")))
        self.assertTrue(mutate(lambda i: i["skills"][0].update(campo_extra="x")))
        self.assertTrue(mutate(lambda i: i["skills"][0].pop("path")))
        self.assertTrue(ss.validate_index([]))


class Texto(unittest.TestCase):
    def test_shorten(self):
        self.assertEqual(ss.shorten("a  b\nc"), "a b c")
        out = ss.shorten("x" * 150)
        self.assertEqual(len(out), 100)
        self.assertTrue(out.endswith("…"))

    def test_frontmatter_field(self):
        f = ss.frontmatter_field
        self.assertEqual(f("---\nname: a\ndescription: Faz isso\n---\n", "description"), "Faz isso")
        self.assertEqual(f('---\ndescription: "Com \\"aspas\\""\n---\n', "description"), 'Com "aspas"')
        self.assertEqual(f("---\ndescription: >-\n  linha um\n  linha dois\nname: a\n---\n", "description"), "linha um linha dois")
        self.assertEqual(f("---\ndescription: |\n  um\n  dois\n---\n", "description"), "um dois")
        self.assertEqual(f("---\ndescription: começa\n  e continua\n---\n", "description"), "começa e continua")
        self.assertEqual(f("sem frontmatter", "description"), "")
        self.assertEqual(f("---\nname: a\n---\n", "description"), "")
        self.assertEqual(f("---\nallowed-tools: Bash, Read\n---\n", "allowed-tools"), "Bash, Read")

    def test_description_falls_back_to_readme(self):
        self.assertEqual(ss.description_from("---\nname: a\n---\n", "# Título\n\nUm resumo útil.\n"), "Um resumo útil.")


class Busca(unittest.TestCase):
    def setUp(self):
        self.idx = make_index()

    def names(self, **kw):
        return [s["name"] for s in ss.search_index(self.idx, **kw)]

    def test_terms_are_case_insensitive_and_anded(self):
        self.assertEqual(self.names(query="PDF"), ["pdf-forms", "pdf-leitor"])
        self.assertEqual(self.names(query="pdf formulários"), ["pdf-forms"])
        self.assertEqual(self.names(query="nada existe"), [])

    def test_tags_category_and_source(self):
        self.assertEqual(self.names(query="#dados"), ["graficos", "planilhas"])
        self.assertEqual(self.names(query="#dados #docs"), ["planilhas"])
        self.assertEqual(self.names(category="docs"), ["pdf-forms", "pdf-leitor", "planilhas"])
        self.assertEqual(self.names(source="comunidade"), ["graficos", "pdf-forms"])

    def test_starred_first(self):
        self.assertEqual(self.names(starred=["comunidade/graficos"])[0], "graficos")

    def test_find_skill_and_ambiguity(self):
        self.assertEqual(ss.find_skill(self.idx, "planilhas")["source"], "oficial")
        self.assertEqual(ss.find_skill(self.idx, "comunidade/pdf-forms")["name"], "pdf-forms")
        self.idx["skills"].append(dict(self.idx["skills"][1], source="comunidade"))
        with self.assertRaises(ss.ScoutError):
            ss.find_skill(self.idx, "pdf-leitor")
        with self.assertRaises(ss.ScoutError):
            ss.find_skill(self.idx, "nao-existe")

    def test_similar(self):
        sim = [s["name"] for s in ss.similar_skills(self.idx, "planilhas")]
        self.assertEqual(sim[0] in ("graficos", "pdf-forms", "pdf-leitor"), True)
        self.assertNotIn("planilhas", sim)
        close = [s["name"] for s in ss.similar_skills(self.idx, "pdf-leitr")]
        self.assertEqual(close[0], "pdf-leitor")  # nome fora do índice: semelhança de caracteres

    def test_recommend_needs_three_and_prefers_official(self):
        res = ss.search_index(self.idx, query="")
        best, why = ss.recommend(res, self.idx, "pdf")
        self.assertEqual(best["name"], "pdf-leitor")
        self.assertIn("oficial", why)
        self.assertIsNone(ss.recommend(res[:2], self.idx, "pdf"))

    def test_web_links(self):
        links = dict(ss.web_search_links("ler pdf"))
        self.assertEqual(set(links), {"Google", "Bing", "DuckDuckGo"})
        self.assertTrue(all("SKILL.md" in u and "ler+pdf" in u for u in links.values()))


class Seguranca(unittest.TestCase):
    def test_host_allowlist(self):
        self.assertEqual(ss.check_host("https://github.com/a/b"), "github.com")
        self.assertEqual(ss.check_host("https://raw.githubusercontent.com/a/b/x"), "raw.githubusercontent.com")
        for bad in ("https://github.com.evil.example/a/b", "https://evil.example/a/b", "https://notgithub.com/a", "file:///etc/passwd"):
            with self.assertRaises(ss.ScoutError, msg=bad):
                ss.check_host(bad)
        self.assertEqual(ss.check_host("https://meu-host.example/x", extra_hosts=["meu-host.example"]), "meu-host.example")

    def test_repo_url(self):
        self.assertEqual(ss.parse_repo_url("https://github.com/dono/repo.git"), ("dono", "repo"))
        for bad in ("http://github.com/a/b", "https://github.com/a", "https://github.com/a/b/c", "https://gist.github.com/a/b", "git@github.com:a/b"):
            with self.assertRaises(ss.ScoutError, msg=bad):
                ss.parse_repo_url(bad)

    def test_unsafe_paths(self):
        for bad in ("", "/etc", "../x", "a/../b", "a//b", "a\\b", "./a"):
            with self.assertRaises(ss.ScoutError, msg=bad):
                ss.safe_relative(bad)
        self.assertEqual(ss.safe_relative("skills/a-b"), "skills/a-b")
        for bad in ("", ".", "..", "a/b", "a\\b"):
            with self.assertRaises(ss.ScoutError, msg=bad):
                ss.safe_name(bad)


def repo_with_skill(extra=None):
    files = {
        "skills/planilhas/SKILL.md": b"---\nname: planilhas\ndescription: Analisa planilhas\nallowed-tools: Bash, Read\n---\n# corpo\n",
        "skills/planilhas/scripts/rodar.sh": b"#!/bin/sh\necho oi\n",
        "skills/planilhas/references/guia.md": b"guia",
    }
    files.update(extra or {})
    return FakeClient({"org/oficial": files})


class Instalacao(unittest.TestCase):
    def setUp(self):
        self.idx = make_index()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dest = Path(self.tmp.name) / "skills"

    def test_install_without_exec_bits_and_no_leftovers(self):
        client = repo_with_skill()
        plan = ss.plan_install(self.idx, "planilhas", client)
        self.assertEqual(plan["host"], "github.com")
        self.assertEqual(plan["requires"], "Bash, Read")
        final = ss.install_skill(plan, client, self.dest)
        self.assertEqual(final, self.dest / "planilhas")
        self.assertEqual((final / "references/guia.md").read_bytes(), b"guia")
        script = final / "scripts/rodar.sh"
        self.assertTrue(script.exists())
        self.assertEqual(stat.S_IMODE(script.stat().st_mode), 0o644)  # nada baixado vira executável
        self.assertEqual([p.name for p in self.dest.iterdir()], ["planilhas"])  # sem pasta temporária

    def test_never_overwrites(self):
        client = repo_with_skill()
        plan = ss.plan_install(self.idx, "planilhas", client)
        ss.install_skill(plan, client, self.dest)
        (self.dest / "planilhas" / "meu.txt").write_text("meu")
        with self.assertRaises(ss.ScoutError):
            ss.install_skill(plan, client, self.dest)
        self.assertEqual((self.dest / "planilhas" / "meu.txt").read_text(), "meu")

    def test_requires_skill_md_and_cleans_up(self):
        client = FakeClient({"org/oficial": {"skills/planilhas/README.md": b"x"}})
        plan = ss.plan_install(self.idx, "planilhas", client)
        with self.assertRaises(ss.ScoutError):
            ss.install_skill(plan, client, self.dest)
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_hostile_remote_name_is_rejected(self):
        class Hostile(FakeClient):
            def list_dir(self, owner, repo, path=""):
                return [{"name": "../fuga.txt", "type": "file", "size": 1}]
        with self.assertRaises(ss.ScoutError):
            ss.install_skill(ss.plan_install(self.idx, "planilhas", repo_with_skill()), Hostile(), self.dest)
        self.assertFalse((self.dest.parent / "fuga.txt").exists())
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_poisoned_index_is_rejected(self):
        self.idx["sources"][0]["url"] = "https://github.com.evil.example/org/oficial"
        with self.assertRaises(ss.ScoutError):
            ss.plan_install(self.idx, "planilhas", repo_with_skill())
        idx = make_index()
        idx["skills"][0]["path"] = "../../etc"
        with self.assertRaises(ss.ScoutError):
            ss.plan_install(idx, "planilhas", repo_with_skill())

    def test_size_limits(self):
        files = {f"skills/planilhas/f{i}.txt": b"x" for i in range(ss.MAX_FILES + 1)}
        files["skills/planilhas/SKILL.md"] = b"---\nname: a\n---\n"
        client = FakeClient({"org/oficial": files})
        with self.assertRaises(ss.ScoutError):
            ss.install_skill(ss.plan_install(self.idx, "planilhas", client), client, self.dest)


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.refs = Path(self.tmp.name) / "references"
        self.refs.mkdir()
        ss.save_json(self.refs / "skill-index.json", make_index())
        self.dest = Path(self.tmp.name) / "instalados"

    def run_cli(self, *argv, client=None):
        lines = []
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = ss.run(["--references-dir", str(self.refs), "--no-interactive", *argv], client=client or FakeClient(), out=lines.append)
        return code, "\n".join(lines), err.getvalue()

    def test_search_output(self):
        code, out, _ = self.run_cli("pdf")
        self.assertEqual(code, 0)
        self.assertIn("2 repositórios, 4 skills pesquisadas", out)
        self.assertIn("pdf-leitor", out)
        self.assertIn("comunidade (por sua conta e risco)", out)
        self.assertIn("Próximos passos", out)
        self.assertNotIn("planilhas", out)

    def test_search_json_and_web(self):
        code, out, _ = self.run_cli("pdf", "--json")
        self.assertEqual([s["name"] for s in json.loads(out)], ["pdf-forms", "pdf-leitor"])
        self.assertIn("duckduckgo", self.run_cli("pdf", "--web")[1].lower())

    def test_stale_index_warns(self):
        idx = make_index()
        idx["lastUpdated"] = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
        ss.save_json(self.refs / "skill-index.json", idx)
        self.assertIn("30 dias", self.run_cli("pdf")[1])

    def test_install_needs_approval_then_works(self):
        client = repo_with_skill()
        code, out, _ = self.run_cli("--install", "planilhas", "--install-dir", str(self.dest), client=client)
        self.assertEqual(code, ss.EXIT_APPROVAL)
        self.assertIn("Nenhum script será executado", out)
        self.assertIn("Bash, Read", out)
        self.assertFalse(self.dest.exists())
        code, out, _ = self.run_cli("--install", "planilhas", "--install-dir", str(self.dest), "--approve", client=client)
        self.assertEqual(code, 0)
        self.assertTrue((self.dest / "planilhas" / "SKILL.md").is_file())

    def test_star_unstar_and_list(self):
        self.assertEqual(self.run_cli("--star", "pdf-forms")[0], 0)
        self.assertEqual(self.run_cli("--list-starred")[1], "comunidade/pdf-forms")
        self.assertEqual(json.loads((self.refs / "starred-skills.json").read_text())["starred"], ["comunidade/pdf-forms"])
        self.assertEqual(self.run_cli("--unstar", "pdf-forms")[0], 0)
        self.assertEqual(self.run_cli("--list-starred")[1], "")
        self.assertEqual(self.run_cli("--star", "nao-existe")[0], ss.EXIT_ERROR)

    def test_lists_stats_info(self):
        self.assertIn("docs", self.run_cli("--list-categories")[1])
        self.assertIn("official", self.run_cli("--list-sources")[1])
        stats_out = self.run_cli("--stats")[1]
        self.assertIn("skills: 4", stats_out)
        self.assertIn("categorias: 2", stats_out)
        self.assertIn("pdf-leitor", self.run_cli("--similar", "pdf-forms")[1])
        self.assertIn("Extrai texto de PDF", self.run_cli("--info", "pdf-leitor")[1])

    def test_invalid_index_is_reported(self):
        bad = make_index()
        bad["skills"][0]["source"] = "x"
        ss.save_json(self.refs / "skill-index.json", bad)
        code, _, err = self.run_cli("pdf")
        self.assertEqual(code, ss.EXIT_ERROR)
        self.assertIn("Índice inválido", err)

    def test_check_environment(self):
        class Proc:
            returncode, stdout = 0, "gh version 2.40.0 (2024)\n"
        lines = ss.check_environment(FakeClient(has_gh=True), runner=lambda *a, **k: Proc())
        self.assertTrue(any(l.startswith("gh: 2.40.0") for l in lines))
        self.assertTrue(any("autenticado: sim" in l for l in lines))
        self.assertTrue(any("não encontrado" in l for l in ss.check_environment(FakeClient(has_gh=False))))

    def test_external_search_without_gh_is_reported_not_fatal(self):
        code, out, _ = self.run_cli("pdf", "--external", client=FakeClient(has_gh=False))
        self.assertEqual(code, 0)
        self.assertIn("Busca externa indisponível", out)


class Atualizacao(unittest.TestCase):
    def setUp(self):
        self.idx = ss.empty_index()
        self.idx["version"] = "1.0.0"
        self.idx["lastUpdated"] = "2000-01-01"
        self.idx["sources"] = [
            {"id": "a-um", "name": "um", "owner": "a", "url": "https://github.com/a/um", "type": "community", "description": "d"},
            {"id": "b-dois", "name": "dois", "owner": "b", "url": "https://github.com/b/dois", "type": "community", "description": "d"},
        ]
        sk = lambda desc: f"---\nname: x\ndescription: {desc}\n---\n".encode()
        self.client = FakeClient({
            "a/um": {"skills/alfa/SKILL.md": sk("Primeira skill"), "skills/beta/SKILL.md": b"---\nname: beta\n---\n", "skills/beta/README.md": b"# Beta\n\nResumo do README.\n",
                     "skills/sem-skill/README.md": b"x"},
            # b/dois sem repositório: falha isolada
        })

    def test_discovers_skills_dir_and_isolates_failures(self):
        idx, failures = ss.update_index(self.idx, self.client, sleep=lambda s: None)
        names = [(s["source"], s["name"]) for s in idx["skills"]]
        self.assertEqual(names, [("a-um", "alfa"), ("a-um", "beta")])
        self.assertEqual({s["name"]: s["description"] for s in idx["skills"]}, {"alfa": "Primeira skill", "beta": "Resumo do README."})
        self.assertTrue(any(f.startswith("b-dois:") for f in failures))
        self.assertEqual(idx["lastUpdated"], datetime.date.today().isoformat())
        self.assertEqual(ss.validate_index(idx), [])

    def test_root_subdirs_fallback_and_code_search_first(self):
        client = FakeClient({"a/um": {"solo/SKILL.md": b"---\nname: s\ndescription: Solo\n---\n"}})
        self.idx["sources"] = self.idx["sources"][:1]
        idx, _ = ss.update_index(self.idx, client, sleep=lambda s: None)
        self.assertEqual([s["path"] for s in idx["skills"]], ["solo"])
        client = FakeClient({"a/um": {"pacotes/x/SKILL.md": b"---\ndescription: Via busca\n---\n"}},
                            code_hits=[{"repo": "a/um", "path": "pacotes/x/SKILL.md"}, {"repo": "a/um", "path": "README.md"}])
        self.idx["skills"] = []
        idx, _ = ss.update_index(self.idx, client, sleep=lambda s: None)
        self.assertEqual([(s["path"], s["description"]) for s in idx["skills"]], [("pacotes/x", "Via busca")])

    def test_only_refreshes_empty_or_skill_suffix_descriptions(self):
        self.idx["sources"] = self.idx["sources"][:1]
        self.idx["skills"] = [
            {"name": "alfa", "source": "a-um", "path": "skills/alfa", "categories": ["geral"], "description": "Descrição curada à mão"},
            {"name": "beta", "source": "a-um", "path": "skills/beta", "categories": ["docs"], "description": "beta skill"},
        ]
        idx, _ = ss.update_index(self.idx, self.client, sleep=lambda s: None)
        by = {s["name"]: s for s in idx["skills"]}
        self.assertEqual(by["alfa"]["description"], "Descrição curada à mão")
        self.assertEqual(by["beta"]["description"], "Resumo do README.")
        self.assertEqual(by["beta"]["categories"], ["docs"])  # categorias existentes são preservadas

    def test_add_source(self):
        src = ss.add_source(self.idx, "https://github.com/Fulano/Minhas-Skills.git")
        self.assertEqual((src["id"], src["url"], src["type"]), ("fulano-minhas-skills", "https://github.com/Fulano/Minhas-Skills", "community"))
        with self.assertRaises(ss.ScoutError):
            ss.add_source(self.idx, "https://github.com/fulano/minhas-skills")
        with self.assertRaises(ss.ScoutError):
            ss.add_source(self.idx, "https://evil.example/a/b")
        self.assertEqual(ss.validate_index(self.idx), [])


class ArquivosDoPacote(unittest.TestCase):
    def test_shipped_index_and_files_are_valid(self):
        refs = Path(__file__).resolve().parent.parent / "references"
        self.assertEqual(ss.validate_index(json.loads((refs / "skill-index.json").read_text(encoding="utf-8"))), [])
        starred = json.loads((refs / "starred-skills.json").read_text(encoding="utf-8"))
        self.assertEqual(starred["starred"], [])
        schema = json.loads((refs / "skill-index.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "http://json-schema.org/draft-07/schema#")

    def test_help_runs(self):
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()) as buf:
            ss.run(["--help"])
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("--install", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
