from __future__ import annotations

import importlib
import os
import shlex
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DependencySpec:
    component: str
    modules: tuple[str, ...] = ()
    commands: tuple[str, ...] = ()


SENSEVOICE_MODULES = ("funasr", "modelscope", "torch", "torchaudio")
VIDEO_COMMANDS = ("ffmpeg", "ffprobe")


def dependency_spec_for_source(platform: str, source: str) -> DependencySpec:
    if platform == "podcast":
        if Path(source).expanduser().is_file():
            return DependencySpec("local-audio", ("faster_whisper",))
        return DependencySpec("podcast", ("faster_whisper",), ("curl",))
    if platform == "douyin":
        return DependencySpec("douyin", SENSEVOICE_MODULES, ("curl", "ffmpeg"))
    if platform == "wechat-channels":
        return DependencySpec("wechat-channels", SENSEVOICE_MODULES, ("ffmpeg", "ffprobe"))
    return DependencySpec(
        platform,
        SENSEVOICE_MODULES + ("yt_dlp",),
        VIDEO_COMMANDS,
    )


def dependency_spec_for_rss(download_only: bool, transcribe_only: bool) -> DependencySpec:
    if download_only:
        return DependencySpec("rss-download", commands=("curl",))
    return DependencySpec("rss", ("faster_whisper",), ("curl",))


def _powershell_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def install_command(component: str, platform: str | None = None) -> str:
    skill_dir = Path(__file__).resolve().parents[2]
    platform = platform or os.name
    if platform == "nt":
        script = _powershell_quote(str(skill_dir / "install.ps1"))
        return (
            "powershell -NoProfile -ExecutionPolicy Bypass "
            f"-File {script} -Component {_powershell_quote(component)}"
        )
    return f"bash {shlex.quote(str(skill_dir / 'install.sh'))} --component {shlex.quote(component)}"


def ensure_opencli() -> None:
    if shutil.which("opencli") is not None:
        return
    raise RuntimeError(
        "OpenCLI is required for Douyin account mode. Install OpenCLI, connect the "
        "Browser Bridge, then run: opencli doctor"
    )


def ensure_dependencies(spec: DependencySpec) -> None:
    missing_modules = []
    for name in spec.modules:
        try:
            importlib.import_module(name)
        except (ImportError, OSError):
            missing_modules.append(name)
    missing_commands = [name for name in spec.commands if shutil.which(name) is None]
    if not missing_modules and not missing_commands:
        return

    missing = []
    if missing_modules:
        missing.append(f"Python modules: {', '.join(missing_modules)}")
    if missing_commands:
        missing.append(f"system commands: {', '.join(missing_commands)}")
    raise RuntimeError(
        f"Missing dependencies for {spec.component} ({'; '.join(missing)}). "
        f"Install this component with: {install_command(spec.component)}"
    )
