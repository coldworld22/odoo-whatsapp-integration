#!/usr/bin/env python3
"""Verify Odoo release ZIPs contain required assets."""

from __future__ import annotations

import ast
import fnmatch
import sys
from pathlib import Path
from zipfile import ZipFile


REQUIRED_FILES = (
    "static/src/scss/demo_brand.scss",
    "static/src/scss/demo_hide_apps.scss",
    "static/src/js/demo_hide_apps.js",
)


def _manifest_path(names: set[str]) -> str:
    manifests = sorted(name for name in names if name.endswith("__manifest__.py"))
    if len(manifests) != 1:
        raise ValueError(f"expected one __manifest__.py, found {len(manifests)}")
    return manifests[0]


def _addon_root(manifest_path: str) -> str:
    return manifest_path.removesuffix("/__manifest__.py").removesuffix("__manifest__.py")


def _archive_path(root: str, module_path: str) -> str:
    if root:
        return f"{root}/{module_path}"
    return module_path


def _iter_asset_entries(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _iter_asset_entries(item)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            yield from _iter_asset_entries(item)


def _asset_path_exists(names: set[str], root: str, asset: str) -> bool:
    if "/static/" not in asset and not asset.startswith("static/"):
        return True

    candidates = [asset]
    if root and asset.startswith(f"{root}/"):
        candidates.append(asset.removeprefix(f"{root}/"))
    elif root and asset.startswith("static/"):
        candidates.append(_archive_path(root, asset))

    for candidate in candidates:
        if any(char in candidate for char in "*?["):
            if any(fnmatch.fnmatch(name, candidate) for name in names):
                return True
        elif candidate in names:
            return True
    return False


def verify_archive(path: Path) -> list[str]:
    errors: list[str] = []
    with ZipFile(path) as archive:
        names = set(archive.namelist())
        try:
            manifest = _manifest_path(names)
        except ValueError as exc:
            return [str(exc)]

        root = _addon_root(manifest)
        try:
            manifest_data = ast.literal_eval(archive.read(manifest).decode("utf-8"))
        except Exception as exc:
            return [f"could not parse {manifest}: {exc}"]

    for module_path in REQUIRED_FILES:
        archive_path = _archive_path(root, module_path)
        if archive_path not in names:
            errors.append(f"missing required file: {archive_path}")

    assets = manifest_data.get("assets", {})
    for asset in _iter_asset_entries(assets):
        if not _asset_path_exists(names, root, asset):
            errors.append(f"manifest asset does not exist: {asset}")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: verify_release_archive.py ZIP [ZIP ...]", file=sys.stderr)
        return 2

    failed = False
    for arg in argv[1:]:
        path = Path(arg)
        errors = verify_archive(path)
        if errors:
            failed = True
            print(f"{path}: FAIL")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"{path}: OK")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
