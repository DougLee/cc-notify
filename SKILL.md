---
name: cc-notify
description: "Configure cc-notify notification settings: sound file, repeat count, enable/disable channels, test notification."
user_invocable: true
---

# /cc-notify — Notification Configuration

Configure cc-notify settings interactively.

## Step 1: Show current config

Read `~/.claude/notify-config.json` and display current settings to the user:
- Sound enabled/disabled
- Sound file (show filename, indicate if from audio/ folder or absolute path)
- Repeat count
- Desktop notification enabled/disabled

```bash
cat ~/.claude/notify-config.json 2>/dev/null || echo "NO_CONFIG"
ls ~/.claude/skills/cc-notify/audio/ 2>/dev/null || echo "NO_AUDIO_DIR"
```

## Step 2: Ask what to configure

Use AskUserQuestion with these options:

> What would you like to configure?

A) Sound settings (file, repeat, enable/disable)
B) Desktop notification (enable/disable)
C) Change all settings
D) Test notification now
E) View current config only

## Step 3: Apply changes

Based on user's choice, ask for new values via AskUserQuestion, then write the updated config to `~/.claude/notify-config.json`.

When setting sound file:
- List available files in `cc-notify/audio/` directory
- User can pick from the list or provide an absolute path
- If user provides a file that's not in audio/, copy it to audio/ automatically

## Step 4: Test

After saving config, always offer to test:

```bash
echo '{"notification_type":"idle_prompt"}' | python3 ~/.claude/skills/cc-notify/notify.py
```

## Config file format

`~/.claude/notify-config.json`:

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
