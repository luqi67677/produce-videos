from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_motion_coverage import (  # noqa: E402
    FRAME_BYTES,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    blank_visual_failed,
    frame_detail,
    longest_true_run,
)


class MotionAnalysisTests(unittest.TestCase):
    def test_blank_frame_has_no_detail(self) -> None:
        self.assertEqual(frame_detail(bytes([255]) * FRAME_BYTES), 0)

    def test_populated_frame_has_detail(self) -> None:
        frame = bytes((255 if (index // FRAME_WIDTH + index % FRAME_WIDTH) % 2 else 0) for index in range(FRAME_BYTES))
        self.assertGreater(frame_detail(frame), 100)

    def test_underfilled_hold_uses_sample_rate(self) -> None:
        self.assertEqual(longest_true_run([False, True, True, False], 10), 0.2)

    def test_sparse_opening_fails_without_intentional_blank(self) -> None:
        self.assertTrue(blank_visual_failed(0.3, 0.4, 0.45, 0.2, True, False))
        self.assertFalse(blank_visual_failed(0.3, 0.4, 0.45, 0.2, True, True))


if __name__ == "__main__":
    unittest.main()
