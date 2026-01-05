import tkinter as tk
from theme import THEME
from buttons import CustomBtn


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("MethEngine")
        self.geometry("1200x800")
        self.minsize(1000, 800)
        self.configure(bg=THEME["content_bg"])

        # ================= STATE =================
        self.current_panel = None
        self.algebra_entries = []
        self.algebra_entry_map = {}
        self.algebra_widgets = []
        self.algebra_canvas = None
        self.mousewheel_bound = False

        # ================= UI SETUP =================
        self._setup_ui()
        self._setup_menu_buttons()
        
        self.home_panel()

    def _setup_ui(self):
        self.container = tk.Frame(self, bg=THEME["content_bg"])
        self.container.pack(fill=tk.BOTH, expand=True)

        self.menubar = tk.Frame(
            self.container,
            width=90,
            bg=THEME["menu_bg"],
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        self.menubar.pack(side="left", fill=tk.Y)
        self.menubar.pack_propagate(False)

        self.panelbar = tk.Frame(
            self.container,
            width=400,
            bg=THEME["panel_bg"],
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        self.panelbar.pack(side="left", fill=tk.Y)
        self.panelbar.pack_propagate(False)

        self.content = tk.Frame(self.container, bg=THEME["content_bg"])
        self.content.pack(side="left", fill=tk.BOTH, expand=True)

    def _setup_menu_buttons(self):
        CustomBtn.add_menu_button(self.menubar, "./img/home.png", "Home", self.home_panel)
        CustomBtn.add_menu_button(self.menubar, "./img/calc.png", "Algebra", self.algebra_panel)
        CustomBtn.add_menu_button(self.menubar, "./img/shape.png", "Tools", self.tool_panel)
        CustomBtn.add_menu_button(self.menubar, "./img/settings.png", "Settings", self.settings_panel)

    # ================= PANEL MANAGEMENT =================

    def clear_panel(self):
        if self.mousewheel_bound:
            self.unbind_all("<MouseWheel>")
            self.mousewheel_bound = False
        
        if self.algebra_canvas:
            self.algebra_canvas = None
        
        self.algebra_entry_map.clear()
        
        for widget in self.panelbar.winfo_children():
            widget.destroy()

    def panel_title(self, text):
        tk.Label(
            self.panelbar,
            text=text,
            fg=THEME["text"],
            bg=THEME["panel_bg"],
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=24, pady=(24, 10))

    def panel_text(self, text):
        tk.Label(
            self.panelbar,
            text=text,
            fg=THEME["subtext"],
            bg=THEME["panel_bg"],
            font=("Segoe UI", 11),
            justify="left",
            wraplength=350
        ).pack(anchor="w", padx=24, pady=6)

    # ================= PANELS =================

    def home_panel(self):
        if self.current_panel == "home":
            return
        
        self.current_panel = "home"
        self.clear_panel()
        
        self.panel_title("Home")
        self.panel_text(
            "Welcome to MethEngine.\n\n"
            "• Algebra panel for equation workflows\n"
            "• Tools panel for geometric utilities\n\n"
            "Designed to stay readable for long sessions."
        )

    def settings_panel(self):
        if self.current_panel == "settings":
            return
        
        self.current_panel = "settings"
        self.clear_panel()

        self.panel_title("Settings")

        grid = tk.Frame(self.panelbar, bg=THEME["panel_bg"])
        grid.pack(padx=12, pady=10)

        settings = [
            ("./img/import.png", "Import", lambda: print("IMPORT")),
            ("./img/export.png", "Export", lambda: print("EXPORT")),
            ("./img/clear.png", "Clear All", lambda: print("CLEAR"))
        ]

        for i, (icon, name, cmd) in enumerate(settings):
            r = i // 4
            c = i % 4
            CustomBtn.add_tool_button(grid, icon, name, cmd, r, c)

    def tool_panel(self):
        if self.current_panel == "tools":
            return

        self.current_panel = "tools"
        self.clear_panel()

        self.panel_title("Tools")

        grid = tk.Frame(self.panelbar, bg=THEME["panel_bg"])
        grid.pack(padx=12, pady=10)

        tools = [
            ("./img/move.png", "Move", self.move_tool),
            ("./img/point.png", "Point", self.point_tool),
            ("./img/line.png", "Line", self.line_tool),
            ("./img/circle.png", "Circle", self.circle_tool),
            ("./img/half-circle.png", "Half Circle", self.halfcircle_tool),
            ("./img/triangle.png", "Triangle", self.triangle_tool),
            ("./img/text.png", "Text", self.text_tool),
            ("./img/erease.png", "Erease", self.text_tool)
        ]

        for i, (icon, name, cmd) in enumerate(tools):
            r = i // 4
            c = i % 4
            CustomBtn.add_tool_button(grid, icon, name, cmd, r, c)

    def algebra_panel(self):
        if self.current_panel == "algebra":
            return

        self.current_panel = "algebra"
        self.clear_panel()
        
        self.panel_title("Algebra")
        self.panel_text(
            "Create and manipulate algebraic expressions,\n"
            "visualize functions and variables."
        )

        CustomBtn.add_square_button(
            self.panelbar,
            "./img/plus.png",
            "New",
            self.add_algebra_entry
        ).pack(pady=10, padx=24)

        self._setup_algebra_scroll()
        
        self.algebra_widgets = []
        for entry_text in self.algebra_entries:
            self._create_algebra_entry(entry_text)

        self.algebra_container.bind("<Button-1>", lambda e: self.focus())

    def _setup_algebra_scroll(self):
        scroll_frame = tk.Frame(self.panelbar, bg=THEME["panel_bg"])
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 10))

        self.algebra_canvas = tk.Canvas(
            scroll_frame,
            bg=THEME["panel_bg"],
            highlightthickness=0
        )
        
        scrollbar = tk.Scrollbar(
            scroll_frame,
            orient="vertical",
            command=self.algebra_canvas.yview
        )
        
        self.algebra_container = tk.Frame(
            self.algebra_canvas,
            bg=THEME["panel_bg"]
        )

        self.algebra_container.bind(
            "<Configure>",
            lambda e: self.algebra_canvas.configure(
                scrollregion=self.algebra_canvas.bbox("all")
            )
        )

        self.algebra_canvas.create_window(
            (0, 0), 
            window=self.algebra_container, 
            anchor="nw",
            width=350
        )

        self.algebra_canvas.configure(yscrollcommand=scrollbar.set)

        self.algebra_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill=tk.Y)

        def on_mousewheel(event):
            self.algebra_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.bind_all("<MouseWheel>", on_mousewheel)
        self.mousewheel_bound = True

    # ================= ALGEBRA ENTRY MANAGEMENT =================

    def add_algebra_entry(self):
        wrapper, var, entry = self._create_algebra_entry("")
        
        entry.focus_set()
        
        self.algebra_canvas.update_idletasks()
        self.algebra_canvas.yview_moveto(1.0)

    def _create_algebra_entry(self, text=""):
        wrapper = tk.Frame(self.algebra_container, bg=THEME["panel_bg"])
        wrapper.pack(fill=tk.X, pady=4)

        var = tk.StringVar(value=text)

        entry = tk.Entry(
            wrapper,
            textvariable=var,
            font=("Segoe UI", 11),
            relief="solid",
            bd=1
        )
        entry.pack(side="left", fill=tk.X, expand=True, ipady=4)
        
        self.algebra_entry_map[id(entry)] = text

        delete_btn = tk.Button(
            wrapper,
            text="✕",
            font=("Segoe UI", 10),
            width=3,
            relief="flat",
            bg=THEME["button_bg"],
            command=lambda: self.delete_algebra_entry(wrapper, entry)
        )
        delete_btn.pack(side="left", padx=6)

        entry.bind("<Return>", lambda e: self.save_entry(entry))
        entry.bind("<FocusOut>", lambda e: self.save_entry(entry))

        self.algebra_widgets.append((wrapper, entry))
        
        return wrapper, var, entry

    def save_entry(self, entry):
        new_text = entry.get().strip()
        entry_id = id(entry)
        old_text = self.algebra_entry_map.get(entry_id, "")
        
        if not new_text:
            return
        
        if new_text == old_text:
            return
        
        if old_text and old_text in self.algebra_entries:
            self.algebra_entries.remove(old_text)
        
        if new_text not in self.algebra_entries:
            self.algebra_entries.append(new_text)
            print(f"Saved: '{new_text}'")
            print(f"All entries: {self.algebra_entries}")
        
        self.algebra_entry_map[entry_id] = new_text

    def delete_algebra_entry(self, frame, entry):
        entry_id = id(entry)
        text = self.algebra_entry_map.get(entry_id, "")
        
        if text in self.algebra_entries:
            self.algebra_entries.remove(text)
            print(f"Deleted: '{text}'")
            print(f"All entries: {self.algebra_entries}")
        
        if entry_id in self.algebra_entry_map:
            del self.algebra_entry_map[entry_id]
        
        self.algebra_widgets = [(w, e) for w, e in self.algebra_widgets if w != frame]
        frame.destroy()

    # ================= TOOL ACTIONS =================

    def move_tool(self):
        print("Move tool activated")

    def point_tool(self):
        print("Point tool activated")

    def line_tool(self):
        print("Line tool activated")

    def circle_tool(self):
        print("Circle tool activated")
    
    def halfcircle_tool(self):
        print("Half Circle tool activated")

    def triangle_tool(self):
        print("Triangle tool activated")

    def text_tool(self):
        print("Text tool activated")

    def erease_tool(self):
        print("Erease tool activated")

    # ================= RUN =================

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()