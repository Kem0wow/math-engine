import tkinter as tk
from PIL import Image, ImageTk
from theme import THEME

class CustomBtn:
    _icon_cache = {}
    
    @classmethod
    def add_menu_button(cls, parent, icon_path, text, command):
        btn = cls.add_square_button(parent, icon_path, text, command)
        btn.pack(pady=10, padx=10)
        return btn

    @classmethod
    def add_tool_button(cls, parent, icon_path, text, command, r, c):
        btn = cls.add_square_button(parent, icon_path, text, command)
        btn.grid(row=r, column=c, padx=10, pady=10)
        return btn

    @classmethod
    def add_square_button(cls, parent, icon_path, text, command):
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

        if icon_path not in cls._icon_cache:
            try:
                img = Image.open(icon_path).resize((30, 30), Image.Resampling.LANCZOS)
                cls._icon_cache[icon_path] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading icon {icon_path}: {e}")
                cls._icon_cache[icon_path] = None
        
        icon = cls._icon_cache[icon_path]
        
        if icon:
            lbl_icon = tk.Label(box, image=icon, bg=THEME["button_bg"])
            lbl_icon.image = icon
            lbl_icon.pack(pady=(10, 2))
        else:
            lbl_icon = tk.Label(box, text="?", bg=THEME["button_bg"], font=("Segoe UI", 16))
            lbl_icon.pack(pady=(10, 2))

        lbl_text = tk.Label(
            box,
            text=text,
            fg=THEME["text"],
            bg=THEME["button_bg"],
            font=("Segoe UI", 9)
        )
        lbl_text.pack()

        widgets = [box, lbl_icon, lbl_text]
        for w in widgets:
            w.bind("<Button-1>", lambda e: command())
            w.bind("<Enter>", lambda e: cls._on_enter(widgets))
            w.bind("<Leave>", lambda e: cls._on_leave(widgets))

        return box
    
    @staticmethod
    def _on_enter(widgets):
        for w in widgets:
            if isinstance(w, tk.Frame):
                w.config(bg=THEME["button_hover"])
            elif isinstance(w, tk.Label):
                w.config(bg=THEME["button_hover"])
    
    @staticmethod
    def _on_leave(widgets):
        for w in widgets:
            if isinstance(w, tk.Frame):
                w.config(bg=THEME["button_bg"])
            elif isinstance(w, tk.Label):
                w.config(bg=THEME["button_bg"])