"""Regressões de fronteira: fixtures locais, sem rede ou execução de skills."""

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).with_name('check_skills.py')
SPEC = importlib.util.spec_from_file_location('check_skills', SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
VALID = '---\nname: fixture\ndescription: fixture\n---\n'


class ValidatorHardeningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR'))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.skill = self.root / '01-test/fixture/SKILL.md'
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text(VALID)
        self.external = Path(self.temp.name) / 'external.md'
        self.external.write_text(VALID)

    def run_validator(self, *flags):
        return subprocess.run(
            [sys.executable, str(SCRIPT), '--root', str(self.root), *flags],
            capture_output=True, text=True, check=False,
        )

    def test_relative_traversal_rejected_even_without_strict(self):
        self.skill.write_text(VALID + '[outside](../../../external.md)\n')
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn('fora do repositório', result.stdout)

    def test_absolute_link_rejected(self):
        self.skill.write_text(VALID + f'[outside]({self.external})\n')
        self.assertEqual(self.run_validator().returncode, 1)
        self.assertEqual(self.run_validator('--strict-links').returncode, 1)

    def test_external_symlink_link_rejected(self):
        (self.skill.parent / 'link.md').symlink_to(self.external)
        self.skill.write_text(VALID + '[outside](link.md)\n')
        self.assertEqual(self.run_validator().returncode, 1)

    def test_symlink_skill_never_read_even_if_internal(self):
        for target in (self.external, self.root / 'internal.md'):
            target.write_text(VALID)
            self.skill.unlink()
            self.skill.symlink_to(target)
            with patch.object(validator.yaml, 'safe_load', side_effect=AssertionError('leitura proibida')):
                errors, _ = validator.check_skill_file(self.skill, self.root)
            self.assertTrue(errors)
            self.assertEqual(self.run_validator().returncode, 1)

    def test_parent_symlink_never_read(self):
        outside_dir = Path(self.temp.name) / 'outside'
        outside_dir.mkdir()
        (outside_dir / 'SKILL.md').write_text(VALID)
        alias = self.root / 'alias'
        alias.symlink_to(outside_dir, target_is_directory=True)
        with patch.object(validator.yaml, 'safe_load', side_effect=AssertionError('leitura proibida')):
            errors, _ = validator.check_skill_file(alias / 'SKILL.md', self.root)
        self.assertTrue(errors)

    def test_missing_yaml_fails_closed(self):
        result = subprocess.run(
            [sys.executable, '-I', '-S', str(SCRIPT), '--root', str(self.root)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn('pyyaml', result.stderr)

    def test_frontmatter_size_stops_before_yaml(self):
        self.skill.write_text('---\n' + 'x' * (validator.MAX_FRONTMATTER_BYTES + 1) + '\n---\n')
        with patch.object(validator.yaml, 'safe_load', side_effect=AssertionError('parser proibido')):
            errors, _ = validator.check_skill_file(self.skill, self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn('64 KB', errors[0])

    def test_total_size_stops_before_yaml(self):
        with self.skill.open('wb') as file:
            file.truncate(validator.MAX_SKILL_BYTES + 1)
        with patch.object(validator.yaml, 'safe_load', side_effect=AssertionError('parser proibido')):
            errors, _ = validator.check_skill_file(self.skill, self.root)
        self.assertIn('4 MB', errors[0])

    def test_delimiters_are_full_lines(self):
        self.skill.write_text('---\nname: fixture\ndescription: "use --- as divider"\n---\n')
        self.assertEqual(self.run_validator().returncode, 0)
        self.skill.write_text('---bad\nname: fixture\ndescription: fixture\n---\n')
        self.assertEqual(self.run_validator().returncode, 1)
        self.skill.write_text('---\nname: fixture\ndescription: fixture\n')
        self.assertEqual(self.run_validator().returncode, 1)

    def test_workflow_contract(self):
        workflow = SCRIPT.parent.parent / '.github/workflows/check-skills.yml'
        data = validator.yaml.safe_load(workflow.read_text())
        triggers = data.get('on', data.get(True))
        self.assertNotIn('paths', triggers['pull_request'])
        self.assertNotIn('paths', triggers['push'])
        self.assertNotIn('pull_request_target', triggers)
        job = data['jobs']['validate-structure']
        install = next(s['run'] for s in job['steps'] if s.get('name') == 'Instalar dependências')
        self.assertIn('--require-hashes', install)
        self.assertIn('--only-binary=:all:', install)
        self.assertIn('PyYAML==6.0.2 --hash=sha256:', install)
        self.assertNotIn('--upgrade pip', install)


if __name__ == '__main__':
    unittest.main()
