from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_transcribe.engines import (
    clean_sensevoice_text,
    paragraphize_video_text,
    restore_video_transcript_text,
)


class EngineTests(unittest.TestCase):
    def test_removes_sensevoice_acoustic_emoji(self):
        text = "🎼开场😊 能抵御炸弹吗？😡 掌声👏 笑声😀 哭😭 咳嗽😷❓"
        self.assertEqual(clean_sensevoice_text(text), "开场 能抵御炸弹吗？ 掌声 笑声 哭 咳嗽")

    def test_preserves_normal_text_and_punctuation(self):
        text = "造价10亿美元的地堡，真的安全吗？"
        self.assertEqual(clean_sensevoice_text(text), text)

    def test_video_fallback_restores_punctuation_and_merges_segments(self):
        class PunctuationModel:
            def generate(self, *, input):
                self.input = input
                return [{"text": "第一句，接着说。第二句？第三句！第四句。第五句。"}]

        model = PunctuationModel()
        raw = "[   0.0s ->    1.0s] 第一句接着说\n[   1.0s ->    2.0s] 第二句第三句第四句第五句"
        result = restore_video_transcript_text(raw, punc_model=model)
        self.assertEqual(model.input, "第一句接着说第二句第三句第四句第五句")
        self.assertNotIn("0.0s", result)
        self.assertIn("第一句，接着说。第二句？第三句！", result)
        self.assertIn("\n\n第五句。", result)

    def test_video_fallback_fails_closed_when_punctuation_is_empty(self):
        model = type("EmptyModel", (), {"generate": lambda self, **_kwargs: []})()
        with self.assertRaisesRegex(RuntimeError, "returned no text"):
            restore_video_transcript_text("[ 0.0s -> 1.0s] 正文", punc_model=model)

    def test_sensevoice_video_text_is_split_into_paragraphs(self):
        text = "第一句。第二句？第三句！第四句。第五句。。第六句。"
        result = paragraphize_video_text(text)
        self.assertEqual(result, "第一句。第二句？第三句！第四句。\n\n第五句。第六句。")
        self.assertNotIn("。。", result)


if __name__ == "__main__":
    unittest.main()
