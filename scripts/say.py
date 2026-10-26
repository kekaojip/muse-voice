#!/usr/bin/env python3
"""Volcano Engine OpenSpeech TTS (seed-tts-2.0) — portable helper.

Part of the muse-voice-chat skill. Reads narration text from a file, synthesizes
it with the user's own Volcano API key, and saves an MP3 plus a metadata
sidecar. The key is never stored in this file and never pasted in chat.

How the key is provided (first match wins):
  1. Inside Muse (recommended): fill the key in the secure form in your
     Muse chat. Muse stores it in secure storage and this script uses it
     through the custom.volcengine-openspeech credential — no key in any
     file, no key in chat.
  2. Standalone fallback: set the VOLCENGINE_API_KEY environment variable
     (see .env.example).

Setup (standalone only):
  cp .env.example .env   # then fill in your key
  export $(grep -v '^#' .env | xargs)   # or use direnv / your shell

Usage:
  python3 say.py --text-file hello.txt --output hello.mp3
  python3 say.py --text-file hello.txt --output hello.mp3 --speaker zh_female_sajiaoxuemei_uranus_bigtts
  python3 say.py --text-file hello.txt --output hello.mp3 --dry-run

Defaults: speaker zh_female_sajiaoxuemei_uranus_bigtts
(sweet female voice), mp3 at 24000 Hz. Text limit 1500 characters per call.
Resource is auto-selected: preset voices use seed-tts-2.0, console-cloned
voices (speaker IDs starting with "S_") use seed-icl-2.0 — enable both
models in the console or cloned voices fail (see README).
Get your key at https://www.volcengine.com/ — console > 语音合成 >
create an app, enable seed-tts-2.0 (and seed-icl-2.0 for cloned voices),
copy the API key.
"""
import argparse
import base64
import hashlib
import json
import os
import sys
import uuid
import urllib.request

URL = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"
ALLOWED_HOSTS = ["openspeech.bytedance.com"]
# Preset voices use seed-tts-2.0; voices cloned in the Volcano console
# (speaker IDs starting with "S_") use seed-icl-2.0. The console models
# must both be enabled for the app's API key, or the service rejects the
# call (55000000 resource mismatch / HTTP 403).
RESOURCE_PRESET = "seed-tts-2.0"
RESOURCE_CLONED = "seed-icl-2.0"
DEFAULT_SPEAKER = "zh_female_sajiaoxuemei_uranus_bigtts"


def resource_for_speaker(speaker: str) -> str:
    return RESOURCE_CLONED if speaker.startswith("S_") else RESOURCE_PRESET
# Muse secure-storage credential name (used when no env key is set).
CREDENTIAL = "custom.volcengine-openspeech"


def _secure_key_available() -> bool:
    """True when Muse's secure credential store can supply the key."""
    try:
        sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
        import dynamic_credentials  # noqa: F401
        return True
    except Exception:
        return False


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def main() -> int:
    parser = argparse.ArgumentParser(description="Volcano OpenSpeech TTS")
    parser.add_argument("--text-file", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--speaker", default=os.environ.get("MUSE_VOICE_SPEAKER", DEFAULT_SPEAKER))
    parser.add_argument("--resource", default=None,
                        help="Override the resource: seed-tts-2.0 for preset "
                             "voices, seed-icl-2.0 for console-cloned (S_*) voices. "
                             "Default: auto-selected from the speaker.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    resource = args.resource or resource_for_speaker(args.speaker)

    api_key = os.environ.get("VOLCENGINE_API_KEY", "").strip()
    use_secure_storage = False
    if not api_key and not args.dry_run:
        if _secure_key_available():
            use_secure_storage = True
        else:
            print("TTS failed: no Volcano API key. In Muse, fill the key in "
                  "the secure form in chat; outside Muse, set "
                  "VOLCENGINE_API_KEY (see .env.example).",
                  file=sys.stderr)
            return 1

    with open(args.text_file, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        print("TTS failed: text is empty.", file=sys.stderr)
        return 1
    if len(text) > 1500:
        print("TTS failed: text over 1500 characters, split it first.", file=sys.stderr)
        return 1
    if not args.output.endswith(".mp3"):
        print("TTS failed: output must have a .mp3 extension.", file=sys.stderr)
        return 1

    request_id = str(uuid.uuid4())
    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if args.dry_run:
        print(json.dumps({
            "dry_run": True, "network_request": False,
            "characters": len(text), "speaker": args.speaker,
            "resource": resource, "text_sha256": text_hash,
            "output": args.output,
        }, ensure_ascii=False))
        return 0

    payload = {
        "user": {"uid": "muse-voice-chat"},
        "req_params": {
            "text": text,
            "speaker": args.speaker,
            "audio_params": {"format": "mp3", "sample_rate": 24000},
        },
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    print(f"One paid TTS request, speaker={args.speaker}, "
          f"characters={len(text)}, request_id={request_id}. No automatic retries.")
    request = urllib.request.Request(URL, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    if use_secure_storage:
        from dynamic_credentials import add_surrogate_to_request
        add_surrogate_to_request(request, CREDENTIAL, allowed_hosts=ALLOWED_HOSTS)
    else:
        request.add_header("X-Api-Key", api_key)
    request.add_header("X-Api-Request-Id", request_id)
    request.add_header("X-Api-Resource-Id", resource)
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=180) as resp:
            raw = resp.read()
    except Exception as exc:
        print(f"TTS transport failed or timed out. Billing may already have "
              f"occurred. Check service logs using request_id={request_id} "
              f"before retrying. ({type(exc).__name__})", file=sys.stderr)
        return 1

    audio = bytearray()
    complete = False
    for line in raw.decode("utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        if complete:
            print("TTS failed: unexpected data after completion.", file=sys.stderr)
            return 1
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            print("TTS failed: malformed response, not saving partial audio.",
                  file=sys.stderr)
            return 1
        code = entry.get("code")
        if code not in (0, 20000000):
            print(f"TTS service rejected the request (code={code}); "
                  f"no retry performed.", file=sys.stderr)
            return 1
        if entry.get("data"):
            try:
                audio.extend(base64.b64decode(entry["data"]))
            except Exception:
                print("TTS failed: invalid audio encoding.", file=sys.stderr)
                return 1
        if code == 20000000:
            complete = True
    if not complete or not audio:
        print("TTS failed: incomplete or empty audio response.", file=sys.stderr)
        return 1

    with open(args.output, "wb") as f:
        f.write(bytes(audio))
    meta = {
        "complete": True, "request_id": request_id, "resource": resource,
        "speaker": args.speaker, "sample_rate": 24000, "format": "mp3",
        "characters": len(text), "text_sha256": text_hash,
        "audio_sha256": hashlib.sha256(bytes(audio)).hexdigest(),
        "needs_listening_review": True,
    }
    with open(args.output + ".json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"Saved: {args.output}. Decode and listen for pronunciation, "
          f"missing words and the ending before delivering.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
