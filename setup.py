#!/usr/bin/env python3
"""
cc-notify setup: detect platform, configure Notification hook in settings.json.
"""

import json
import os
import platform
import sys

SETTINGS_PATH = os.path.expanduser("~/.claude/settings.json")


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


def hook_exists(hook_list, notify_cmd):
    for h in hook_list:
        for hook in h.get("hooks", []):
            if notify_cmd in hook.get("command", ""):
                return True
    return False


def configure_hooks():
    if not os.path.exists(SETTINGS_PATH):
        print(f"Error: {SETTINGS_PATH} not found.")
        print("Please run Claude Code at least once to generate settings.json.")
        sys.exit(1)

    with open(SETTINGS_PATH) as f:
        settings = json.load(f)

    skill_path = os.path.dirname(os.path.abspath(__file__))
    notify_cmd = f"python3 {skill_path}/notify.py"

    hooks = settings.get("hooks", {})
    changed = False

    # Notification hook: idle_prompt + permission_prompt
    notification_hooks = hooks.get("Notification", [])
    if not hook_exists(notification_hooks, notify_cmd):
        notification_hooks.append({
            "matcher": "",
            "hooks": [{"type": "command", "command": notify_cmd}]
        })
        hooks["Notification"] = notification_hooks
        print("✓ Notification hook configured")
        changed = True
    else:
        print("  Notification hook already exists, skipping.")

    # Stop hook: CC finished answering
    stop_hooks = hooks.get("Stop", [])
    if not hook_exists(stop_hooks, notify_cmd):
        stop_hooks.append({
            "matcher": "",
            "hooks": [{"type": "command", "command": notify_cmd}]
        })
        hooks["Stop"] = stop_hooks
        print("✓ Stop hook configured")
        changed = True
    else:
        print("  Stop hook already exists, skipping.")

    # StopFailure hook: error/crash
    stop_failure_hooks = hooks.get("StopFailure", [])
    if not hook_exists(stop_failure_hooks, notify_cmd):
        stop_failure_hooks.append({
            "matcher": "",
            "hooks": [{"type": "command", "command": notify_cmd}]
        })
        hooks["StopFailure"] = stop_failure_hooks
        print("✓ StopFailure hook configured")
        changed = True
    else:
        print("  StopFailure hook already exists, skipping.")

    if changed:
        settings["hooks"] = hooks
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        print(f"Hooks written to {SETTINGS_PATH}")
    else:
        print("All hooks up to date.")


def main():
    p = get_platform()
    platform_names = {
        "darwin": "macOS",
        "windows": "Windows",
        "wsl": "Windows (WSL)",
    }
    print(f"Platform: {platform_names.get(p, p)}")

    configure_hooks()

    skill_path = os.path.dirname(os.path.abspath(__file__))
    print(f"\nSetup complete! Test with:")
    print(f'  echo \'{{"notification_type":"idle_prompt"}}\' | python3 {skill_path}/notify.py')


if __name__ == "__main__":
    main()
