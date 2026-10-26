# Voices (seed-tts-2.0 preset + seed-icl-2.0 cloned, verified against the live API on 2026-10-26)

Set one in `.env` as `MUSE_VOICE_SPEAKER`.

| Speaker ID | Label | Style |
|---|---|---|
| `zh_female_sajiaoxuemei_uranus_bigtts` | 撒娇学妹 (default) | Sweet, playful female |
| `zh_female_tianmeixiaoyuan_uranus_bigtts` | 甜美校园 | Sweet campus female |
| `zh_female_wenrouxiaoya_uranus_bigtts` | 温柔小雅 | Gentle female |
| `zh_male_liufei_uranus_bigtts` | 刘飞 | Male narrator — best for video narration |

How to pick: synthesize the same sentence with each (`scripts/say.py
--speaker <id>`) and listen. The agent should remember the user's pick.

## Custom / cloned voices

Clone a voice in the Volcano console (豆包语音控制台 → 体验中心 →
声音复刻, upload 10–30s of clean speech) and you get a speaker ID
starting with `S_`. `scripts/say.py` auto-selects the resource:
preset voices use `seed-tts-2.0`, `S_*` voices use `seed-icl-2.0` —
enable **both** models in the console or cloned voices fail
(`55000000` resource mismatch, or HTTP 403 before the model is
enabled; authorization can take a few minutes to take effect).

Example: `personas/girlfriend.json` in this repo points at
`S_58godekj2` (女友音), a voice cloned from the author's own video —
it only works with the author's Volcano account. To use your own
cloned voice, replace the `voice` field with your own `S_*` ID.
