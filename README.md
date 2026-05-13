# cc-notify

Claude Code 任务通知 Skill。当 CC 完成任务、需要权限审批、或遇到错误停止时，自动播放音效和桌面通知。

## 工作原理

利用 Claude Code 的 [Hooks 系统](https://docs.anthropic.com/en/docs/claude-code/hooks) 实现确定性触发，不依赖 LLM 提示词，100% 可靠。

| 触发场景 | Hook 事件 | 通知内容 |
|---------|----------|---------|
| CC 完成回答，等待输入 | `Stop` | ✅ 任务完成 |
| CC 需要权限审批 | `Notification` → `permission_prompt` | 🔐 需要权限审批 |
| CC 收到推送通知 | `Notification` → `idle_prompt` | 📬 收到通知 |
| CC 报错停止 | `StopFailure` | ❌ Claude 遇到错误 |

## 支持平台

| 平台 | 声音 | 桌面通知 |
|------|------|---------|
| macOS | `afplay` | `osascript` |
| Windows | PowerShell Media.SoundPlayer | BalloonTip |
| WSL | `powershell.exe` | `powershell.exe` BalloonTip |

## 安装

```bash
# 1. 克隆项目
git clone https://github.com/你的用户名/cc-notify.git /path/to/cc-notify

# 2. 链接到 Claude Code skills 目录
ln -s /path/to/cc-notify ~/.claude/skills/cc-notify

# 3. 运行安装脚本（自动检测平台 + 写入 hooks）
python3 ~/.claude/skills/cc-notify/setup.py
```

安装脚本会向 `~/.claude/settings.json` 写入 `Stop`、`Notification` 和 `StopFailure` 三个 hook，幂等执行，重复运行不会重复添加。

## 测试

```bash
echo '{"notification_type":"idle_prompt"}' | python3 ~/.claude/skills/cc-notify/notify.py
```

你应该听到音效并看到桌面通知弹窗。

## 配置

### 配置文件

全局配置：`~/.claude/notify-config.json`（优先）
内置默认：`cc-notify/notify-config.json`（兜底）

```json
{
  "sound": {
    "enabled": true,
    "file_macos": "notify.mp3",
    "file_windows": "",
    "repeat": 1
  },
  "desktop_notification": {
    "enabled": true
  }
}
```

### 自定义音效

将音频文件放入 `cc-notify/audio/` 目录，在配置中填写文件名即可：

```bash
# 复制你的音效文件到 audio 目录
cp ~/Downloads/my-sound.mp3 ~/.claude/skills/cc-notify/audio/

# 编辑配置
vim ~/.claude/notify-config.json
```

```json
{
  "sound": {
    "enabled": true,
    "file_macos": "my-sound.mp3",
    "repeat": 3
  }
}
```

**音效文件查找顺序：**
1. `cc-notify/audio/<filename>` — 项目内 audio 目录
2. 绝对路径 — 如 `/Users/xxx/sounds/ding.mp3`
3. 系统默认 — macOS: `Glass.aiff`，Windows: 系统提示音

**支持的音频格式：** `.mp3`、`.wav`、`.aiff`

**`repeat`：** 音效播放次数，默认 `1`，设为 `3` 则连播 3 次。

### 交互式配置

在 Claude Code 中运行 `/cc-notify` 可交互式修改配置和测试通知。

### 开关通知

```json
{
  "sound": { "enabled": false },
  "desktop_notification": { "enabled": false }
}
```

## 项目结构

```
cc-notify/
├── SKILL.md              # Skill 描述（Claude Code 识别）
├── notify.py             # 核心通知脚本
├── setup.py              # 安装脚本
├── notify-config.json    # 默认配置
├── audio/                # 自定义音效文件目录
│   └── notify.mp3
└── README.md
```

## macOS 注意事项

首次运行后，需要在 **系统设置 → 通知** 中给 **Script Editor** 开启通知权限，否则桌面通知弹窗不会显示。

## 致谢

灵感来自 [crossoverJie 的 agent-notifier](https://github.com/crossoverJie/skills/tree/main/skills/agent-notifier) — Hooks > Prompts 的理念和跨平台通知方案。
