from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Literal, cast

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalGroup, VerticalScroll
from textual.css.query import NoMatches
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    DirectoryTree,
    Footer,
    Header,
    Input,
    Label,
    OptionList,
    RadioButton,
    RadioSet,
    Static,
    Tab,
    Tabs,
)
from textual.widgets.option_list import Option

from .compatibility import GROUP_ORDER
from .dto import ColumnReport, ColumnSelection, DtypeOption, LoadedDataset
from .service import DtypeflowService

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.widget import Widget
_GROUP_ICONS: dict[str, str] = {"Safe": "✓", "Too small": "↓", "Discouraged": "!"}
_TYPE_COL_WIDTH = 14
_STAR_COLOR = "gold"
_TYPE_COLOR = "cyan"
_NUMBER_COLOR = "#ffd166"
_NUMBER_PATTERN = re.compile("-?\\d[\\d,]*(?:\\.\\d+)?(?:E[+-]\\d+)?")


def _colorize_type(label: str) -> str:
    return f"[{_TYPE_COLOR}]{label}[/{_TYPE_COLOR}]"


def _colorize_description(name: str, description: str) -> str:
    if name == "Boolean":
        colored = description.replace(
            "True", f"[{_NUMBER_COLOR}]True[/{_NUMBER_COLOR}]",
        )
        return colored.replace("False", f"[{_NUMBER_COLOR}]False[/{_NUMBER_COLOR}]")
    return _NUMBER_PATTERN.sub(
        lambda match: f"[{_NUMBER_COLOR}]{match.group()}[/{_NUMBER_COLOR}]", description,
    )


_FALSY_TOKENS = frozenset({"0", "f", "false", "n", "no"})
_TRUTHY_TOKENS = frozenset({"1", "t", "true", "y", "yes"})
_TWO_VALUES = 2


def _grouped_options(options: tuple[DtypeOption, ...]) -> dict[str, list[DtypeOption]]:
    grouped: dict[str, list[DtypeOption]] = {}
    for option in options:
        grouped.setdefault(option.group, []).append(option)
    return {group: grouped[group] for group in GROUP_ORDER if group in grouped}


def _stats_text(stats: tuple[tuple[str, str], ...]) -> str:
    return "\n".join(

            f"{label}: [{_NUMBER_COLOR}]{value}[/{_NUMBER_COLOR}]"
            for (label, value) in stats

    )


def _dtype_row_text(option: DtypeOption) -> str:
    padded_label = f"{option.label:<{_TYPE_COL_WIDTH}}"
    colored_label = f"[{_TYPE_COLOR}]{padded_label}[/{_TYPE_COLOR}]"
    description = _colorize_description(option.name, option.description)
    return f"{colored_label}{description}"


def _status_classes(*, ok: bool | None) -> str:
    if ok is None:
        return "status"
    return "status -ok" if ok else "status -error"


def _default_true_value(values: tuple[str, str]) -> str:
    (first, second) = values
    if (
        first.strip().lower() in _FALSY_TOKENS
        or second.strip().lower() in _TRUTHY_TOKENS
    ):
        return second
    if (
        second.strip().lower() in _FALSY_TOKENS
        or first.strip().lower() in _TRUTHY_TOKENS
    ):
        return first
    return second


class CSVDirectoryTree(DirectoryTree):
    def __init__(
        self, path: str | Path, *, suffixes: tuple[str, ...], **kwargs: Any,
    ) -> None:
        super().__init__(path, **kwargs)
        self._suffixes = suffixes

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [
            path
            for path in paths
            if path.is_dir() or path.suffix.lower() in self._suffixes
        ]


class BrowseModal(ModalScreen[str | None]):
    BINDINGS: ClassVar[list[Binding]] = [Binding("escape", "cancel", "Cancel")]

    def __init__(
        self,
        *,
        mode: Literal["open", "save"],
        suffixes: tuple[str, ...],
        title: str,
        start_dir: Path | None = None,
        default_filename: str = "",
    ) -> None:
        super().__init__()
        self._mode = mode
        self._suffixes = suffixes
        self._title = title
        self._current_dir = start_dir or Path.cwd()
        self._default_filename = default_filename

    def compose(self) -> ComposeResult:
        with Vertical(classes="browse-dialog"):
            yield Label(self._title, classes="app-subtitle")
            yield CSVDirectoryTree(
                self._current_dir, suffixes=self._suffixes, id="browse-tree",
            )
            yield Input(
                value=self._default_filename,
                placeholder="File name or full path",
                id="browse-input",
            )
            with Horizontal(classes="browse-buttons"):
                yield Button("Cancel", id="browse-cancel")
                yield Button("Select", id="browse-select", variant="primary")

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected,
    ) -> None:
        self._current_dir = event.path

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected,
    ) -> None:
        if self._mode == "open":
            self.dismiss(str(event.path))
            return
        self._current_dir = event.path.parent
        self.query_one("#browse-input", Input).value = event.path.name

    @on(Button.Pressed, "#browse-cancel")
    def _cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#browse-select")
    def _select(self) -> None:
        entered = self.query_one("#browse-input", Input).value.strip()
        if not entered:
            self.notify("Enter a file name.", severity="warning")
            return
        entered_path = Path(entered)
        destination = (
            entered_path
            if entered_path.is_absolute()
            else self._current_dir / entered_path
        )
        self.dismiss(str(destination))

    def action_cancel(self) -> None:
        self.dismiss(None)


class CategoryOrderPicker(Vertical):
    def __init__(self, categories: tuple[str, ...], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._order: list[str] = list(categories)

    def compose(self) -> ComposeResult:
        yield OptionList(*self._order, id="order-list")
        with Horizontal(classes="reorder-buttons"):
            yield Button("▲ Move up", id="move-up")
            yield Button("▼ Move down", id="move-down")

    @property
    def order(self) -> tuple[str, ...]:
        return tuple(self._order)

    @on(Button.Pressed, "#move-up")
    def _move_up(self) -> None:
        self._move(-1)

    @on(Button.Pressed, "#move-down")
    def _move_down(self) -> None:
        self._move(1)

    def _move(self, delta: int) -> None:
        option_list = self.query_one("#order-list", OptionList)
        index = option_list.highlighted
        if index is None:
            return
        new_index = index + delta
        if not 0 <= new_index < len(self._order):
            return
        (self._order[index], self._order[new_index]) = (
            self._order[new_index],
            self._order[index],
        )
        option_list.clear_options()
        option_list.add_options(self._order)
        option_list.highlighted = new_index


class ColumnPanel(Vertical):
    def __init__(
        self,
        column: ColumnReport,
        service: DtypeflowService,
        loaded: LoadedDataset,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.column = column
        self._service = service
        self._loaded = loaded
        self._grouped = _grouped_options(column.options)
        self._groups = list(self._grouped)
        self._tab_ids = {group: f"group-{i}" for (i, group) in enumerate(self._groups)}
        self._group_by_tab_id = {
            tab_id: group for (group, tab_id) in self._tab_ids.items()
        }
        self._recommended: DtypeOption = column.options[0]
        self._chosen: DtypeOption = self._recommended
        self._active_group: str = self._recommended.group
        self._unique_values: tuple[str, ...] | None = None

    def compose(self) -> ComposeResult:
        recommended_label = _colorize_type(self._recommended.label)
        recommended_description = _colorize_description(
            self._recommended.name, self._recommended.description,
        )
        yield Static(self.column.name, classes="column-title")
        yield Static(
            f"[{_STAR_COLOR}]Recommended:[/{_STAR_COLOR}] {recommended_label} — {recommended_description}",
            classes="column-recommended",
        )
        yield Static(_stats_text(self.column.stats), classes="column-stats")
        yield Tabs(*self._category_tabs(), id="dtype-tabs")
        yield OptionList(*self._option_rows(self._active_group), id="dtype-options")
        yield Static(
            _colorize_description(self._chosen.name, self._chosen.description),
            classes="dtype-description",
        )
        yield VerticalGroup(id="extra-container")

    async def on_mount(self) -> None:
        tabs = self.query_one("#dtype-tabs", Tabs)
        tabs.active = self._tab_ids[self._active_group]
        option_list = self.query_one("#dtype-options", OptionList)
        option_list.highlighted = option_list.get_option_index(self._recommended.name)
        await self._rebuild_extra()

    def _category_tabs(self) -> list[Tab]:
        return [
            Tab(
                f"{_GROUP_ICONS.get(group, '')} {group}".strip(),
                id=self._tab_ids[group],
            )
            for group in self._groups
        ]

    @on(Tabs.TabActivated, "#dtype-tabs")
    async def _tab_activated(self, event: Tabs.TabActivated) -> None:
        group = self._group_by_tab_id[event.tab.id]
        if group == self._active_group:
            return
        self._active_group = group
        option_list = self.query_one("#dtype-options", OptionList)
        option_list.clear_options()
        option_list.add_options(self._option_rows(group))
        option_list.highlighted = 0
        await self._select_option(self._grouped[group][0])

    def _option_rows(self, group: str) -> list[Option]:
        return [
            Option(_dtype_row_text(option), id=option.name)
            for option in self._grouped[group]
        ]

    def _option_by_name(self, name: str) -> DtypeOption:
        for options in self._grouped.values():
            for option in options:
                if option.name == name:
                    return option
        msg = f"Unknown dtype option {name!r} for column {self.column.name!r}."
        raise KeyError(msg)

    @on(OptionList.OptionSelected, "#dtype-options")
    async def _dtype_selected(self, event: OptionList.OptionSelected) -> None:
        await self._select_option(self._option_by_name(cast("str", event.option.id)))

    async def _select_option(self, option: DtypeOption) -> None:
        self._chosen = option
        description = _colorize_description(option.name, option.description)
        self.query_one(".dtype-description", Static).update(description)
        await self._rebuild_extra()

    async def _rebuild_extra(self) -> None:
        container = self.query_one("#extra-container", VerticalGroup)
        await container.remove_children()
        if self._chosen.name == "Boolean":
            await container.mount(*self._boolean_widgets())
        elif self._chosen.name == "Dictionary":
            await container.mount(*self._dictionary_widgets())

    def _values(self) -> tuple[str, ...]:
        if self._unique_values is None:
            self._unique_values = self._service.unique_values(
                self._loaded, self.column.name,
            )
        return self._unique_values

    def _boolean_widgets(self) -> list[Widget]:
        values = self._values()
        if len(values) >= _TWO_VALUES:
            (true_value, false_value) = self._boolean_order(values)
            return [
                Label("Which value means True?"),
                RadioSet(
                    RadioButton(
                        f"{true_value!r} means True / {false_value!r} means False",
                        value=True,
                    ),
                    RadioButton(
                        f"{false_value!r} means True / {true_value!r} means False",
                        value=False,
                    ),
                    id="bool-radio",
                ),
            ]
        if len(values) == 1:
            return [
                Static(
                    f"Only one observed value: {values[0]!r}", classes="boolean-caption",
                ),
                Checkbox(f"{values[0]!r} means True", id="bool-single-toggle"),
                Input(
                    value="OTHER",
                    placeholder="Label for the value that never appears",
                    id="bool-other-label",
                ),
            ]
        return [
            Static("No observed values to map to Boolean.", classes="status -error"),
        ]

    def _boolean_order(self, values: tuple[str, ...]) -> tuple[str, str]:
        true_value = _default_true_value((values[0], values[1]))
        false_value = values[1] if true_value == values[0] else values[0]
        return (true_value, false_value)

    def _dictionary_widgets(self) -> list[Widget]:
        values = self._values()
        picker = CategoryOrderPicker(values, id="dict-order", classes="dictionary-box")
        picker.display = False
        return [Checkbox("Ordered categories", id="dict-ordered"), picker]

    @on(Checkbox.Changed, "#dict-ordered")
    def _ordered_changed(self, event: Checkbox.Changed) -> None:
        try:
            picker = self.query_one("#dict-order", CategoryOrderPicker)
        except NoMatches:
            return
        picker.display = event.value

    def is_valid(self) -> bool:
        if self._chosen.name != "Boolean":
            return True
        values = self._values()
        if len(values) >= _TWO_VALUES:
            return True
        if len(values) == 1:
            try:
                other = self.query_one("#bool-other-label", Input).value.strip()
            except NoMatches:
                return False
            return bool(other) and other.lower() != values[0].strip().lower()
        return False

    def get_selection(self) -> ColumnSelection:
        if self._chosen.name == "Boolean":
            return self._boolean_selection()
        if self._chosen.name == "Dictionary":
            return self._dictionary_selection()
        return ColumnSelection(dtype_name=self._chosen.name)

    def _boolean_selection(self) -> ColumnSelection:
        values = self._values()
        if len(values) >= _TWO_VALUES:
            radio = self.query_one("#bool-radio", RadioSet)
            (true_default, false_default) = self._boolean_order(values)
            true_value = true_default if radio.pressed_index == 0 else false_default
            false_value = false_default if radio.pressed_index == 0 else true_default
            return ColumnSelection(
                dtype_name="Boolean", true_value=true_value, false_value=false_value,
            )
        if len(values) == 1:
            is_true = self.query_one("#bool-single-toggle", Checkbox).value
            other_input = self.query_one("#bool-other-label", Input).value.strip()
            other_label = other_input or "OTHER"
            true_value = values[0] if is_true else other_label
            false_value = other_label if is_true else values[0]
            return ColumnSelection(
                dtype_name="Boolean", true_value=true_value, false_value=false_value,
            )
        return ColumnSelection(dtype_name="Boolean")

    def _dictionary_selection(self) -> ColumnSelection:
        ordered = self.query_one("#dict-ordered", Checkbox).value
        categories = (
            self.query_one("#dict-order", CategoryOrderPicker).order
            if ordered
            else self._values()
        )
        return ColumnSelection(
            dtype_name="Dictionary", ordered=ordered, categories=categories,
        )


class PickFileScreen(Screen[None]):
    def __init__(self, initial_path: str | None = None) -> None:
        super().__init__()
        self._initial_path = initial_path

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="pick-file-screen"), Vertical(classes="panel hero"):
            with Horizontal(classes="field-row"):
                yield Input(
                    placeholder="Path to a CSV file",
                    id="csv-path",
                    value=self._initial_path or "",
                )
                yield Button("Browse…", id="browse-csv")
            yield Button(
                "Load dataset",
                id="load-btn",
                variant="primary",
                classes="primary-action",
            )
            yield Static("", id="pick-status", classes="status")
        yield Footer()

    def on_mount(self) -> None:
        if self._initial_path:
            self._start_load(self._initial_path)

    @on(Button.Pressed, "#browse-csv")
    def _browse(self) -> None:

        def _picked(path: str | None) -> None:
            if path:
                self.query_one("#csv-path", Input).value = path

        self.app.push_screen(
            BrowseModal(mode="open", suffixes=(".csv",), title="Pick a CSV file"),
            _picked,
        )

    @on(Button.Pressed, "#load-btn")
    def _load_pressed(self) -> None:
        path = self.query_one("#csv-path", Input).value.strip()
        if not path:
            self._set_status("Enter or browse for a CSV path.", ok=False)
            return
        self._start_load(path)

    def _start_load(self, path: str) -> None:
        self._set_status("Reading and profiling…", ok=None)
        self.query_one("#load-btn", Button).disabled = True
        self._load(path)

    @work(thread=True)
    def _load(self, path: str) -> None:
        app = cast("DtypeflowApp", self.app)
        try:
            loaded = app.service.load_dataset(path)
        except Exception as exc:
            self.app.call_from_thread(self._load_failed, str(exc))
            return
        self.app.call_from_thread(self._load_succeeded, loaded)

    def _load_succeeded(self, loaded: LoadedDataset) -> None:
        app = cast("DtypeflowApp", self.app)
        app.loaded = loaded
        app.selections = None
        self.query_one("#load-btn", Button).disabled = False
        self._set_status("", ok=None)
        self.app.push_screen(ConfigureScreen())

    def _load_failed(self, message: str) -> None:
        self.query_one("#load-btn", Button).disabled = False
        self._set_status(f"Could not load file: {message}", ok=False)

    def _set_status(self, message: str, *, ok: bool | None) -> None:
        status = self.query_one("#pick-status", Static)
        status.set_classes(_status_classes(ok=ok))
        status.update(message)


class ConfigureScreen(Screen[None]):
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "change_file", "Change file"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._index = 0

    def compose(self) -> ComposeResult:
        app = cast("DtypeflowApp", self.app)
        loaded = app.loaded
        assert loaded is not None
        yield Header()
        if not app.file_locked:
            with Horizontal(id="configure-header"):
                yield Button("← Change file", id="change-file")
        with VerticalScroll(id="configure-columns"):
            for index, column in enumerate(loaded.report.columns):
                yield ColumnPanel(column, app.service, loaded, id=f"panel-{index}")
        with Vertical(id="configure-footer"):
            yield Static("", id="configure-status", classes="status")
            with Horizontal(id="configure-footer-nav"):
                yield Button("← Back", id="back-btn")
                yield Static("", id="configure-counter", classes="footer-counter")
                yield Button("Next", id="next-btn", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        self._show_current()

    def _panels(self) -> list[ColumnPanel]:
        return list(self.query(ColumnPanel))

    def _show_current(self) -> None:
        panels = self._panels()
        for index, panel in enumerate(panels):
            panel.display = index == self._index
        self.query_one("#configure-counter", Static).update(
            f"{self._index + 1} of {len(panels)}",
        )
        self.query_one("#configure-status", Static).update("")
        self.query_one("#back-btn", Button).disabled = self._index == 0
        is_last = self._index == len(panels) - 1
        self.query_one("#next-btn", Button).label = "Finish" if is_last else "Next"

    @on(Button.Pressed, "#change-file")
    def _change_file(self) -> None:
        self.action_change_file()

    def action_change_file(self) -> None:
        app = cast("DtypeflowApp", self.app)
        if app.file_locked:
            return
        app.loaded = None
        self.app.pop_screen()

    @on(Button.Pressed, "#back-btn")
    def _back(self) -> None:
        if self._index > 0:
            self._index -= 1
            self._show_current()

    @on(Button.Pressed, "#next-btn")
    def _next(self) -> None:
        panels = self._panels()
        current = panels[self._index]
        if not current.is_valid():
            self.query_one("#configure-status", Static).update(
                f"Finish configuring {current.column.name!r} before continuing.",
            )
            return
        if self._index == len(panels) - 1:
            app = cast("DtypeflowApp", self.app)
            app.selections = {
                panel.column.name: panel.get_selection() for panel in panels
            }
            self.app.push_screen(ExportScreen())
            return
        self._index += 1
        self._show_current()


class ExportScreen(Screen[None]):
    BINDINGS: ClassVar[list[Binding]] = [Binding("escape", "back", "Back")]

    def compose(self) -> ComposeResult:
        app = cast("DtypeflowApp", self.app)
        loaded = app.loaded
        assert loaded is not None
        default_destination = str(Path(loaded.report.source).with_suffix(".parquet"))
        yield Header()
        with VerticalScroll():
            with Vertical(classes="panel hero"):
                yield Label("Save as Parquet", classes="app-title")
                with Horizontal(classes="field-row"):
                    yield Input(
                        value=default_destination,
                        placeholder="Output .parquet path",
                        id="dest-path",
                    )
                    yield Button("Choose destination…", id="browse-dest")
                yield Button(
                    "Store", id="store-btn", variant="primary", classes="primary-action",
                )
                yield Static("", id="export-status", classes="status")
            yield DataTable(id="export-result")
            with Horizontal(classes="browse-buttons"):
                yield Button("← Back", id="back-btn")
                yield Button("Quit", id="quit-btn", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#export-result", DataTable)
        table.add_columns("Column", "Arrow type")
        table.display = False
        self.query_one("#quit-btn", Button).display = False

    @on(Button.Pressed, "#browse-dest")
    def _browse(self) -> None:
        app = cast("DtypeflowApp", self.app)
        loaded = app.loaded
        assert loaded is not None
        default_name = Path(loaded.report.source).with_suffix(".parquet").name

        def _picked(path: str | None) -> None:
            if path:
                self.query_one("#dest-path", Input).value = path

        self.app.push_screen(
            BrowseModal(
                mode="save",
                suffixes=(".parquet",),
                title="Choose a destination",
                default_filename=default_name,
            ),
            _picked,
        )

    @on(Button.Pressed, "#store-btn")
    def _store_pressed(self) -> None:
        destination = self.query_one("#dest-path", Input).value.strip()
        if not destination:
            self._set_status("Enter or choose a destination path.", ok=False)
            return
        self._set_status("Storing…", ok=None)
        self.query_one("#store-btn", Button).disabled = True
        self._store(destination)

    @work(thread=True)
    def _store(self, destination: str) -> None:
        app = cast("DtypeflowApp", self.app)
        loaded = app.loaded
        selections = app.selections
        assert loaded is not None
        assert selections is not None
        try:
            written_schema = app.service.export(loaded, destination, selections)
        except Exception as exc:
            self.app.call_from_thread(self._store_failed, str(exc))
            return
        self.app.call_from_thread(self._store_succeeded, destination, written_schema)

    def _store_succeeded(
        self, destination: str, written_schema: tuple[tuple[str, str], ...],
    ) -> None:
        self.query_one("#store-btn", Button).disabled = False
        self._set_status(f"Wrote {destination}", ok=True)
        table = self.query_one("#export-result", DataTable)
        table.clear()
        for name, dtype in written_schema:
            table.add_row(name, dtype)
        table.display = True
        self.query_one("#quit-btn", Button).display = True

    def _store_failed(self, message: str) -> None:
        self.query_one("#store-btn", Button).disabled = False
        self._set_status(f"Export failed: {message}", ok=False)

    @on(Button.Pressed, "#back-btn")
    def _back(self) -> None:
        self.action_back()

    def action_back(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#quit-btn")
    def _quit(self) -> None:
        self.app.exit()

    def _set_status(self, message: str, *, ok: bool | None) -> None:
        status = self.query_one("#export-status", Static)
        status.set_classes(_status_classes(ok=ok))
        status.update(message)


class DtypeflowApp(App[None]):
    CSS_PATH = "app.tcss"
    TITLE = "dtypeflow"
    BINDINGS: ClassVar[list[Binding]] = [Binding("ctrl+q", "quit", "Quit")]

    def __init__(self, initial_path: str | None = None) -> None:
        super().__init__()
        self.service = DtypeflowService()
        self.loaded: LoadedDataset | None = None
        self.selections: dict[str, ColumnSelection] | None = None
        self.file_locked = initial_path is not None
        self._pick_screen = PickFileScreen(initial_path=initial_path)

    def on_mount(self) -> None:
        self.push_screen(self._pick_screen)


if __name__ == "__main__":
    DtypeflowApp().run()
