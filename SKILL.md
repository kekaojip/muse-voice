---
name: muse-voice
description: 让你的 Muse 助手开口说话——用语音消息回复聊天、发表情包。先读用户的记忆，了解每个人喜欢怎么被回复，语音、表情包还是文字都按个人的偏好来。还能主动开口，比如用户约好的早上问候或提醒。用火山引擎 seed-tts-2.0（你自己的 API key）合成中文语音。用户让助手说话、发语音消息、念一段文字、发表情包，或者你想提供语音回复时用这个 skill。
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

## Preference record (偏好记录）

Memory tells you what the user likes; the preference record is where
you keep it, in one place, so you don't have to re-read everything
to decide how to answer. It lives in the user's long-term memory —
not in the repo, not in a shared file — because every user has their
own. Copy the shape from `preferences.example.json`.

Fields:
- `name`: what to call them.
- `voice_mode`: `always` (voice for replies and proactive messages),
  `replies` (voice only when replying), `proactive-only` (voice only
  for messages the agent starts), `never` (text only).
- `voice_speaker`: the Volcano speaker ID to use — a preset voice or
  their own cloned `S_*` ID.
- `stickers`: `yes` / `no`, plus `sticker_style` when yes.
- `tone`: `short` / `detailed`, `playful` / `straight`.
- `scope`: which chats voice is allowed in (`this chat only` /
  `everywhere`).
- `persona`: which persona is active (`assistant` by default).
- `proactive`: what proactive messages they asked for (greeting time,
  reminders), or `none`.

Rules:
- Write the record after the first answer about voice, and update it
  every time the user corrects the format. A correction ("发文字吧",
  "以后都发语音") overrides the stored value immediately — don't
  make them say it twice.
- Latest explicit statement wins. An explicit instruction beats an
  inferred one; mark inferred values as inferred and confirm them
  when you get the chance.
- Don't record one-offs as preferences: "这次发语音" is a single
  request, not a new default.
- Keep voice choice and voice mode separate: which voice to use and
  whether to speak at all are two different fields. A user can love
  a voice and still want text in a given chat.
- Never store secrets, keys, or other people's preferences here.
- Read the record at the start of each conversation (see "Know the
  user first") and decide the format of every message from it.

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

## Proactive voice (主动发语音）

Voice isn't only for replies. The agent can also start the
conversation — and when it does, it can speak.

When to initiate:
- The user asked for it: a morning greeting, a reminder ("提醒我还
  分期乐"), a daily briefing, a check-in.
- Something the user cares about happened: a price hit their level,
  a reply arrived, a scheduled event is near. Only if memory says
  they want to hear about it.
- Never initiate to fill silence. No "just checking in" voice notes
  out of nowhere, and never stack them: if the user hasn't replied
  to the last proactive message, don't send another one.

How to do it:
1. Read memory first (see "Know the user first"): the proactive
   message must be about something real — their schedule, their
   holdings, their people — not a generic greeting.
2. Check the voice preference. If memory says text only, the
   proactive message is text. If it says voice, speak.
3. Keep it short: one or two sentences. A proactive voice note is
   an interruption — long ones are rude.
4. Synthesize with `scripts/say.py` exactly like a reply, attach
   the MP3, and always include the text transcript.
5. Match the format to the content: greetings and good news suit
   voice; anything the user must read carefully (numbers, links, a
   decision) goes in text first, voice optional.

Setting it up (scheduled proactive voice):
- A scheduled job (cron) runs an agent turn at the agreed time.
  That turn composes the message from memory, synthesizes it with
  `scripts/say.py`, and delivers it to the chat.
- Example: a morning greeting at 08:00 every day — the job reads
  memory for today's schedule, writes one or two spoken sentences,
  synthesizes, and sends voice + transcript.
- Only set up schedules the user explicitly asked for. Say the time
  and the content out loud when confirming, and let them cancel with
  one sentence.

## When to use voice

The memory preference decides first (see "Know the user first").
If memory says voice, speak; if it says text only, stay in text.
For starting a conversation yourself, see "Proactive voice" above.

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

Check pre-installed packs first: `stickers/packs/<pack>/` holds the
image files plus a `manifest.json` (`pack`, `name`, `source`, and a
`stickers` list of `file` / `label` / `mood` / `keywords`). Pick the
sticker whose label or keywords match the moment (greeting, yes, laugh,
speechless...) and attach it on its own line.

To install a pack, run `scripts/fetch-stickers.sh <pack>` — it fetches
that category from ChineseBQB (zhaoolee/ChineseBQB, open data source)
and builds the manifest. Built-in pack: `huaji` (滑稽大佬, 125 stickers).
Images are fetched on demand, not bundled in the repo, so the repo stays
light. Only fetch packs you are comfortable redistributing — ChineseBQB
collects images from the internet and has no LICENSE file, and some
categories contain copyrighted characters or real people's faces.

To add the user's own stickers: save the images they send into
`stickers/packs/<pack>/` and run
`python3 scripts/make-sticker-manifest.py <pack_dir> <pack_id> <pack_name>`.

### Sending principles

- Don't send one on every message. Send a sticker when the moment
  calls for it — a greeting, a reaction, encouragement, a joke that
  landed, or answering a sticker the user sent — or at random in casual
  conversation. Don't overthink the choice: a close-enough one is fine,
  and when nothing fits, any pack sticker will do.
- One at a time: at most one sticker per message, never a burst.
- Packs only, never generate: pick the closest match from installed
  packs by label / keywords / mood; if nothing fits, send any sticker
  from the packs. Never generate a sticker image — drawing is forbidden.
- Stay in character: the sticker must match the current persona
  (assistant / girlfriend / boyfriend) — never mix styles across
  personas.
- Follow the preference record: if the user's record says no stickers,
  send none. If it says yes, stickers follow their `sticker_style`.
- Never replace substance: numbers, links, decisions and answers stay
  in text. A sticker goes alongside the message, never instead of it.
- Don't repeat: never send the same sticker twice in a short while.
- Stay restrained when it's serious: money, bad news, decisions — no
  sticker to brush it off, unless the user is joking first.
- When the user sends a sticker, read the mood and answer in kind, but
  don't mirror automatically.

If no pack fits, send any sticker from the installed packs — never
generate one. Drawing sticker images is forbidden.

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
