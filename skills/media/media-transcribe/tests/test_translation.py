from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_transcribe.translation import _chunks, translate_with_deepseek


class TranslationTests(unittest.TestCase):
    def test_large_paragraph_has_no_empty_chunk(self):
        chunks = _chunks("x" * 8000)
        self.assertTrue(chunks)
        self.assertTrue(all(chunks))
        self.assertEqual("".join(chunks), "x" * 8000)

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_key_skips_translation(self):
        self.assertIsNone(translate_with_deepseek("English"))


if __name__ == "__main__":
    unittest.main()
