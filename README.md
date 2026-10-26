# muse-voice

Give your Muse a voice. A skill that lets a Muse agent reply to chat
messages with spoken voice notes — and send stickers.

## What it does

- **Voice replies**: the agent answers in spoken Chinese via Volcano
  Engine seed-tts-2.0, default voice 撒娇学妹 (sweet female). It attaches
  the MP3 as a voice message, always with a text transcript.
- **Stickers**: the agent can generate and send sticker-style images on
  request.
- **Memory-aware**: reads your Muse memory first, so it knows how you
  like to be spoken to — voice, stickers or text — instead of asking
  every time.
- **Proactive voice**: can start the conversation with a spoken
  greeting or reminder you asked for, not just reply to you.

## Install (3 steps)

Listed on skills.sh: https://skills.sh/kekaojip/muse-voice/muse-voice

1. Clone this repo and install the skill:
   ```bash
   git clone https://github.com/kekaojip/muse-voice.git
   npx skills add kekaojip/muse-voice -g
   ```
   Or copy the folder into `~/.claude/skills/muse-voice`.
2. Get a Volcano Engine API key: https://www.volcengine.com/ — console,
   search 语音合成, enable the service and seed-tts-2.0, create an app,
   copy the API key. (Using a cloned voice? Also enable seed-icl-2.0 —
   see "Custom / cloned voices" in `voices.md`.)
3. Fill in the key in the secure form in your Muse chat: ask Muse to
   connect Volcano TTS and it will show a secure entry card. The key is
   stored in Muse's secure storage — never in chat, never in a file.
   (Running the script outside Muse? Copy `.env.example` to `.env` and
   fill in `VOLCENGINE_API_KEY` instead.)

That's it. Ask your Muse to "send me a voice message" and it will speak.
Your key is yours — TTS usage is billed to your own Volcano account,
and the key never leaves secure storage (or your own `.env`).

## Personas (角色卡)

Three built-in personas live in `personas/` — one JSON file each,
in chara_card_v2 format (`spec_version: "2.0"`, importable into
SillyTavern as-is) plus a Volcano voice at
`data.extensions.muse-voice.speaker` and a sticker style:

- **助手** (`assistant.json`, default): 干练贴心，voice 撒娇学妹.
- **女友** (`girlfriend.json`): 温柔甜美，voice 女友音（定制复刻
  `S_58godekj2`，作者自己克隆的声音，只在作者账号上可用；换成
  自己的复刻音色见 `voices.md`）.
- **男友** (`boyfriend.json`): 稳重幽默，voice 刘飞（占位，待替换）.

Switch with one sentence ("换成女友"). Add your own persona by
copying a JSON file and editing the fields — no code changes.

## Test it

```bash
echo "你好呀，我是你的小助手。" > hello.txt
python3 scripts/say.py --text-file hello.txt --output hello.mp3
```

## Notes

- Text limit is 1500 characters per synthesis call; long replies are
  split or summarized before speaking.
- Voice is off by default in every chat — it only speaks where the user
  asked for it.
- Muse itself is Meta's product and is not part of this repo. This skill
  only teaches a Muse agent how to speak using your own TTS key.
