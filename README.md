# Push-Style Playing Clip Colors Installer

This tool reinstalls the Launchpad playing-clip color animation patch after Ableton updates or script resets.

## What it changes

- Writes `novation/push_playing_clip_session.py` (shared clip-slot override).
- Writes wrapper `__init__.py` files for target Launchpad controller folders.
- Each wrapper loads the original `__init__.pyc`, patches `session_class`, and delegates normal startup.

## Default behavior

If you run without arguments, it applies to:

- `Launchpad_Mini_MK3`

## Usage

```bash
python3.11 '/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/_Tools/apply_push_style_launchpad_colors/apply_push_style_launchpad_colors.py'
python3.11 '/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/_Tools/apply_push_style_launchpad_colors/apply_push_style_launchpad_colors.py' Launchpad_Mini_MK3 Launchpad_X Launchpad_Pro_MK3
python3.11 '/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/_Tools/apply_push_style_launchpad_colors/apply_push_style_launchpad_colors.py' --all-launchpads
python3.11 '/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/_Tools/apply_push_style_launchpad_colors/apply_push_style_launchpad_colors.py' --all-launchpads --dry-run
python3.11 '/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/_Tools/apply_push_style_launchpad_colors/apply_push_style_launchpad_colors.py' --uninstall Launchpad_Mini_MK3
python3.11 '/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/_Tools/apply_push_style_launchpad_colors/apply_push_style_launchpad_colors.py' --uninstall --all-launchpads
python3.11 '/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/_Tools/apply_push_style_launchpad_colors/apply_push_style_launchpad_colors.py' --uninstall --all-launchpads --dry-run
```

## Notes

- If a target already has a custom `__init__.py`, the tool creates a timestamped backup before replacing it.
- During uninstall, a managed `__init__.py` is restored from the newest backup when available; otherwise it is removed.
- The helper module `novation/push_playing_clip_session.py` is removed only when no managed Launchpad wrappers remain.
- Restart Ableton Live after applying changes.


