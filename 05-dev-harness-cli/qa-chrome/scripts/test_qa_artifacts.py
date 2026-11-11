"""Testes do helper qa_artifacts. Todos os dados são SINTÉTICOS (repo/SHA fictícios)."""
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path

import qa_artifacts as qa

SHA = "a" * 40
BASE = "b" * 40


def sample():
    return {
        "repo": "/srv/synthetic/repo-fake",
        "mode": "separado",
        "targets": [{"label": "PR-0 sintético", "kind": "pr", "ref": "feature/fake",
                     "sha": SHA, "base_branch": "develop-fake", "base_sha": BASE,
                     "base_discovery": "origin/HEAD sintético"}],
        "environment": {
            "urls": ["http://127.0.0.1:9999/"], "description": "painel sintético",
            "isolation_verified": True, "url_serves_target_sha": True,
            "readiness_evidence": ["curl /version -> sha aaaa (sintético)"],
            "resources": ["worktree /tmp/fake-wt"], "stop_commands": ["git worktree remove /tmp/fake-wt"],
        },
        "scenarios": [
            {"id": "C1", "title": "Feliz", "source": "issue #0", "priority": "alta",
             "steps": ["abrir /"], "expected": "vê título", "evidence_required": "texto exato"},
            {"id": "C2", "title": "Erro", "source": "diff x", "steps": ["enviar vazio"],
             "expected": "mensagem", "evidence_required": "texto", "depends_on": ["C1"]},
        ],
        "known_failures": ["flaky sintético"],
    }


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.out = self.root / "out"

    def write(self, data, name="in.json"):
        p = self.root / name
        p.write_text(json.dumps(data), encoding="utf-8")
        return str(p)

    def init(self, data=None):
        rc = qa.main(["init", "--input", self.write(data or sample()), "--out-root", str(self.out)])
        return rc

    def run_dir(self):
        return next(self.out.iterdir())


class PositiveFlow(Base):
    def test_full_flow(self):
        self.assertEqual(self.init(), 0)
        d = self.run_dir()
        names = sorted(p.name for p in d.iterdir())
        self.assertEqual(names, ["briefing-gemini-qa.md", "checklist.md", "manifest.json", "results.json"])
        prompt = (d / "briefing-gemini-qa.md").read_text()
        for needle in (SHA, "http://127.0.0.1:9999/", "C1", "C2", "aprovado | reprovado | bloqueado | não executado",
                       "Intervenção do usuário", "Não corrija código", "Gemini 3.8 Flash high",
                       "Playwright/Chromium headless", "trace inclusive dos testes aprovados",
                       "não verificados até auditoria"):
            self.assertIn(needle, prompt)
        self.assertEqual(qa.main(["suite", "--run-dir", str(d), "--command", "pytest -q", "--exit-code", "0",
                                  "--log", "/x/log.txt"]), 0)
        self.assertEqual(qa.main(["record", "--run-dir", str(d), "--id", "C1", "--status", "aprovado",
                                  "--evidence", "texto 'Olá' visível", "--by", "chrome"]), 0)
        self.assertEqual(qa.main(["report", "--run-dir", str(d)]), 0)
        rep = (d / "relatorio-qa.md").read_text()
        self.assertIn("C1 — Feliz: aprovado", rep)
        self.assertIn("C2 — Erro: não executado", rep)
        self.assertIn("INCOMPLETA", rep)
        self.assertIn("git worktree remove /tmp/fake-wt", rep)
        self.assertIn("exit 0", rep)

    def test_unready_env_blocks_prompt(self):
        s = sample()
        s["environment"]["url_serves_target_sha"] = False
        self.assertEqual(self.init(s), 3)
        self.assertFalse((self.run_dir() / "briefing-gemini-qa.md").exists())


class Security(Base):
    def assertRejected(self, data):
        self.assertEqual(self.init(data), 2)
        self.assertFalse(self.out.exists() and any(self.out.iterdir()))

    def test_secrets_rejected(self):
        for bad in ("password=hunter2", "sk-abcdefghijklmnopqrstuvwx", "Bearer abcdefghijklmnop1234",
                    "http://u:p@host/", "ghp_" + "a" * 30, "-----BEGIN RSA PRIVATE KEY-----"):
            s = sample()
            s["scenarios"][0]["data"] = [bad]
            self.assertRejected(s)

    def test_bad_sha_and_url(self):
        s = sample(); s["targets"][0]["sha"] = "abc123"; self.assertRejected(s)
        s = sample(); s["environment"]["urls"] = ["file:///etc/passwd"]; self.assertRejected(s)
        s = sample(); s["environment"]["urls"] = ["javascript:alert(1)"]; self.assertRejected(s)
        s = sample(); s["environment"]["urls"] = ["http://user:pw@x/"]; self.assertRejected(s)

    def test_ready_requires_evidence(self):
        s = sample(); s["environment"]["readiness_evidence"] = []; self.assertRejected(s)

    def test_modes(self):
        s = sample(); s["targets"].append(copy.deepcopy(s["targets"][0])); self.assertRejected(s)  # separado, 2 alvos
        s["mode"] = "integrado"; self.assertRejected(s)  # sem pedido explícito
        s["integration_requested_by_user"] = True
        self.assertEqual(self.init(s), 2)  # sem tested_sha
        s["tested_sha"] = "d" * 40
        self.assertEqual(self.init(s), 0)

    def integrated(self, **extra):
        s = sample(); s["mode"] = "integrado"; s["integration_requested_by_user"] = True
        t2 = copy.deepcopy(s["targets"][0]); t2["label"] = "PR-1"; t2["sha"] = "c" * 40
        s["targets"].append(t2)
        s.update(extra)
        return s

    def test_integrated_requires_tested_sha(self):
        self.assertRejected(self.integrated())

    def test_integrated_renders_distinct_tested_sha(self):
        INT = "d" * 40
        self.assertEqual(self.init(self.integrated(tested_sha=INT)), 0)
        d = self.run_dir()
        self.assertEqual(json.loads((d / "manifest.json").read_text())["tested_sha"], INT)
        self.assertIn(INT[:8], d.name)
        for f in ("checklist.md", "briefing-gemini-qa.md"):
            self.assertIn(f"`{INT}`", (d / f).read_text())
        qa.main(["report", "--run-dir", str(d)])
        self.assertIn(f"`{INT}`", (d / "relatorio-qa.md").read_text())

    def test_separado_derives_tested_sha(self):
        self.assertEqual(self.init(), 0)
        self.assertEqual(json.loads((self.run_dir() / "manifest.json").read_text())["tested_sha"], SHA)

    def test_separado_conflicting_tested_sha_rejected(self):
        s = sample(); s["tested_sha"] = "d" * 40; self.assertRejected(s)

    def test_sha_not_normalized(self):
        for bad in (SHA.upper(), " " + SHA, SHA + " ", SHA + "\n"):
            s = sample(); s["targets"][0]["sha"] = bad; self.assertRejected(s)
            s = sample(); s["targets"][0]["base_sha"] = bad; self.assertRejected(s)
            self.assertRejected(self.integrated(tested_sha=bad))

    def test_scenario_validation(self):
        s = sample(); s["scenarios"][1]["id"] = "C1"; self.assertRejected(s)
        s = sample(); s["scenarios"][1]["depends_on"] = ["ZZ"]; self.assertRejected(s)
        s = sample(); s["scenarios"][0]["id"] = "../x"; self.assertRejected(s)

    def test_out_root_rules(self):
        inp = self.write(sample())
        self.assertEqual(qa.main(["init", "--input", inp, "--out-root", "relativo"]), 2)
        self.assertEqual(qa.main(["init", "--input", inp, "--out-root", str(self.root / "a" / ".." / "b")]), 2)
        s = sample(); s["repo"] = str(self.root / "repo"); (self.root / "repo").mkdir()
        inp = self.write(s, "in2.json")
        self.assertEqual(qa.main(["init", "--input", inp, "--out-root", str(self.root / "repo" / "qa")]), 2)

    def test_out_root_validated_before_mkdir(self):
        s = sample(); s["repo"] = str(self.root / "repo2"); (self.root / "repo2").mkdir()
        bad = self.root / "repo2" / "novo" / "fundo"
        self.assertEqual(qa.main(["init", "--input", self.write(s), "--out-root", str(bad)]), 2)
        self.assertFalse((self.root / "repo2" / "novo").exists())

    def test_no_overwrite(self):
        self.assertEqual(self.init(), 0)
        d = self.run_dir()
        with self.assertRaises(FileExistsError):
            qa.write_new(d / "checklist.md", "x")
        self.assertEqual(qa.main(["report", "--run-dir", str(d)]), 0)
        self.assertEqual(qa.main(["report", "--run-dir", str(d)]), 2)  # segundo falha
        d2 = qa.Path(d)
        with self.assertRaises(FileExistsError):
            d2.mkdir(parents=False, exist_ok=False)

    def test_record_rules(self):
        self.init()
        d = str(self.run_dir())
        # aprovado sem evidência é recusado
        self.assertEqual(qa.main(["record", "--run-dir", d, "--id", "C1", "--status", "aprovado", "--by", "chrome"]), 2)
        # com --unverified fica marcado
        self.assertEqual(qa.main(["record", "--run-dir", d, "--id", "C1", "--status", "aprovado",
                                  "--by", "chrome", "--unverified"]), 0)
        res = json.loads((Path(d) / "results.json").read_text())
        self.assertFalse(res["scenarios"]["C1"]["verified"])
        # id desconhecido, segredo em resultado, bloqueado vazio
        self.assertEqual(qa.main(["record", "--run-dir", d, "--id", "ZZ", "--status", "bloqueado",
                                  "--observed", "x", "--by", "hermes"]), 2)
        self.assertEqual(qa.main(["record", "--run-dir", d, "--id", "C2", "--status", "reprovado",
                                  "--evidence", "senha: abc123", "--by", "hermes"]), 2)
        self.assertEqual(qa.main(["record", "--run-dir", d, "--id", "C2", "--status", "bloqueado", "--by", "hermes"]), 2)
        qa.main(["report", "--run-dir", d])
        self.assertIn("NÃO VERIFICADO", (Path(d) / "relatorio-qa.md").read_text())

    def test_run_dir_must_be_valid(self):
        self.assertEqual(qa.main(["report", "--run-dir", str(self.root)]), 2)
        self.assertEqual(qa.main(["report", "--run-dir", "relativo"]), 2)

    def test_no_exec_or_network_imports(self):
        src = (Path(qa.__file__)).read_text()
        for banned in ("subprocess", "socket", "urllib.request", "http.client", "os.system", "requests"):
            self.assertNotIn(banned, src)


if __name__ == "__main__":
    unittest.main()
