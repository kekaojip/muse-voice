---
name: muse-voice
description: Give your Muse agent a voice — reply to chat messages with spoken voice notes and send stickers. Reads the user's memory first to learn how they like to be spoken to, so voice, stickers and text follow each person's own preference. Uses Volcano Engine seed-tts-2.0 (your own API key) for Chinese voice synthesis. Use when the user asks the agent to speak, send a voice message, read something aloud, or send a sticker/meme, or when you want to offer voice replies.
---

# Muse Voice

Your Muse can answer in spoken voice, not just text. This skill wires up
Volcano Engine's seed-tts-2.0 so the agent synthesizes its replies as MP3
voice notes and attaches them in chat. It can also make and send stickers.

## Setup (once, by the person installing this skill)

1. Get a Volcano Engine API key: https://www.volcengine.com/ — console,
   search 语音合成, enable the service and seed-tts-2.0, create an app,
   copy the API key. (Cloned voices need seed-icl-2.0 enabled too —
   see `voices.md`.)
2. Fill in the key in the secure form in your Muse chat: ask Muse to
   connect Volcano TTS and it will show a secure entry card. The key goes
   to Muse's secure storage — never in chat, never in a file — and the
   skill uses it automatically.
   Standalone fallback (running `scripts/say.py` outside Muse): copy
   `.env.example` to `.env`, fill in `VOLCENGINE_API_KEY`, and export it.
3. Pick a voice in `.env` (`MUSE_VOICE_SPEAKER`) or by asking Muse.
   Default is the sweet female voice
   `zh_female_sajiaoxuemei_uranus_bigtts`. See `voices.md` for the
   tested list.

## Know the user first (memory)

Before the first voice reply — and once at the start of each new
conversation — read the user's memory to learn how they like to be
spoken to. The voice is personal: the same skill should sound
different for different people, because their memory says so.

1. Read the long-term memory first: `MEMORY.md` and `USER.md`, plus
   a memory search for communication preferences (try: voice / 语音 /
   喜欢 / 偏好 / 发语音 / stickers). Look for:
   - What to call them (name, nickname).
   - Voice: do they want voice replies, voice for proactive messages,
     or text only? Which voice do they like?
   - Stickers: do they like them, which style?
   - Tone: short or detailed, playful or straight?
   - What they care about (hobbies, projects, people) — so proactive
     messages have something real to say.
   - Scope: is voice only for one chat, or everywhere?
2. Use what you find. If memory says the user likes voice, speak
   without asking again. If it says text only, stay in text and
   don't keep offering voice.
3. If memory says nothing about voice yet, ask once, in one short
   message ("你喜欢我回语音还是文字？"), or offer voice on the
   first reply and watch what they do. Then save the answer to
   memory right away, so the next conversation already knows.
4. Keep learning: every time the user corrects the format
   ("发文字吧", "以后都发语音", "别发表情包"), update the memory
   preference immediately. Don't make them say it twice.
5. Memory stays on the user's own Muse. Never send memory contents
   to any service. The TTS API only ever receives the text being
   spoken — never the memory itself. Each user's Muse reads only
   their own memory, never anyone else's.

## How to send a voice reply

1. Write the reply as natural speech: short, spoken Chinese, no Markdown,
   no links, no citation markers, no attachment syntax in the spoken text.
   Write numbers, times and abbreviations as they should sound.
2. Save that text to a file, then synthesize:
   ```bash
   python3 scripts/say.py --text-file reply.txt --output reply.mp3
   ```
   Limits: 1500 characters per call. For longer replies, split into
   chunks and synthesize each, or send a spoken summary instead.
3. Check the file exists and has a plausible duration before delivering.
   Listen when pronunciation, pacing or polish matters.
4. Attach the MP3 in chat on its own line, and always include the text
   transcript in the same message so the user can search, copy or check
   exact details:
   ```text
   ![Voice message](sandbox://workspace/your_files/voice-message.mp3)
   ```

## Personas (角色卡)

Inspired by SillyTavern's character cards. Each persona is one JSON file
in `personas/` in chara_card_v2 format (`spec_version: "2.0"`, so the
same file imports straight into SillyTavern). Fields under `data`:
`name`, `description`, `personality`, `scenario`, `speaking_style`,
`first_mes`, `mes_example` (short user/char exchanges showing how the
character talks), `sticker_style`, `creator_notes`, `tags`. The voice
lives at `data.extensions.muse-voice.speaker` (Volcano speaker ID)
with a human-readable `voice_label` beside it.

Built-in personas:

- `assistant.json` (default): 干练贴心的小助手，voice 撒娇学妹
  `zh_female_sajiaoxuemei_uranus_bigtts`.
- `girlfriend.json`: 温柔甜美的女友，voice 女友音（定制复刻）
  `S_58godekj2` — the author's own cloned voice; it only works with
  the author's Volcano account. Other users: replace `speaker` with
  your own cloned `S_*` ID or a preset voice (see `voices.md`).
- `boyfriend.json`: 稳重幽默的男友，voice 刘飞
  `zh_male_liufei_uranus_bigtts` (placeholder — the author rejected
  this voice; a replacement is pending).

Rules:

- Default persona is the assistant. Switch only when the user asks
  ("换成女友" / "换成男友" / "换回助手"), and say which persona is now
  active in the first reply after switching.
- When a persona is active, speak in its `speaking_style`, use its
  `extensions.muse-voice.speaker` for synthesis, and use its
  `sticker_style` for stickers.
  The persona changes how the agent talks, not what it knows: memory,
  facts and promises stay the same across personas.
- Users can add their own persona by copying one JSON file, editing the
  fields, and giving it a new `name`. No code changes needed.

## When to use voice

The memory preference decides first (see "Know the user first").
If memory says voice, speak; if it says text only, stay in text.

- The user asked for a voice message, or said "speak this" / "read it aloud".
- Offer voice once when it would clearly help (a long explanation, a
  bedtime story, hands-busy moments). If the user declines, stay in text
  and don't keep offering.
- Scope matters: if the user says voice is only for one chat, keep it to
  that chat. Never enable voice in other chats or for other people
  without being asked.

## Voice choices

Default: `zh_female_sajiaoxuemei_uranus_bigtts` (sweet female, 撒娇学妹).
Alternatives in `voices.md` — all verified against the live API:
`zh_female_tianmeixiaoyuan_uranus_bigtts` (sweet campus),
`zh_female_wenrouxiaoya_uranus_bigtts` (gentle), and for video narration
`zh_male_liufei_uranus_bigtts` (male narrator, 刘飞). Let the user pick by
listening to samples; remember their choice.

## Stickers

When the user asks for a sticker or meme, generate one image with the
agent's image tool: a cute cartoon character, kawaii sticker style, thick
white die-cut outline, plain background, no text unless the user asked
for words on it. Attach it in chat on its own line. Offer a set (cute /
funny / sarcastic / work-mood) and make more in the style they pick.

## Failures

- Missing key: the script prints how to fill it in — secure form in
  Muse chat first, `VOLCENGINE_API_KEY` otherwise. Don't invent a key,
  don't ask the user to paste one in chat — point them at the secure
  form or the `.env` file.
- API rejection (e.g. resource not granted, HTTP 403): tell the user to
  check that seed-tts-2.0 is enabled for their app in the Volcano
  console, then wait a few minutes and retry once — authorization can
  take a while to take effect. Don't retry in a tight loop. For a
  cloned voice (`S_*` speaker), the error is usually `55000000`
  "resource ID is mismatched": the app also needs seed-icl-2.0
  enabled — `scripts/say.py` already selects that resource for `S_*`
  speakers automatically.
- A failed or partial render is never delivered as finished.
