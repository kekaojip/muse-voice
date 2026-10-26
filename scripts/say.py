#!/usr/bin/env python3
"""Volcano Engine OpenSpeech TTS (seed-tts-2.0) — portable helper.

Part of the muse-voice skill. Reads narration text from a file, synthesizes
it with the user's own Volcano API key, and saves an MP3 plus a metadata
sidecar. The key is never stored in this file: it comes from the
VOLCENGINE_API_KEY environment variable (see .env.example).

Setup:
  cp .env.example .env   # then fill in your key
  export $(grep -v '^#' .env | xargs)   # or use direnv / your shell

Usage:
  python3 say.py --text-file hello.txt --output hello.mp3
  python3 say.py --text-file hello.txt --output hello.mp3 --speaker zh_female_sajiaoxuemei_uranus_bigtts
  python3 say.py --text-file hello.txt --output hello.mp3 --dry-run

Defaults: resource seed-tts-2.0, speaker zh_female_sajiaoxuemei_uranus_bigtts
(sweet female voice), mp3 at 24000 Hz. Text limit 1500 characters per call.
Get your key at https://www.volcengine.com/ — console > 语音合成 >
create an app, enable seed-tts-2.0, copy the API key.
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
RESOURCE = "seed-tts-2.0"
DEFAULT_SPEAKER = "zh_female_sajiaoxuemei_uranus_bigtts"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def main() -> int:
    parser = argparse.ArgumentParser(description="Volcano OpenSpeech TTS")
    parser.add_argument("--text-file", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--speaker", default=os.environ.get("MUSE_VOICE_SPEAKER", DEFAULT_SPEAKER))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    api_key = os.environ.get("VOLCENGINE_API_KEY", "").strip()
    if not api_key and not args.dry_run:
        print("TTS failed: VOLCENGINE_API_KEY is not set. Copy .env.example "
              "to .env, fill in your Volcano API key, and export it.",
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
            "resource": RESOURCE, "text_sha256": text_hash,
            "output": args.output,
        }, ensure_ascii=False))
        return 0

    payload = {
        "user": {"uid": "muse-voice"},
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
    request.add_header("X-Api-Key", api_key)
    request.add_header("X-Api-Request-Id", request_id)
    request.add_header("X-Api-Resource-Id", RESOURCE)
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
        "complete": True, "request_id": request_id, "resource": RESOURCE,
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
