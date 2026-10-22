#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SKILL_DIR/.venv"
PYTHON="${PYTHON:-python3}"

usage() {
  cat <<'EOF'
Usage:
  bash install.sh                       # interactive menu in a terminal; all otherwise
  bash install.sh --all                 # install every component
  bash install.sh --component NAME      # install one component; repeatable
  bash install.sh --check [selection]   # check all or selected components
  bash install.sh --help

Components:
  video        All supported video platforms
  douyin       Douyin video transcription
  bilibili     Bilibili video transcription
  tiktok       TikTok video transcription
  weibo        Weibo video transcription
  zhihu        Zhihu video transcription
  youtube      YouTube video transcription
  wechat-channels WeChat Channels single-video transcription
  wechat-yuanbao Isolated Tencent Yuanbao fallback for WeChat Channels
  podcast      Remote podcast/audio transcription
  rss          RSS download and transcription
  local-audio  Local audio transcription
  rss-download RSS audio download only
EOF
}

fail_usage() {
  echo "error: $1" >&2
  usage >&2
  exit 2
}

format_command() {
  local result="" arg quoted
  for arg in "$@"; do
    quoted="${arg//\\/\\\\}"
    quoted="${quoted//\"/\\\"}"
    quoted="${quoted//\$/\\\$}"
    quoted="${quoted//\`/\\\`}"
    result="${result:+$result }\"$quoted\""
  done
  printf '%s' "$result"
}

add_command() {
  case " $COMMANDS " in
    *" $1 "*) ;;
    *) COMMANDS="${COMMANDS:+$COMMANDS }$1" ;;
  esac
}

choose_interactively() {
  cat <<'EOF'
Select components to install (comma or space separated):
  1) all           Everything
  2) video         All video platforms
  3) douyin        Douyin
  4) bilibili      Bilibili
  5) tiktok        TikTok
  6) weibo         Weibo
  7) zhihu         Zhihu
  8) youtube       YouTube
  9) wechat-channels WeChat Channels
 10) wechat-yuanbao Isolated Tencent Yuanbao fallback
 11) podcast       Remote podcast/audio
 12) rss           RSS download and transcription
 13) local-audio   Local audio only
 14) rss-download  RSS download only
EOF
  printf "Selection: "
  local answer item
  local selections=()
  read -r answer || fail_usage "no component selected"
  IFS=$' \t\n,' read -r -a selections <<< "$answer"
  ((${#selections[@]})) || fail_usage "no component selected"
  for item in "${selections[@]}"; do
    case "$item" in
      1|all) SELECT_ALL=true ;;
      2|video) COMPONENTS+=("video") ;;
      3|douyin) COMPONENTS+=("douyin") ;;
      4|bilibili) COMPONENTS+=("bilibili") ;;
      5|tiktok) COMPONENTS+=("tiktok") ;;
      6|weibo) COMPONENTS+=("weibo") ;;
      7|zhihu) COMPONENTS+=("zhihu") ;;
      8|youtube) COMPONENTS+=("youtube") ;;
      9|wechat-channels) COMPONENTS+=("wechat-channels") ;;
      10|wechat-yuanbao) COMPONENTS+=("wechat-yuanbao") ;;
      11|podcast) COMPONENTS+=("podcast") ;;
      12|rss) COMPONENTS+=("rss") ;;
      13|local-audio) COMPONENTS+=("local-audio") ;;
      14|rss-download) COMPONENTS+=("rss-download") ;;
      *) fail_usage "unknown selection: $item" ;;
    esac
  done
}

CHECK_ONLY=false
SELECT_ALL=false
COMPONENTS=()

while (($#)); do
  case "$1" in
    --all)
      SELECT_ALL=true
      shift
      ;;
    --component)
      (($# >= 2)) || fail_usage "--component requires a name"
      COMPONENTS+=("$2")
      shift 2
      ;;
    --check)
      CHECK_ONLY=true
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      fail_usage "unknown option: $1"
      ;;
  esac
done

if ! $SELECT_ALL && ((${#COMPONENTS[@]} == 0)); then
  if $CHECK_ONLY || [[ ! -t 0 ]]; then
    SELECT_ALL=true
  else
    choose_interactively
  fi
fi

NORMALIZED=()
if ((${#COMPONENTS[@]})); then
  for component in "${COMPONENTS[@]}"; do
    case "$component" in
      all) SELECT_ALL=true ;;
      video|douyin|bilibili|tiktok|weibo|zhihu|youtube|wechat-channels|wechat-yuanbao|podcast|rss|local-audio|rss-download)
        NORMALIZED+=("$component")
        ;;
      *) fail_usage "unknown component: $component" ;;
    esac
  done
  COMPONENTS=("${NORMALIZED[@]}")
fi
if $SELECT_ALL && ((${#COMPONENTS[@]})); then
  fail_usage "--all cannot be combined with another component"
fi
if $SELECT_ALL; then
  COMPONENTS=("all")
fi

NEED_SENSEVOICE=false
NEED_WHISPER=false
NEED_DOWNLOADERS=false
NEED_YUANBAO=false
COMMANDS=""

for component in "${COMPONENTS[@]}"; do
  case "$component" in
    all|video)
      NEED_SENSEVOICE=true
      NEED_DOWNLOADERS=true
      add_command curl
      add_command ffmpeg
      add_command ffprobe
      [[ "$component" == "all" ]] && NEED_WHISPER=true
      ;;
    douyin)
      NEED_SENSEVOICE=true
      add_command curl
      add_command ffmpeg
      ;;
    bilibili|tiktok|weibo|zhihu|youtube)
      NEED_SENSEVOICE=true
      NEED_DOWNLOADERS=true
      add_command ffmpeg
      add_command ffprobe
      ;;
    wechat-channels)
      NEED_SENSEVOICE=true
      add_command ffmpeg
      add_command ffprobe
      ;;
    wechat-yuanbao)
      NEED_YUANBAO=true
      ;;
    podcast|rss)
      NEED_WHISPER=true
      add_command curl
      ;;
    local-audio)
      NEED_WHISPER=true
      ;;
    rss-download)
      add_command curl
      ;;
  esac
done

INSTALL_ARGS=(bash "$SKILL_DIR/install.sh")
if [[ "${COMPONENTS[0]}" == "all" ]]; then
  INSTALL_ARGS+=(--all)
else
  for component in "${COMPONENTS[@]}"; do
    INSTALL_ARGS+=(--component "$component")
  done
fi
INSTALL_COMMAND="$(format_command "${INSTALL_ARGS[@]}")"

missing=()
for command in $COMMANDS; do
  command -v "$command" >/dev/null 2>&1 || missing+=("$command")
done
if ((${#missing[@]})); then
  packages=""
  for command in "${missing[@]}"; do
    case "$command" in
      ffmpeg|ffprobe) package="ffmpeg" ;;
      *) package="$command" ;;
    esac
    case " $packages " in
      *" $package "*) ;;
      *) packages="${packages:+$packages }$package" ;;
    esac
  done
  echo "Missing system commands: ${missing[*]}" >&2
  echo "macOS: brew install $packages" >&2
  echo "Debian/Ubuntu: sudo apt-get install $packages" >&2
  exit 1
fi

if [[ ! -x "$VENV/bin/python" ]]; then
  if $CHECK_ONLY; then
    echo "Missing .venv. Install the selected components with: $INSTALL_COMMAND" >&2
    exit 1
  fi
  if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Missing python3. Install Python 3.9 or newer." >&2
    exit 1
  fi
  "$PYTHON" - <<'PY'
import sys
if sys.version_info < (3, 9):
    raise SystemExit("Python 3.9 or newer is required")
PY
  "$PYTHON" -m venv "$VENV"
fi

if ! "$VENV/bin/python" - <<'PY'
import sys
if sys.version_info < (3, 9):
    raise SystemExit("The existing .venv uses Python older than 3.9; remove it and reinstall.")
PY
then
  exit 1
fi

PIP_ARGS=()
$NEED_SENSEVOICE && PIP_ARGS+=(-r "$SKILL_DIR/requirements/sensevoice.txt")
$NEED_WHISPER && PIP_ARGS+=(-r "$SKILL_DIR/requirements/whisper.txt")
$NEED_DOWNLOADERS && PIP_ARGS+=(-r "$SKILL_DIR/requirements/downloaders.txt")
$NEED_YUANBAO && PIP_ARGS+=(-r "$SKILL_DIR/requirements/yuanbao.txt")
if ! $CHECK_ONLY && ((${#PIP_ARGS[@]})); then
  "$VENV/bin/python" -m pip install "${PIP_ARGS[@]}"
fi

if ! "$VENV/bin/python" - "$NEED_SENSEVOICE" "$NEED_WHISPER" "$NEED_DOWNLOADERS" "$NEED_YUANBAO" <<'PY'
import importlib
import sys

need_sensevoice, need_whisper, need_downloaders, need_yuanbao = (value == "true" for value in sys.argv[1:])
modules = []
if need_sensevoice:
    modules.extend(("funasr", "modelscope", "torch", "torchaudio"))
if need_whisper:
    modules.append("faster_whisper")
if need_downloaders:
    modules.append("yt_dlp")
if need_yuanbao:
    modules.append("websocket")

failed = []
for name in modules:
    try:
        importlib.import_module(name)
    except (ImportError, OSError) as exc:
        failed.append(f"{name}: {exc}")
if failed:
    raise SystemExit("Missing or unusable Python dependencies:\n  " + "\n  ".join(failed))
print("Selected Python dependencies: OK")
PY
then
  echo "Install or repair the selected components with: $INSTALL_COMMAND" >&2
  exit 1
fi

if [[ -n "$COMMANDS" ]]; then
  echo "Selected system commands: OK ($COMMANDS)"
else
  echo "Selected system commands: none required"
fi
echo "Components ready: ${COMPONENTS[*]}"
echo "Run: $(format_command "$VENV/bin/python" "$SKILL_DIR/scripts/transcribe.py" --help)"
