import tkinter as tk
from PIL import Image, ImageTk


# ================= SOFT LIGHT THEME =================
THEME = {
    "menu_bg": "#ececec",
    "panel_bg": "#f3f3f3",
    "content_bg": "#fafafa",
    "button_bg": "#e0e0e0",
    "button_hover": "#d2d2d2",
    "text": "#2b2b2b",
    "subtext": "#5f5f5f",
    "accent": "#3f8cff",
    "border": "#cfcfcf"
}


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("MethEngine")
        self.geometry("1200x800")
        self.minsize(1000, 800)
        self.configure(bg=THEME["content_bg"])

        # ================= STATE =================
        self.current_panel = None  # Track current panel to prevent refresh
        self.algebra_entries = []
        self.algebra_widgets = []  # Store widget references
        self.algebra_canvas = None  # Store canvas reference for cleanup

        # ================= ROOT =================
        self.container = tk.Frame(self, bg=THEME["content_bg"])
        self.container.pack(fill=tk.BOTH, expand=True)

        # ================= MENU BAR =================
        self.menubar = tk.Frame(
            self.container, width=90,
            bg=THEME["menu_bg"],
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        self.menubar.pack(side="left", fill=tk.Y)
        self.menubar.pack_propagate(False)

        # ================= PANEL BAR =================
        self.panelbar = tk.Frame(
            self.container, width=400,
            bg=THEME["panel_bg"],
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        self.panelbar.pack(side="left", fill=tk.Y)
        self.panelbar.pack_propagate(False)

        # ================= CONTENT =================
        self.content = tk.Frame(self.container, bg=THEME["content_bg"])
        self.content.pack(side="left", fill=tk.BOTH, expand=True)

        # ================= MENU BUTTONS =================
        self.add_menu_button("./img/home.png", "Home", self.home_panel)
        self.add_menu_button("./img/calc.png", "Algebra", self.algebra_panel)
        self.add_menu_button("./img/shape.png", "Tools", self.tool_panel)

        self.home_panel()

    # ================= HELPERS =================

    def clear_panel(self):
        # Unbind mousewheel if canvas exists
        if self.algebra_canvas:
            self.unbind_all("<MouseWheel>")
            self.algebra_canvas = None
        
        for w in self.panelbar.winfo_children():
            w.destroy()

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
            return  # Don't refresh if already on this panel
        
        self.current_panel = "home"
        self.clear_panel()
        self.panel_title("Home")
        self.panel_text(
            "Welcome to MethEngine.\n\n"
            "• Algebra panel for equation workflows\n"
            "• Tools panel for geometric utilities\n\n"
            "Designed to stay readable for long sessions."
        )

    def tool_panel(self):
        if self.current_panel == "tools":
            return  # Don't refresh if already on this panel
        
        self.current_panel = "tools"
        self.clear_panel()
        self.panel_title("Tools")
        
        grid = tk.Frame(self.panelbar, bg=THEME["panel_bg"])
        grid.pack(padx=24, pady=10)
        
        self.add_tool_button(grid, "./img/point.png", "Point", self.point_tool, 0, 0)
        self.add_tool_button(grid, "./img/line.png", "Line", self.line_tool, 0, 1)
        self.add_tool_button(grid, "./img/circle.png", "Circle", self.circle_tool, 0, 2)
        self.add_tool_button(grid, "./img/triangle.png", "Triangle", self.triangle_tool, 0, 3)

    def point_tool(self):
        print("Point activated")

    def line_tool(self):
        print("Line activated")

    def circle_tool(self):
        print("Circle activated")

    def triangle_tool(self):
        print("Triangle activated")

    def algebra_panel(self):
        if self.current_panel == "algebra":
            return  # Don't refresh if already on this panel

        self.current_panel = "algebra"
        self.clear_panel()
        self.panel_title("Algebra")
        self.panel_text(
            "Create and manipulate algebraic expressions,\n"
            "visualize functions and variables."
        )

        self.add_square_button(
            self.panelbar,
            "./img/plus.png",
            "New",
            self.add_algebra_entry
        ).pack(pady=10, padx=24)

        # Create scrollable frame container
        scroll_frame = tk.Frame(self.panelbar, bg=THEME["panel_bg"])
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 10))

        # Create canvas and scrollbar
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

        # Configure canvas scrolling
        self.algebra_container.bind(
            "<Configure>",
            lambda e: self.algebra_canvas.configure(scrollregion=self.algebra_canvas.bbox("all"))
        )

        canvas_window = self.algebra_canvas.create_window(
            (0, 0), 
            window=self.algebra_container, 
            anchor="nw",
            width=350  # Match the panel width minus padding
        )

        self.algebra_canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        self.algebra_canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill=tk.Y)

        # Mouse wheel scrolling
        def on_mousewheel(event):
            self.algebra_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.bind_all("<MouseWheel>", on_mousewheel)

        # Restore existing entries
        self.algebra_widgets = []
        for entry_text in self.algebra_entries:
            self.restore_algebra_entry(entry_text)

        # Click empty area to unfocus
        self.algebra_container.bind("<Button-1>", lambda e: self.focus())

    # ================= ALGEBRA ENTRY =================

    def add_algebra_entry(self):
        wrapper = tk.Frame(
            self.algebra_container,
            bg=THEME["panel_bg"]
        )
        wrapper.pack(fill=tk.X, pady=4)

        var = tk.StringVar()

        entry = tk.Entry(
            wrapper,
            textvariable=var,
            font=("Segoe UI", 11),
            relief="solid",
            bd=1
        )
        entry.pack(side="left", fill=tk.X, expand=True, ipady=4)

        delete_btn = tk.Button(
            wrapper,
            text="✕",
            font=("Segoe UI", 10),
            width=3,
            relief="flat",
            bg=THEME["button_bg"],
            command=lambda: self.delete_algebra_entry(wrapper, var)
        )
        delete_btn.pack(side="left", padx=6)

        self.algebra_widgets.append((wrapper, var))

        entry.bind("<Return>", lambda e: self.save_entry(var))
        entry.bind("<FocusOut>", lambda e: self.save_entry(var))

        entry.focus_set()
        
        # Scroll to bottom to show new entry
        self.algebra_canvas.update_idletasks()
        self.algebra_canvas.yview_moveto(1.0)

    def restore_algebra_entry(self, text):
        """Restore an existing algebra entry when returning to the panel"""
        wrapper = tk.Frame(
            self.algebra_container,
            bg=THEME["panel_bg"]
        )
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

        delete_btn = tk.Button(
            wrapper,
            text="✕",
            font=("Segoe UI", 10),
            width=3,
            relief="flat",
            bg=THEME["button_bg"],
            command=lambda: self.delete_algebra_entry(wrapper, var)
        )
        delete_btn.pack(side="left", padx=6)

        self.algebra_widgets.append((wrapper, var))

        entry.bind("<Return>", lambda e: self.save_entry(var))
        entry.bind("<FocusOut>", lambda e: self.save_entry(var))

    def save_entry(self, var):
        text = var.get().strip()
        if text and text not in self.algebra_entries:
            self.algebra_entries.append(text)
            print("Saved:", text)
            print("All algebra entries:", self.algebra_entries)

    def delete_algebra_entry(self, frame, var):
        text = var.get().strip()
        if text in self.algebra_entries:
            self.algebra_entries.remove(text)
            print("Deleted:", text)
            print("All algebra entries:", self.algebra_entries)
        
        # Remove from widget list
        self.algebra_widgets = [(w, v) for w, v in self.algebra_widgets if w != frame]
        frame.destroy()

    # ================= BUTTONS =================

    def add_menu_button(self, icon_path, text, command):
        self.add_square_button(
            self.menubar, icon_path, text, command
        ).pack(pady=10, padx=10)

    def add_tool_button(self, parent, icon_path, text, command, r, c):
        btn = self.add_square_button(parent, icon_path, text, command)
        btn.grid(row=r, column=c, padx=10, pady=10)

    def add_square_button(self, parent, icon_path, text, command):
        box = tk.Frame(
            parent,
            width=70,
            height=70,
            bg=THEME["button_bg"],
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=THEME["border"]
        )
        box.pack_propagate(False)

        img = Image.open(icon_path).resize((26, 26))
        icon = ImageTk.PhotoImage(img)

        lbl_icon = tk.Label(box, image=icon, bg=THEME["button_bg"])
        lbl_icon.image = icon
        lbl_icon.pack(pady=(10, 2))

        lbl_text = tk.Label(
            box,
            text=text,
            fg=THEME["text"],
            bg=THEME["button_bg"],
            font=("Segoe UI", 9)
        )
        lbl_text.pack()

        for w in (box, lbl_icon, lbl_text):
            w.bind("<Button-1>", lambda e: command())
            w.bind("<Enter>", lambda e, b=box: b.config(bg=THEME["button_hover"]))
            w.bind("<Leave>", lambda e, b=box: b.config(bg=THEME["button_bg"]))

        return box

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    MainWindow().run()