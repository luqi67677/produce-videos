from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_layout_catalog import validate  # noqa: E402


class LayoutCatalogTests(unittest.TestCase):
    def test_all_88_layouts_have_specs_and_previews(self) -> None:
        self.assertEqual(validate(ROOT / "references/frontend-slides-layouts"), [])


if __name__ == "__main__":
    unittest.main()
