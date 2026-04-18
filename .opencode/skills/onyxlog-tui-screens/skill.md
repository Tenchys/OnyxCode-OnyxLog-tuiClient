---
name: onyxlog-tui-screens
description: Patrones de implementacion de pantallas y widgets Textual para el OnyxLog TUI Client. Compose, navegacion, workers, bindings y notificaciones.
metadata:
  audience: developers
  workflow: onyxlog-tui
---

## Crear una Screen nueva

1. Crear archivo en `src/screens/<nombre>.py`
2. Definir clase que herede de `Screen`
3. Implementar `compose()` con los widgets de la pantalla
4. Implementar `on_mount()` para carga inicial de datos via worker
5. Registrar en `src/app.py` importando la screen

## Estructura de una Screen

```python
from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Header, Footer, Static


class LogsScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("f", "filter", "Filter"),
        ("/", "search", "Search"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="logs-table")
        yield Footer()

    async def on_mount(self) -> None:
        self.run_worker(self._load_logs())

    async def _load_logs(self) -> None:
        table = self.query_one("#logs-table", DataTable)
        table.loading = True
        try:
            client = self.app.client
            logs = await client.get_logs()
            self._populate_table(table, logs)
            self.notify(f"{len(logs)} logs loaded", severity="information")
        except ApiClientError as e:
            self.notify(e.message, severity="error")
        finally:
            table.loading = False

    def _populate_table(self, table: DataTable, logs: list) -> None:
        table.clear(columns=True)
        table.add_columns("Timestamp", "Level", "App", "Message")
        for log in logs:
            table.add_row(log.timestamp, log.level, log.app_id, log.message)

    def action_refresh(self) -> None:
        self.run_worker(self._load_logs())

    def action_filter(self) -> None:
        self.app.push_screen(FilterDialog())

    def action_search(self) -> None:
        self.app.push_screen(SearchDialog())
```

## Navegacion entre pantallas

OnyxLog TUI usa un patron de navegacion jerarquico:

```
LoginScreen → DashboardScreen → ApplicationsScreen
                            → LogsScreen
                            → SettingsScreen
```

Metodos de navegacion:

| Metodo | Uso |
|--------|-----|
| `app.push_screen(ScreenClass)` | Navegar a una nueva pantalla (se apila sobre la actual) |
| `app.pop_screen()` | Volver a la pantalla anterior |
| `app.switch_screen(ScreenClass)` | Reemplazar la pantalla actual (para tabs del dashboard) |

Patron en `app.py`:

```python
from textual.app import App

from src.screens.login import LoginScreen
from src.screens.dashboard import DashboardScreen


class OnyxLogApp(App):
    CSS_PATH = "styles.tcss"

    def on_mount(self) -> None:
        self.push_screen(LoginScreen())
```

## Workers (tareas async)

Las llamadas HTTP y operaciones de DB deben ejecutarse en workers para no bloquear la UI.

```python
from textual.worker import Worker, WorkerState


class MyScreen(Screen):
    async def on_mount(self) -> None:
        self.run_worker(self._load_data(), name="load_data")

    async def _load_data(self) -> None:
        try:
            result = await self.app.client.get_something()
            self._update_ui(result)
        except ApiClientError as e:
            self.notify(e.message, severity="error")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name == "load_data":
            if event.state == WorkerState.SUCCESS:
                self.notify("Data loaded", severity="information")
            elif event.state == WorkerState.ERROR:
                self.notify("Failed to load data", severity="error")
```

Reglas de workers:
- NUNCA usar `time.sleep()` — usar `asyncio.sleep()` si se necesita espera
- Workers corren en thread separado, comunicar con UI via `call_from_thread()` si es necesario
- Nombrar workers con `name=` para poder monitorear su estado

## Notificaciones

```python
# Informacion
self.notify("Operation completed", severity="information")

# Advertencia
self.notify("No results found", severity="warning")

# Error
self.notify("Connection failed", severity="error")
```

Timeouts:
- `information`: 3 segundos (default)
- `warning`: 5 segundos
- `error`: 5 segundos

## Bindings (atajos de teclado)

```python
class MyScreen(Screen):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("n", "new_item", "New"),
        ("escape", "go_back", "Back"),
    ]
```

Reglas:
- `q` para quit
- `r` para refresh/recargar
- `n` para nuevo item
- `escape` para volver atras
- `/` para buscar
- `f` para filtrar

## Dialogos modales

Para formularios y confirmaciones, usar `ModalScreen`:

```python
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class ConfirmDialog(ModalScreen[bool]):
    def compose(self) -> ComposeResult:
        yield Label("Are you sure?")
        yield Button("Yes", variant="primary", id="confirm-btn")
        yield Button("No", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            self.dismiss(True)
        else:
            self.dismiss(False)
```

Uso desde una Screen:

```python
def action_delete(self) -> None:
    self.app.push_screen(ConfirmDialog(), self._handle_delete_confirm)

def _handle_delete_confirm(self, confirmed: bool) -> None:
    if confirmed:
        self.run_worker(self._do_delete())
```

## DataTable (tablas de logs/aplicaciones)

```python
from textual.widgets import DataTable

def compose(self) -> ComposeResult:
    yield DataTable(id="items-table")

async def on_mount(self) -> None:
    table = self.query_one("#items-table", DataTable)
    table.add_columns("Name", "Status", "Created")
    self.run_worker(self._load_items())
```

Reglas para tablas:
- Siempre con `id` para poder hacer `query_one`
- `cursor_type="row"` para seleccion por fila
- `loading = True` durante carga de datos
- Definir `on_data_table_row_selected` para acciones al seleccionar

## Formularios (Input, Select)

```python
from textual.widgets import Input, Select, Button


class CreateAppScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Application name", id="name-input")
        yield Input(placeholder="Application ID", id="appid-input")
        yield Select(
            [("Development", "development"), ("Testing", "testing"), ("Production", "production")],
            id="env-select",
        )
        yield Button("Create", variant="primary", id="create-btn")
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create-btn":
            await self._handle_create()

    async def _handle_create(self) -> None:
        name = self.query_one("#name-input", Input).value
        app_id = self.query_one("#appid-input", Input).value
        environment = self.query_one("#env-select", Select).value
        # Validar y llamar API...
```

## Rich (formateo de tablas y contenido)

```python
from rich.table import Table
from rich.text import Text

def _format_level(self, level: str) -> Text:
    colors = {"ERROR": "red", "WARN": "yellow", "INFO": "green", "DEBUG": "dim"}
    return Text(level, style=colors.get(level, "white"))
```