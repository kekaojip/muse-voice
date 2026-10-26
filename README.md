# muse-voice

让你的 Muse 开口说话。一个 skill，让 Muse 助手用语音消息回复聊天，还能发表情包。

## 能做什么

- **语音回复**：助手用火山引擎 seed-tts-2.0 说中文回复，默认音色撒娇学妹（甜美女声）。MP3 以语音消息发出，每条都附文字稿。
- **表情包**：只用预装包（按心情从包清单里挑，挑不到就随便发一张包里的——绝不现画）。自带下载脚本，可以从 ChineseBQB 的开放数据源安装表情包，比如 `huaji`（滑稽大佬，125 张）。
- **懂记忆**：先读你的 Muse 记忆，知道你喜欢怎么被回复——语音、表情包还是文字——不用每次都问。
- **主动语音**：不只会回你，还能主动开口，比如你约好的早上问候或提醒。
- **偏好记录**：每人一份记录——语音还是文字、用哪个声音、要不要表情包——存在他自己的记忆里，格式跟着他走，不用问第二遍。

## 安装（3 步）

skills.sh 上有收录：https://skills.sh/kekaojip/muse-voice/muse-voice

1. 克隆仓库并安装 skill：
   ```bash
   git clone https://github.com/kekaojip/muse-voice.git
   npx skills add kekaojip/muse-voice -g
   ```
   或者把文件夹拷到 `~/.claude/skills/muse-voice`。
2. 拿一个火山引擎 API key：https://www.volcengine.com/ —— 控制台搜「语音合成」，开通服务和 seed-tts-2.0，建应用、复制 API key。（用克隆音色？还要开通 seed-icl-2.0 —— 见 `voices.md` 里的“Custom / cloned voices”。）
3. 在 Muse 对话里的安全表单填 key：让 Muse 连接 Volcano TTS，它会弹出安全录入卡。Key 存在 Muse 的安全存储里——不在聊天里，不在文件里。（在 Muse 之外跑脚本？把 `.env.example` 拷成 `.env`，填 `VOLCENGINE_API_KEY`。）

好了。让你的 Muse“给我发条语音”，它就会说话。Key 是你自己的——TTS 费用走你自己的火山账号，Key 不会离开安全存储（或你自己的 `.env`）。

## 角色卡（Personas）

`personas/` 里有三张内置角色卡，每种角色一个 JSON，chara_card_v2 格式（`spec_version: "2.0"`，可以直接导入 SillyTavern），音色在 `data.extensions.muse-voice.speaker`，还有表情包风格：

- **助手**（`assistant.json`，默认）：干练贴心，音色撒娇学妹。
- **女友**（`girlfriend.json`）：温柔甜美，音色女友音（定制复刻 `S_58godekj2`，作者自己克隆的声音，只在作者账号上可用；换成自己的复刻音色见 `voices.md`）。
- **男友**（`boyfriend.json`）：稳重幽默，音色刘飞（占位，待替换）。

一句话切换（“换成女友”）。想加自己的角色，复制一个 JSON 改字段就行——不用改代码。

## 试一下

```bash
echo "你好呀，我是你的小助手。" > hello.txt
python3 scripts/say.py --text-file hello.txt --output hello.mp3
```

## 说明

- 单次合成限 1500 字；长回复先分段或概括再说。
- 每个对话默认都是文字模式——只在用户要求的地方才发语音。
- Muse 本身是 Meta 的产品，不在这个仓库里。这个 skill 只是教 Muse 助手用你自己的 TTS key 说话。
