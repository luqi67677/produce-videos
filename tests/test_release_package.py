from __future__ import annotations

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from package_release import build_all  # noqa: E402


class ReleasePackageTests(unittest.TestCase):
    def test_builds_three_installers_without_demo_videos(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifacts = build_all(ROOT, Path(temp_dir))
            names = {path.name for path in artifacts}
            self.assertEqual(names, {"produce-videos.zip", "produce-videos.skill", "produce-videos-workbuddy.zip", "SHA256SUMS.txt"})
            with zipfile.ZipFile(Path(temp_dir) / "produce-videos.zip") as archive:
                archived = set(archive.namelist())
                self.assertIn("produce-videos/SKILL.md", archived)
                self.assertIn("produce-videos/examples/README.md", archived)
                self.assertIn("produce-videos/examples/thumbnails/obsidian-ai-brain.jpg", archived)
                self.assertFalse(any("examples/videos/" in name for name in archived))
                self.assertFalse(any("/dist/" in name for name in archived))


if __name__ == "__main__":
    unittest.main()
