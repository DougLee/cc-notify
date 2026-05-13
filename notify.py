#!/usr/bin/env python3
"""
cc-notify: Cross-platform notification for Claude Code.
Called by Notification hook via stdin JSON.
"""

import json
import os
import platform
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))

MESSAGES = {
    "idle_prompt": "✅ 任务完成",
    "permission_prompt": "🔐 需要权限审批",
    "stop_failure": "❌ Claude 遇到错误",
}


def is_wsl():
    try:
        with open("/proc/version") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False


def get_platform():
    system = platform.system()
    if system == "Linux" and is_wsl():
        return "wsl"
    return system.lower()


def load_config():
    global_path = os.path.expanduser("~/.claude/notify-config.json")
    if os.path.exists(global_path):
        with open(global_path) as f:
            return json.load(f)
    local_path = os.path.join(SKILL_DIR, "notify-config.json")
    if os.path.exists(local_path):
        with open(local_path) as f:
            return json.load(f)
    return {"sound": {"enabled": True}, "desktop_notification": {"enabled": True}}


def resolve_sound_file(config, platform_key):
    """Resolve sound file path: audio/ filename > absolute path > default."""
    filename = config.get("sound", {}).get(platform_key, "")
    if not filename:
        return "/System/Library/Sounds/Glass.aiff" if platform_key == "file_macos" else ""
    # Relative filename → look in cc-notify/audio/
    audio_dir = os.path.join(SKILL_DIR, "audio")
    candidate = os.path.join(audio_dir, filename)
    if os.path.exists(candidate):
        return candidate
    # Absolute path
    if os.path.isabs(filename):
        return filename
    return filename


def play_sound(config):
    if not config.get("sound", {}).get("enabled"):
        return
    repeat = max(1, config.get("sound", {}).get("repeat", 1))
    p = get_platform()
    try:
        for _ in range(repeat):
            if p == "darwin":
                sound_file = resolve_sound_file(config, "file_macos")
                subprocess.run(["afplay", sound_file], timeout=5)
            elif p in ("windows", "wsl"):
                sound_file = resolve_sound_file(config, "file_windows")
                if sound_file and os.path.exists(sound_file):
                    exe = "powershell.exe" if p == "wsl" else "powershell"
                    subprocess.run([exe, "-Command", f'(New-Object Media.SoundPlayer "{sound_file}").PlaySync()'], timeout=5)
                else:
                    exe = "powershell.exe" if p == "wsl" else "powershell"
                    subprocess.run([exe, "-Command", "[System.Media.SystemSounds]::Asterisk.Play()"], timeout=5)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass


def send_notification(title, message, config):
    if not config.get("desktop_notification", {}).get("enabled"):
        return
    p = get_platform()
    if p == "darwin":
        subprocess.Popen([
            "osascript", "-e",
            f'display notification "{message}" with title "{title}"'
        ])
    elif p == "windows":
        ps_script = (
            'Add-Type -AssemblyName System.Windows.Forms; '
            f'$n = New-Object System.Windows.Forms.NotifyIcon; '
            f'$n.Icon = [System.Drawing.SystemIcons]::Information; '
            f'$n.Visible = $true; '
            f'$n.ShowBalloonTip(5000, "{title}", "{message}", [System.Windows.Forms.ToolTipIcon]::Info)'
        )
        subprocess.Popen(["powershell", "-Command", ps_script])
    elif p == "wsl":
        ps_script = (
            'Add-Type -AssemblyName System.Windows.Forms; '
            f'$n = New-Object System.Windows.Forms.NotifyIcon; '
            f'$n.Icon = [System.Drawing.SystemIcons]::Information; '
            f'$n.Visible = $true; '
            f'$n.ShowBalloonTip(5000, "{title}", "{message}", [System.Windows.Forms.ToolTipIcon]::Info)'
        )
        subprocess.Popen(["powershell.exe", "-Command", ps_script])


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        data = {}

    event_type = data.get("notification_type", "") or data.get("hook_event", "")
    message = MESSAGES.get(event_type, f"📢 {event_type}")
    config = load_config()

    play_sound(config)
    send_notification("Claude Code", message, config)


if __name__ == "__main__":
    main()
