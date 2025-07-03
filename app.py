from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.containers import Center, Vertical, Horizontal
from textual.screen import Screen

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
        yield Center (
            Vertical(
            *[
                Static(f"[reverse]{tab}[/reverse]" if i == self.tab_index else tab)
                for i, (tab, _) in enumerate(HELP_TABS)
            ],
            id="help-menu",
        )
    )
        yield Static(HELP_TABS[self.tab_index][1], id="help-content")


class TabScreen(Screen):
    def __init__(self):
        super().__init__()
        self.active_tab = "terminal"
        self.help_tab_index = 0

    def compose(self) -> ComposeResult:
        yield Center(
            Vertical(
                Static(self.render_tab_bar(), id="tab-bar"),
                Static(id="tab-content"),
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
            id="help-content"
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
                id="tab-content"
            )
        elif self.active_tab == "set":
            return Static(
                "Set-Config Tab\n"
                "===============\n"
                "Here you can configure system settings:\n"
                "- Network\n"
                "- Display\n"
                "- User preferences\n"
                "\n"
                "Press 'b' to return to Baybay terminal.",
                id="tab-content"
            )
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
                id="tab-content"
            )
        elif self.active_tab == "help":
            return self.render_help_widget()
        return Static("")

    def on_mount(self):
        self.query_one("#tab-content", Static | Horizontal).mount(self.render_tab_content())

    def on_key(self, event):
        key = event.key
        if self.active_tab == "help":
            if key == "up":
                self.help_tab_index = (self.help_tab_index - 1) % len(HELP_TABS)
            elif key == "down":
                self.help_tab_index = (self.help_tab_index + 1) % len(HELP_TABS)
            elif key == "b":
                self.active_tab = "terminal"
            elif key == "q":
                self.app.exit()
            container = self.query_one("#help-content", Horizontal)
            container.remove()
            self.query_one("#tab-area").mount(self.render_help_widget(), before="#footer-line")
            return

        if key in {"s", "d", "h", "b"}:
            self.active_tab = {
                "s": "set",
                "d": "download",
                "h": "help",
                "b": "terminal"
            }[key]
            self.query_one("#tab-content", Static | Horizontal).remove()
            self.query_one("#tab-area").mount(self.render_tab_content(), before="#footer-line")

        elif key == "q":
            self.app.exit()


class BaybayApp(App):
    CSS = """
    Screen {
        align: center middle;
        background: #181b20;
    }

    #tab-area {
        align: center middle;
        padding: 1;
    }

    #tab-bar {
        color: white;
        content-align: center middle;
    }

    #tab-content {
        padding: 1;
        content-align: center middle;
        height: 25;
        color: green;
    }

    #help-content {
        padding: 1;
        content-align: center middle;
        height: 25;
        color: green;
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

    #help-menu {
        width: 40%;
        padding: 1;
        color: cyan;
    }

    #help-content {
        width: 60%;
        padding: 2;
        color: white;
    }
    """

    def on_mount(self):
        self.push_screen(TabScreen())


if __name__ == "__main__":
    from loader import loader
    loader()
    BaybayApp().run()
