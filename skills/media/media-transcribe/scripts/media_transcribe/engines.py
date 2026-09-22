from __future__ import annotations

import re
import time

from .models import Transcript
from .status import StatusReporter


_SENSEVOICE_MARKERS = str.maketrans("", "", "😊😔😡😰🤢😮🎼👏😀😭🤧😷❓")
_TIMESTAMP_LINE = re.compile(
    r"^\[\s*\d+(?:\.\d+)?s\s*->\s*\d+(?:\.\d+)?s\]\s*(.*)$"
)
_SENTENCE = re.compile(r".+?(?:[。！？!?…]+|$)", re.DOTALL)


def paragraphize_video_text(text: str, max_sentences: int = 4, max_chars: int = 180) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"([。！？!?…])(?:[。！？!?…])+", r"\1", compact)
    sentences = [match.group(0).strip() for match in _SENTENCE.finditer(compact) if match.group(0).strip()]
    paragraphs: list[str] = []
    current: list[str] = []
    size = 0
    for sentence in sentences:
        if current and (len(current) >= max_sentences or size + len(sentence) > max_chars):
            paragraphs.append("".join(current))
            current = []
            size = 0
        current.append(sentence)
        size += len(sentence)
    if current:
        paragraphs.append("".join(current))
    return "\n\n".join(paragraphs)


def restore_video_transcript_text(text: str, punc_model=None) -> str:
    segments = []
    for line in text.splitlines():
        match = _TIMESTAMP_LINE.match(line)
        if match and match.group(1).strip():
            segments.append(match.group(1).strip())
    if not segments:
        return text
    raw = "".join(segments)
    if punc_model is None:
        from funasr import AutoModel

        punc_model = AutoModel(
            model="ct-punc",
            device="cpu",
            disable_update=True,
            disable_pbar=True,
        )
    result = punc_model.generate(input=raw)
    punctuated = next(
        (
            item.get("text", "").strip()
            for item in (result or [])
            if isinstance(item, dict) and item.get("text")
        ),
        "",
    )
    if not punctuated:
        raise RuntimeError("Video punctuation restoration returned no text.")
    return paragraphize_video_text(punctuated)


def clean_sensevoice_text(text: str) -> str:
    return text.translate(_SENSEVOICE_MARKERS).strip()


def load_sensevoice_model():
    from funasr import AutoModel

    return AutoModel(
        model="iic/SenseVoiceSmall",
        trust_remote_code=True,
        vad_model="fsmn-vad",
        vad_kwargs={"max_single_segment_time": 30000},
        device="cpu",
        disable_update=True,
        disable_pbar=True,
    )


def transcribe_sensevoice(
    audio_path: str,
    language: str,
    model=None,
    reporter: StatusReporter | None = None,
) -> Transcript:
    from funasr.utils.postprocess_utils import rich_transcription_postprocess

    model = model or load_sensevoice_model()
    started = time.time()

    def progress(current: int, total: int) -> None:
        if reporter and total:
            reporter.detail(f"segment {current}/{total}")

    result = model.generate(
        input=audio_path,
        language=language,
        use_itn=True,
        batch_size_s=60,
        progress_callback=progress,
    )
    texts = [
        clean_sensevoice_text(rich_transcription_postprocess(item["text"]))
        for item in (result or [])
        if item.get("text")
    ]
    text = "\n\n".join(texts).strip()
    if not text:
        raise RuntimeError("Transcription returned no text.")
    detected = language
    if language == "auto":
        compact = re.sub(r"\s+", "", text)
        chinese = len(re.findall(r"[一-鿿]", compact))
        detected = "zh" if chinese / max(len(compact), 1) > 0.3 else "en"
    return Transcript(text, detected, "sensevoice-small", time.time() - started)


def load_whisper_model():
    from faster_whisper import WhisperModel

    return WhisperModel("small", device="cpu", compute_type="int8")


def transcribe_whisper(audio_path: str, model=None) -> Transcript:
    model = model or load_whisper_model()
    started = time.time()
    segments, info = model.transcribe(
        audio_path,
        language=None,
        beam_size=5,
        vad_filter=True,
        log_progress=False,
    )
    lines = [f"[{segment.start:6.1f}s -> {segment.end:6.1f}s] {segment.text.strip()}" for segment in segments]
    if not lines:
        raise RuntimeError("Transcription returned no text.")
    language = getattr(info, "language", None) or "zh"
    return Transcript("\n".join(lines), language, "faster-whisper-small", time.time() - started, lines)
