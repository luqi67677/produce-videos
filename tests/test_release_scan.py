from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scan_release import DEFAULT_BANNED, SECRET_PATTERNS, scan  # noqa: E402


class ReleaseScanTests(unittest.TestCase):
    def test_contact_outside_public_examples_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            contact = "person" + "@" + "example.com"
            (root / "README.md").write_text(f"contact {contact}", encoding="utf-8")

            errors = scan(root, DEFAULT_BANNED, release_root=False)

            self.assertTrue(any("密钥或访问令牌" in error for error in errors))

    def test_imported_layouts_have_no_email_or_secret_pattern(self) -> None:
        layout_root = ROOT / "references/frontend-slides-layouts"
        matches: list[str] = []
        for path in layout_root.rglob("*"):
            if not path.is_file():
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if any(pattern.search(content) for pattern in SECRET_PATTERNS):
                matches.append(path.relative_to(ROOT).as_posix())

        self.assertEqual(matches, [])


if __name__ == "__main__":
    unittest.main()
