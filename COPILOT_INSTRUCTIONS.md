# Copilot Instructions: Push-Style Playing Clip Colors for Novation Launchpads

Use this prompt with Copilot Chat when you need to recreate the same patch from scratch.

## Prompt

```text
I am modifying Ableton Live 12 MIDI Remote Scripts.

Goal:
For Novation Launchpad Session mode clip buttons:
- Idle clip: keep original Ableton clip color.
- Playing clip: animate using the same clip color (pulse or blink), not fixed green.
- Keep default behavior unchanged for empty, stopped, triggered/queued, recording, and record-triggered states.

Implementation requirements:
1) Create `novation/push_playing_clip_session.py` with:
   - `PushStyleClipSlotComponent(ClipSlotComponent)` overriding `_feedback_value(track, slot_or_clip)`.
   - Call `super(...)._feedback_value(...)` first and return that for all non-target states.
   - Only override when `slot_or_clip.is_playing` is true and `slot_or_clip.is_recording` is false.
   - Read clip color from `slot_or_clip.color`, map with existing `_color_value(slot_or_clip)`.
   - Return `Pulse(color1=Rgb.BLACK, color2=Color(mapped_value))`.
   - Add `PushStyleSceneComponent(SceneComponent)` with `clip_slot_component_type = PushStyleClipSlotComponent`.
   - Add `PushStyleSessionComponent(SessionComponent)` with `scene_component_type = PushStyleSceneComponent`.

2) For each target Launchpad folder (e.g. `Launchpad_Mini_MK3`, `Launchpad_X`, `Launchpad_Pro_MK3`), create `__init__.py` wrapper that:
   - Loads original `__init__.pyc` via `importlib.util.spec_from_file_location`.
   - Finds subclasses of `novation.novation_base.NovationBase` in that module.
   - Sets each class `session_class = PushStyleSessionComponent`.
   - Delegates exported `get_capabilities()` and `create_instance(c_instance)` to original module.

3) Create installer script `_Tools/apply_push_style_launchpad_colors/apply_push_style_launchpad_colors.py` that can:
   - Apply patch to specific targets or `--all-launchpads`.
   - Use default target `Launchpad_Mini_MK3`.
   - Backup any pre-existing target `__init__.py` before replacing.
   - Support `--dry-run`.
   - Support `--uninstall`:
     - If target wrapper is managed by installer and backup exists, restore latest backup.
     - Else remove managed wrapper `__init__.py`.
     - Keep or remove helper module safely: remove only if no managed wrappers remain.

4) Add `_Tools/apply_push_style_launchpad_colors/README.md` with install/uninstall command examples.

5) Validate by running Python syntax checks (`py_compile`) on created/edited `.py` files.

Please implement directly in files and then report changed paths and test output.
```

## Notes

- Use pulse animation for parity with current patch. If you want blink instead, swap `Pulse` to `Blink` in the helper module.
- Restart Ableton Live after applying or uninstalling the patch.


