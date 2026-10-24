from __future__ import annotations

__all__: list[str] = ["run"]


def run() -> None:
    from dtypeflow.tui.app import DtypeflowApp

    DtypeflowApp().run()
