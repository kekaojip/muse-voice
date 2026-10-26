---
name: muse-voice
description: Give your Muse agent a voice — reply to chat messages with spoken voice notes and send stickers. Uses Volcano Engine seed-tts-2.0 (your own API key) for Chinese voice synthesis. Use when the user asks the agent to speak, send a voice message, read something aloud, or send a sticker/meme, or when you want to offer voice replies.
---

# Muse Voice

Your Muse can answer in spoken voice, not just text. This skill wires up
Volcano Engine's seed-tts-2.0 so the agent synthesizes its replies as MP3
voice notes and attaches them in chat. It can also make and send stickers.

## Setup (once, by the person installing this skill)

1. Get a Volcano Engine API key: https://www.volcengine.com/ — console,
   search 语音合成, enable the service and seed-tts-2.0, create an app,
   copy the API key.
2. Copy the example env file and fill in the key (never commit the real key):
   ```bash
   cp .env.example .env
   # edit .env: VOLCENGINE_API_KEY=your-key-here
   export $(grep -v '^#' .env | xargs)
   ```
3. Pick a voice in `.env` (`MUSE_VOICE_SPEAKER`). Default is the sweet
   female voice `zh_female_sajiaoxuemei_uranus_bigtts`. See `voices.md`
   for the tested list.

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
in `personas/` with these fields: `name`, `description`, `personality`,
`scenario`, `speaking_style`, `voice` (Volcano speaker ID), `voice_label`,
`first_message`, `example_dialogue` (short user/char exchanges showing
how the character talks), `sticker_style`.

Built-in personas:

- `assistant.json` (default): 干练贴心的小助手，voice 撒娇学妹
  `zh_female_sajiaoxuemei_uranus_bigtts`.
- `girlfriend.json`: 温柔甜美的女友，voice 甜美校园
  `zh_female_tianmeixiaoyuan_uranus_bigtts`.
- `boyfriend.json`: 稳重幽默的男友，voice 刘飞
  `zh_male_liufei_uranus_bigtts`.

Rules:

- Default persona is the assistant. Switch only when the user asks
  ("换成女友" / "换成男友" / "换回助手"), and say which persona is now
  active in the first reply after switching.
- When a persona is active, speak in its `speaking_style`, use its
  `voice` for synthesis, and use its `sticker_style` for stickers.
  The persona changes how the agent talks, not what it knows: memory,
  facts and promises stay the same across personas.
- Users can add their own persona by copying one JSON file, editing the
  fields, and giving it a new `name`. No code changes needed.

## When to use voice

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

- Missing key: the script prints how to set `VOLCENGINE_API_KEY`. Don't
  invent a key, don't ask the user to paste one in chat — point them at
  the `.env` file.
- API rejection (e.g. resource not granted, HTTP 403): tell the user to
  check that seed-tts-2.0 is enabled for their app in the Volcano
  console, then wait a few minutes and retry once — authorization can
  take a while to take effect. Don't retry in a tight loop.
- A failed or partial render is never delivered as finished.
