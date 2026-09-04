import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from video_preflight import loudness_status, true_peak_status  # noqa: E402


class VideoPreflightThresholdsTest(unittest.TestCase):
    def test_loudness_outside_delivery_range_fails(self):
        self.assertEqual("fail", loudness_status(-20.5))
        self.assertEqual("fail", loudness_status(-13.9))

    def test_loudness_near_target_passes(self):
        self.assertEqual("pass", loudness_status(-17.2))

    def test_acceptable_edge_can_warn(self):
        self.assertEqual("warn", loudness_status(-19.0))

    def test_true_peak_above_limit_fails(self):
        self.assertEqual("fail", true_peak_status(-0.9))
        self.assertEqual("pass", true_peak_status(-1.0))


if __name__ == "__main__":
    unittest.main()
