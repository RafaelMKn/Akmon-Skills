import importlib.machinery
import io
from pathlib import Path
import tarfile
import unittest

mod = importlib.machinery.SourceFileLoader('podman_qa_wrapper', str(Path(__file__).parent / 'bin/podman')).load_module()


def archive(payload=b'qa-fixture', name='marker'):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w', format=tarfile.PAX_FORMAT) as tar:
        member = tarfile.TarInfo(name)
        member.size = len(payload)
        tar.addfile(member, io.BytesIO(payload))
    return buf.getvalue()


class PaddingTests(unittest.TestCase):
    def test_preserves_payload(self):
        data = archive(b'qa-fixture\x00\x00')
        compact = mod.compact_tar(data)
        self.assertLess(len(compact), len(data))
        with tarfile.open(fileobj=io.BytesIO(compact)) as tar:
            self.assertEqual(tar.extractfile('marker').read(), b'qa-fixture\x00\x00')

    def test_long_pax_name(self):
        name = 'x' * 200
        with tarfile.open(fileobj=io.BytesIO(mod.compact_tar(archive(b'hello', name)))) as tar:
            self.assertEqual(tar.extractfile(name).read(), b'hello')

    def test_already_compact(self):
        compact = mod.compact_tar(archive())
        self.assertEqual(mod.compact_tar(compact), compact)

    def test_rejects_nonzero_trailer(self):
        with self.assertRaises(ValueError):
            mod.compact_tar(archive() + b'UNEXPECTED')

    def test_rejects_invalid(self):
        with self.assertRaises(tarfile.TarError):
            mod.compact_tar(b'not a tar archive')


if __name__ == '__main__':
    unittest.main()
