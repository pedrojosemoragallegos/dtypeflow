"""Generate representative screenshots of the TUI using mock/demo.csv.

Run with: uv run python scripts/screenshots.py
Writes SVG screenshots to screenshots/: the pick-file screen, one screenshot
per column per available dtype-group tab (Safe / Too small / Discouraged),
and the export screen.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from dtypeflow.tui.app import ConfigureScreen, DtypeflowApp, ExportScreen

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "mock" / "demo.csv"
OUT_DIR = ROOT / "screenshots"


def _slug(text: str) -> str:
    return text.lower().replace(" ", "_")


async def screenshot_pick_file() -> None:
    app = DtypeflowApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.pause()
        app.save_screenshot(str(OUT_DIR / "00_pick_file.svg"))
        app.exit()


async def _goto_panel_index(pilot, screen: ConfigureScreen, target: int) -> None:
    while screen._index < target:  # noqa: SLF001
        await pilot.click("#next-btn")
        await pilot.pause()


async def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    await screenshot_pick_file()

    app = DtypeflowApp(initial_path=str(CSV_PATH))
    async with app.run_test(size=(120, 45)) as pilot:
        # Wait for the background load worker to finish and push ConfigureScreen.
        for _ in range(50):
            await pilot.pause()
            if isinstance(app.screen, ConfigureScreen):
                break

        screen = app.screen
        panels = list(screen.query("ColumnPanel"))

        for index, panel in enumerate(panels):
            await _goto_panel_index(pilot, screen, index)
            column_slug = _slug(panel.column.name)
            for group in panel._groups:  # noqa: SLF001
                tab = panel.query_one(f"#{panel._tab_ids[group]}")  # noqa: SLF001
                await pilot.click(tab)
                await pilot.pause()
                app.save_screenshot(
                    str(OUT_DIR / f"{index + 1:02d}_{column_slug}_{_slug(group)}.svg"),
                )

        # Jump to the last column and finish to reach the export screen.
        while screen.query_one("#next-btn").label != "Finish":
            await pilot.click("#next-btn")
            await pilot.pause()
        await pilot.click("#next-btn")
        for _ in range(20):
            await pilot.pause()
            if isinstance(app.screen, ExportScreen):
                break
        app.save_screenshot(str(OUT_DIR / f"{len(panels) + 1:02d}_export_screen.svg"))

        app.exit()


if __name__ == "__main__":
    asyncio.run(main())
