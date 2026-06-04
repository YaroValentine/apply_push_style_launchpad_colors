# Push-Style Playing Clip Colors Installer

This tool reinstalls the Launchpad playing-clip color animation patch after Ableton updates or script resets.

## What it changes

- Writes `novation/push_playing_clip_session.py` (shared clip-slot override).
- Writes wrapper `__init__.py` files for target Launchpad controller folders.
- Each wrapper loads the original `__init__.pyc`, patches `session_class`, and delegates normal startup.

## Controller compatibility

- Designed for **Novation Launchpad** controller scripts (`Launchpad*` folders).
- Works for `Launchpad_Mini_MK3` by default.
- Can target other Launchpads (for example `Launchpad_X`, `Launchpad_Pro_MK3`) when those folders exist in your Ableton install.
- It does **not** patch non-Launchpad controllers.

## Default behavior

If you run without arguments, it applies to:

- `Launchpad_Mini_MK3`

## Where Ableton keeps MIDI Remote Scripts

- macOS (typical): `/Applications/Ableton Live <version>.app/Contents/App-Resources/MIDI Remote Scripts`
- Windows (typical): `C:\ProgramData\Ableton\Live <version>\Resources\MIDI Remote Scripts`
- Windows (alternative installs): `C:\Program Files\Ableton\Live <version>\Resources\MIDI Remote Scripts`

`<version>` can be `12 Suite`, `12 Standard`, etc.

## Run from any location

You can run the installer from any folder. If `--root` is omitted, it tries to auto-detect the Ableton `MIDI Remote Scripts` folder in this order:

1. `ABLETON_MIDI_REMOTE_SCRIPTS` environment variable.
2. Parent folders of the script path.
3. OS install defaults (macOS `/Applications/...`, Windows `ProgramData` / `Program Files`).

Use `--print-detected-root` to verify what path it will use.

## Usage

```bash
python3 apply_push_style_launchpad_colors.py --print-detected-root
python3 apply_push_style_launchpad_colors.py
python3 apply_push_style_launchpad_colors.py Launchpad_Mini_MK3 Launchpad_X Launchpad_Pro_MK3
python3 apply_push_style_launchpad_colors.py --all-launchpads
python3 apply_push_style_launchpad_colors.py --all-launchpads --dry-run
python3 apply_push_style_launchpad_colors.py --uninstall Launchpad_Mini_MK3
python3 apply_push_style_launchpad_colors.py --uninstall --all-launchpads
python3 apply_push_style_launchpad_colors.py --uninstall --all-launchpads --dry-run
python3 apply_push_style_launchpad_colors.py --root '/absolute/path/to/MIDI Remote Scripts' --all-launchpads
```

Windows PowerShell example:

```powershell
python .\apply_push_style_launchpad_colors.py --print-detected-root
python .\apply_push_style_launchpad_colors.py --root 'C:\ProgramData\Ableton\Live 12 Suite\Resources\MIDI Remote Scripts' --all-launchpads
```

## Notes

- If a target already has a custom `__init__.py`, the tool creates a timestamped backup before replacing it.
- During uninstall, a managed `__init__.py` is restored from the newest backup when available; otherwise it is removed.
- The helper module `novation/push_playing_clip_session.py` is removed only when no managed Launchpad wrappers remain.
- Restart Ableton Live after applying changes.


