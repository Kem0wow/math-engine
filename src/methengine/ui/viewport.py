import tkinter as tk
import math
from theme import THEME

class Viewport(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg=THEME["content_bg"], highlightthickness=0)
        
        self.scale = 50.0  # 1 birim kaç piksel?
        self.offset_x = 0.0
        self.offset_y = 0.0
        
        self.mode = "move"
        self.objects = {"points": [], "lines": [], "functions": []}
        
        # Tool yardımcıları
        self.temp_point = None

        # Bindings
        self.bind("<ButtonPress-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<MouseWheel>", self.on_zoom)
        self.bind("<Configure>", lambda e: self.redraw())
        
        self.last_mouse_x = 0
        self.last_mouse_y = 0

    def to_screen(self, mx, my):
        sx = self.winfo_width()/2 + (mx * self.scale) + self.offset_x
        sy = self.winfo_height()/2 - (my * self.scale) + self.offset_y
        return sx, sy

    def to_math(self, sx, sy):
        mx = (sx - self.winfo_width()/2 - self.offset_x) / self.scale
        my = (self.winfo_height()/2 + self.offset_y - sy) / self.scale
        return mx, my

    def redraw(self):
        self.delete("all")
        self.draw_grid()
        
        # Fonksiyonları çiz (Algebra)
        for func_str in self.objects["functions"]:
            self.draw_function(func_str)
            
        # Noktaları çiz (Tools)
        for p in self.objects["points"]:
            sx, sy = self.to_screen(p[0], p[1])
            self.create_oval(sx-4, sy-4, sx+4, sy+4, fill=THEME["accent"], outline="white")

    def draw_grid(self):
        w, h = self.winfo_width(), self.winfo_height()
        cx, cy = w/2 + self.offset_x, h/2 + self.offset_y
        
        # Izgara Çizgileri
        step = self.scale
        start_x = cx % step
        for x in range(int(start_x), w, int(step)):
            self.create_line(x, 0, x, h, fill=THEME["grid_light"])
        
        start_y = cy % step
        for y in range(int(start_y), h, int(step)):
            self.create_line(0, y, w, y, fill=THEME["grid_light"])

        # Ana Eksenler
        self.create_line(0, cy, w, cy, fill=THEME["grid_dark"], width=2)
        self.create_line(cx, 0, cx, h, fill=THEME["grid_dark"], width=2)

    def draw_function(self, expr):
        points = []
        w = self.winfo_width()
        for sx in range(0, w, 2):
            mx, _ = self.to_math(sx, 0)
            try:
                # Güvenli matematiksel değerlendirme
                # 'x' yerine mx koyarak y'yi bulur
                allowed_names = {"x": mx, "sin": math.sin, "cos": math.cos, "tan": math.tan, "sqrt": math.sqrt, "exp": math.exp}
                my = eval(expr.replace("^", "**"), {"__builtins__": None}, allowed_names)
                points.append(self.to_screen(mx, my))
            except: continue
        
        if len(points) > 1:
            self.create_line(points, fill=THEME["accent"], width=2, smooth=True)

    def on_click(self, event):
        mx, my = self.to_math(event.x, event.y)
        
        if self.mode == "point":
            self.objects["points"].append((mx, my))
            self.redraw()
        
        self.last_mouse_x, self.last_mouse_y = event.x, event.y

    def on_drag(self, event):
        if self.mode == "move":
            self.offset_x += event.x - self.last_mouse_x
            self.offset_y += event.y - self.last_mouse_y
            self.last_mouse_x, self.last_mouse_y = event.x, event.y
            self.redraw()

    def on_zoom(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.scale *= factor
        self.redraw()