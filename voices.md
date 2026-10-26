# Voices (seed-tts-2.0, verified against the live API on 2026-10-26)

Set one in `.env` as `MUSE_VOICE_SPEAKER`.

| Speaker ID | Label | Style |
|---|---|---|
| `zh_female_sajiaoxuemei_uranus_bigtts` | 撒娇学妹 (default) | Sweet, playful female |
| `zh_female_tianmeixiaoyuan_uranus_bigtts` | 甜美校园 | Sweet campus female |
| `zh_female_wenrouxiaoya_uranus_bigtts` | 温柔小雅 | Gentle female |
| `zh_male_liufei_uranus_bigtts` | 刘飞 | Male narrator — best for video narration |

How to pick: synthesize the same sentence with each (`scripts/say.py
--speaker <id>`) and listen. The agent should remember the user's pick.
