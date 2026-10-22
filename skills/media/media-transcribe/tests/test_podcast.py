from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_transcribe.podcast import extract_audio_from_html, parse_duration, parse_rss_xml, select_episodes


class PodcastTests(unittest.TestCase):
    def test_extracts_audio_when_meta_attributes_are_reversed(self):
        content = (ROOT / "tests/fixtures/podcast.html").read_text(encoding="utf-8")
        url, title = extract_audio_from_html(content, "https://example.com/episode")
        self.assertEqual(url, "https://cdn.example.com/audio/episode.m4a?token=abc&x=1")
        self.assertEqual(title, "一期节目")

    def test_extracts_relative_audio_url(self):
        url, _ = extract_audio_from_html(
            '<html><title>Episode</title><audio src="/media/episode.mp3"></audio></html>',
            "https://podcast.example.com/episodes/1",
        )
        self.assertEqual(url, "https://podcast.example.com/media/episode.mp3")

    def test_parses_rss_metadata_and_preserves_feed_order(self):
        content = (ROOT / "tests/fixtures/feed.xml").read_text(encoding="utf-8")
        episodes = parse_rss_xml(content)
        self.assertEqual([ep.number for ep in episodes], [2, 1])
        self.assertEqual(episodes[1].duration_seconds, 3600)
        self.assertEqual(episodes[0].duration_seconds, 3723)
        self.assertEqual(episodes[0].audio_url, "https://cdn.example.com/ep2.mp3?x=1&y=2")
        self.assertEqual(select_episodes(episodes, 1, 1), [episodes[1]])
        self.assertEqual(select_episodes(episodes, 2, 1), [episodes[0]])

    def test_duration_parser_handles_common_formats(self):
        self.assertEqual(parse_duration("90"), 90)
        self.assertEqual(parse_duration("01:30"), 90)
        self.assertEqual(parse_duration("1:01:01"), 3661)
        self.assertEqual(parse_duration("unknown"), 0)


if __name__ == "__main__":
    unittest.main()
