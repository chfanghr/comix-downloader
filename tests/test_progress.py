import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from src.core.downloader import _ChapterProgress


class ChapterProgressTests(unittest.TestCase):
    def test_completed_pages_survive_and_invalid_pages_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            progress = _ChapterProgress(Path(directory) / "chapter", 2, "1nkd")
            output = BytesIO()
            Image.new("RGB", (2, 2), "red").save(output, format="PNG")
            data = output.getvalue()

            progress.save(1, data)
            self.assertEqual(progress.load(), {1: data})
            self.assertIn('"1nkd"', (progress.directory / "progress.json").read_text())

            (progress.directory / "00002.bin").write_bytes(b"not an image")
            self.assertEqual(progress.load(), {1: data})

            progress.clear()
            self.assertFalse(progress.directory.exists())
