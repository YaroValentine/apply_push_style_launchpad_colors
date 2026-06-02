#!/usr/bin/env python3
"""Apply Push-style playing-clip colors to Novation Launchpad scripts.

This installer writes two pieces:
1) `novation/push_playing_clip_session.py` (shared custom session classes)
2) `<controller>/__init__.py` wrappers that load the original `__init__.pyc`,
   patch `session_class`, and delegate `get_capabilities/create_instance`.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Optional

HELPER_REL_PATH = Path("novation/push_playing_clip_session.py")

HELPER_CONTENT = """from __future__ import absolute_import, print_function, unicode_literals

from ableton.v2.control_surface.components import (
    ClipSlotComponent,
    SceneComponent,
    SessionComponent,
)
from ableton.v2.control_surface.elements import Color

from .colors import Pulse, Rgb


class PushStyleClipSlotComponent(ClipSlotComponent):
    \"\"\"Use clip color animation while a clip is actively playing.\"\"\"

    def _feedback_value(self, track, slot_or_clip):
        # Keep all existing states from the base implementation unless this is a plain playing clip.
        base_value = super(PushStyleClipSlotComponent, self)._feedback_value(track, slot_or_clip)
        if not getattr(slot_or_clip, \"is_playing\", False) or getattr(slot_or_clip, \"is_recording\", False):
            return base_value

        if getattr(slot_or_clip, \"color\", None) is None:
            return base_value

        mapped_color = self._color_value(slot_or_clip)
        if isinstance(mapped_color, Color):
            playing_color = mapped_color
        elif isinstance(mapped_color, int):
            playing_color = Color(mapped_color)
        else:
            return base_value

        return Pulse(color1=Rgb.BLACK, color2=playing_color)


class PushStyleSceneComponent(SceneComponent):
    clip_slot_component_type = PushStyleClipSlotComponent


class PushStyleSessionComponent(SessionComponent):
    scene_component_type = PushStyleSceneComponent
"""

WRAPPER_TEMPLATE = """from __future__ import absolute_import, print_function, unicode_literals

import importlib.util
from pathlib import Path

from novation.novation_base import NovationBase
from novation.push_playing_clip_session import PushStyleSessionComponent


def _load_original_module():
    module_name = __name__ + \"._original\"
    pyc_path = Path(__file__).with_suffix(\".pyc\")
    spec = importlib.util.spec_from_file_location(module_name, str(pyc_path))
    if spec is None or spec.loader is None:
        raise RuntimeError(\"Cannot load original bytecode module from {0}\".format(pyc_path))

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ORIGINAL = _load_original_module()

for _value in vars(_ORIGINAL).values():
    if isinstance(_value, type) and issubclass(_value, NovationBase) and _value is not NovationBase:
        _value.session_class = PushStyleSessionComponent


def get_capabilities():
    return _ORIGINAL.get_capabilities()


def create_instance(c_instance):
    return _ORIGINAL.create_instance(c_instance)
"""

WRAPPER_MARKER = "from novation.push_playing_clip_session import PushStyleSessionComponent"


def detect_launchpad_dirs(root: Path) -> List[Path]:
    return sorted(
        [
            child
            for child in root.iterdir()
            if child.is_dir() and child.name.startswith("Launchpad") and (child / "__init__.pyc").exists()
        ],
        key=lambda p: p.name,
    )


def write_text_file(path: Path, content: str, dry_run: bool) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False

    if not dry_run:
        path.write_text(content, encoding="utf-8")
    return True


def backup_file(path: Path, dry_run: bool) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_name(path.name + ".pushstyle_backup_" + stamp)
    if not dry_run:
        backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return backup_path


def is_managed_wrapper(content: str) -> bool:
    return content == WRAPPER_TEMPLATE or WRAPPER_MARKER in content


def latest_backup_for(path: Path) -> Optional[Path]:
    backups = sorted(path.parent.glob(path.name + ".pushstyle_backup_*"), key=lambda p: p.name)
    return backups[-1] if backups else None


def apply_to_target(root: Path, target: str, dry_run: bool) -> str:
    folder = root / target
    if not folder.is_dir():
        return f"[skip] {target}: folder not found"

    pyc_path = folder / "__init__.pyc"
    if not pyc_path.exists():
        return f"[skip] {target}: missing __init__.pyc"

    init_py = folder / "__init__.py"
    wrapper_changed = False
    backup_note = ""

    if init_py.exists() and init_py.read_text(encoding="utf-8") != WRAPPER_TEMPLATE:
        backup_path = backup_file(init_py, dry_run)
        backup_note = f" (backup: {backup_path.name})"

    wrapper_changed = write_text_file(init_py, WRAPPER_TEMPLATE, dry_run)
    action = "updated" if wrapper_changed else "unchanged"
    return f"[{action}] {target}/__init__.py{backup_note}"


def uninstall_from_target(root: Path, target: str, dry_run: bool) -> str:
    folder = root / target
    if not folder.is_dir():
        return f"[skip] {target}: folder not found"

    init_py = folder / "__init__.py"
    if not init_py.exists():
        return f"[skip] {target}: no __init__.py override present"

    content = init_py.read_text(encoding="utf-8")
    if not is_managed_wrapper(content):
        return f"[skip] {target}: __init__.py is not managed by this installer"

    backup_path = latest_backup_for(init_py)
    if backup_path is not None:
        if not dry_run:
            init_py.write_text(backup_path.read_text(encoding="utf-8"), encoding="utf-8")
        return f"[restored] {target}/__init__.py from {backup_path.name}"

    if not dry_run:
        init_py.unlink()
    return f"[removed] {target}/__init__.py"


def wrappers_still_present(root: Path) -> bool:
    for folder in detect_launchpad_dirs(root):
        init_py = folder / "__init__.py"
        if init_py.exists() and is_managed_wrapper(init_py.read_text(encoding="utf-8")):
            return True
    return False


def cleanup_helper_if_unused(root: Path, dry_run: bool) -> str:
    helper_path = root / HELPER_REL_PATH
    if not helper_path.exists():
        return f"[skip] {helper_path.relative_to(root)}: not present"

    if wrappers_still_present(root):
        return f"[kept] {helper_path.relative_to(root)} (still used by managed wrappers)"

    if not dry_run:
        helper_path.unlink()
    return f"[removed] {helper_path.relative_to(root)}"


def resolve_targets(root: Path, args: argparse.Namespace) -> List[str]:
    if args.targets:
        return args.targets

    if args.all_launchpads:
        return [p.name for p in detect_launchpad_dirs(root)]

    return ["Launchpad_Mini_MK3"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply Push-style playing-clip colors to Launchpad scripts.")
    parser.add_argument(
        "targets",
        nargs="*",
        help="Controller folder names (example: Launchpad_Mini_MK3 Launchpad_X)",
    )
    parser.add_argument(
        "--all-launchpads",
        action="store_true",
        help="Apply to all Launchpad* folders that contain __init__.pyc",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove managed wrappers (or restore backups) for selected targets",
    )
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parents[2]),
        help="Path to 'MIDI Remote Scripts' root",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()

    if not root.is_dir():
        print(f"error: root does not exist: {root}")
        return 2

    targets = resolve_targets(root, args)
    if not targets:
        print("[skip] no targets selected")
        return 0

    if args.uninstall:
        for target in targets:
            print(uninstall_from_target(root, target, args.dry_run))
        print(cleanup_helper_if_unused(root, args.dry_run))
        return 0

    helper_path = root / HELPER_REL_PATH
    helper_changed = write_text_file(helper_path, HELPER_CONTENT, args.dry_run)
    print(f"[{'updated' if helper_changed else 'unchanged'}] {helper_path.relative_to(root)}")

    for target in targets:
        print(apply_to_target(root, target, args.dry_run))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())



