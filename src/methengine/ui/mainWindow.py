import tkinter as tk
import math
import string
from theme import THEME
from buttons import CustomBtn

class AlgebraFunction:
    def __init__(self, expression, mx=0, my=0):
        self.expression = expression
        self.mx = mx
        self.my = my
        self.visible = True
        self.color = THEME["accent"]
        self.line_width = 3
        self.dash_pattern = None
        self._cached_points = None  # Cache for rendered points
        self._cache_scale = None
        self._cache_offset = None

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("MethEngine")
        self.geometry("1200x800")
        self.minsize(1000, 800)
        self.configure(bg=THEME["content_bg"])

        # ================= STATE =================
        self.current_panel = None
        self.algebra_functions = []
        self.algebra_widgets = []
        self.algebra_canvas = None
        self.selected_algebra_func = None
        self.algebra_objects = {}
        
        self.colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", 
                       "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
                       "#F8C471", "#82E0AA", "#F1948A", "#85929E", "#AED6F1"]

        self.scale = 50.0
        self.offset_x = 0
        self.offset_y = 0
        self.tool_mode = "move"
        
        self.points = []
        self.shapes = []
        self.point_counter = 0
        
        self.selected_point = None
        self.selected_shape = None
        self.temp_points = []
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        
        self.is_dragging = False
        self.drag_target = None
        
        self.show_grid = True
        self.show_coordinates = True
        
        # Performans için
        self._render_scheduled = False
        self._last_render_time = 0
        self._render_cooldown = 16  # ~60 FPS

        # ================= UI SETUP =================
        self._setup_ui()
        self._setup_menu_buttons()
        
        self.home_panel()
        self.render_canvas()

    def _setup_ui(self):
        self.container = tk.Frame(self, bg=THEME["content_bg"])
        self.container.pack(fill=tk.BOTH, expand=True)

        self.menubar = tk.Frame(self.container, width=90, bg=THEME["menu_bg"], highlightthickness=1, highlightbackground=THEME["border"])
        self.menubar.pack(side="left", fill=tk.Y)
        self.menubar.pack_propagate(False)

        self.panelbar = tk.Frame(self.container, width=400, bg=THEME["panel_bg"], highlightthickness=1, highlightbackground=THEME["border"])
        self.panelbar.pack(side="left", fill=tk.Y)
        self.panelbar.pack_propagate(False)

        self.content = tk.Canvas(self.container, bg="#1e1e1e", highlightthickness=0)
        self.content.pack(side="left", fill=tk.BOTH, expand=True)

        self.content.bind("<ButtonPress-1>", self.on_canvas_click)
        self.content.bind("<B1-Motion>", self.on_canvas_drag)
        self.content.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.content.bind("<MouseWheel>", self.on_canvas_zoom)
        self.content.bind("<Configure>", lambda e: self.schedule_render())
        
        self.bind("<Delete>", lambda e: self.delete_selected())
        self.bind("<Escape>", lambda e: self.deselect_all())
        self.bind("<g>", lambda e: self.toggle_grid())
        self.bind("<c>", lambda e: self.toggle_coordinates())

    def _setup_menu_buttons(self):
        CustomBtn.add_menu_button(self.menubar, "./img/home.png", "Home", self.home_panel)
        CustomBtn.add_menu_button(self.menubar, "./img/calc.png", "Algebra", self.algebra_panel)
        CustomBtn.add_menu_button(self.menubar, "./img/shape.png", "Tools", self.tool_panel)
        CustomBtn.add_menu_button(self.menubar, "./img/settings.png", "Settings", self.settings_panel)

    def schedule_render(self):
        """Render'ı schedule et - performans için"""
        if not self._render_scheduled:
            self._render_scheduled = True
            self.after(16, self._do_render)  # ~60 FPS

    def _do_render(self):
        """Gerçek render işlemi"""
        self._render_scheduled = False
        self.render_canvas()

    def clear_panel(self):
        self.temp_points = []
        self.selected_algebra_func = None
        self.selected_point = None
        self.selected_shape = None
        self.algebra_objects.clear()
        for widget in self.panelbar.winfo_children():
            widget.destroy()

    def panel_title(self, text):
        tk.Label(self.panelbar, text=text, fg=THEME["text"], bg=THEME["panel_bg"], font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=24, pady=(24, 10))

    def panel_text(self, text):
        tk.Label(self.panelbar, text=text, fg=THEME["subtext"], bg=THEME["panel_bg"], font=("Segoe UI", 11), justify="left", wraplength=350).pack(anchor="w", padx=24, pady=6)

    def to_screen(self, mx, my):
        sx = self.content.winfo_width()/2 + (mx * self.scale) + self.offset_x
        sy = self.content.winfo_height()/2 - (my * self.scale) + self.offset_y
        return sx, sy

    def to_math(self, sx, sy):
        mx = (sx - self.content.winfo_width()/2 - self.offset_x) / self.scale
        my = (self.content.winfo_height()/2 + self.offset_y - sy) / self.scale
        return mx, my

    def render_canvas(self):
        """Optimize edilmiş render"""
        self.content.delete("all")
        w, h = self.content.winfo_width(), self.content.winfo_height()
        
        if w < 10 or h < 10:  # Pencere çok küçükse render etme
            return
            
        cx, cy = w/2 + self.offset_x, h/2 + self.offset_y
        
        # Arka plan - tek renk (gradyan yerine)
        self.content.create_rectangle(0, 0, w, h, fill="#1e1e1e", outline="")

        # Grid - sadece görünür alanda
        if self.show_grid:
            self._draw_grid(w, h)

        # Eksenler
        self.content.create_line(0, cy, w, cy, fill="#ffffff", width=2) 
        self.content.create_line(cx, 0, cx, h, fill="#ffffff", width=2)
        
        # Oklar
        arrow_size = 10
        self.content.create_polygon(w, cy, w-arrow_size, cy-arrow_size/2, w-arrow_size, cy+arrow_size/2, fill="#ffffff")
        self.content.create_polygon(cx, 0, cx-arrow_size/2, arrow_size, cx+arrow_size/2, arrow_size, fill="#ffffff")
        
        # Etiketler
        self.content.create_text(w-20, cy-15, text="X", fill="#ffffff", font=("Segoe UI", 12, "bold"))
        self.content.create_text(cx+15, 15, text="Y", fill="#ffffff", font=("Segoe UI", 12, "bold"))
        self.content.create_text(cx+15, cy+15, text="O", fill="#ffffff", font=("Segoe UI", 10, "bold"))

        # Batch drawing için gruplama
        shapes_group = []
        points_group = []
        
        # Fonksiyonlar
        for func in self.algebra_functions:
            if func.visible:
                self._draw_function_optimized(func)

        # Şekiller
        for s in self.shapes:
            color = self.colors[id(s) % len(self.colors)]
            width = 5 if s == self.selected_shape else 3
            self._draw_shape_optimized(s, color, width)

        # Noktalar
        for p in self.points:
            self._draw_point_optimized(p)

    def _draw_grid(self, w, h):
        """Optimize grid çizimi"""
        grid_size = max(self.scale, 20)  # Çok küçük grid'leri engelle
        
        # Görünür grid aralığını hesapla
        x_start = self.offset_x % grid_size
        if x_start < 0:
            x_start += grid_size
            
        y_start = self.offset_y % grid_size
        if y_start < 0:
            y_start += grid_size
        
        # Dikey çizgiler - batch
        x_lines = []
        for x in range(int(x_start), w, int(grid_size)):
            x_lines.extend([x, 0, x, h])
        if x_lines:
            self.content.create_line(x_lines, fill="#2a2a2a", width=1)
        
        # Yatay çizgiler - batch
        y_lines = []
        for y in range(int(y_start), h, int(grid_size)):
            y_lines.extend([0, y, w, y])
        if y_lines:
            self.content.create_line(y_lines, fill="#2a2a2a", width=1)

    def _draw_function_optimized(self, func):
        """Optimize fonksiyon çizimi"""
        # Cache kontrolü
        if (func._cached_points is not None and 
            func._cache_scale == self.scale and 
            func._cache_offset == (self.offset_x, self.offset_y)):
            pts = func._cached_points
        else:
            pts = []
            w = self.content.winfo_width()
            step = max(3, int(50 / self.scale))  # Dinamik adım
            
            for sx in range(0, w, step):
                mx, _ = self.to_math(sx, 0)
                try:
                    adjusted_mx = mx - func.mx
                    allowed = {
                        "x": adjusted_mx, 
                        "sin": math.sin, "cos": math.cos, "sqrt": math.sqrt,
                        "tan": math.tan, "abs": abs, "pi": math.pi, "e": math.e,
                        "log": math.log, "exp": math.exp,
                        "asin": math.asin, "acos": math.acos, "atan": math.atan,
                        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
                        "ceil": math.ceil, "floor": math.floor
                    }
                    my = eval(func.expression.replace("^", "**"), {"__builtins__": None}, allowed)
                    my += func.my
                    screen_x, screen_y = self.to_screen(adjusted_mx + func.mx, my)
                    pts.append((screen_x, screen_y))
                except: 
                    continue
            
            # Cache'le
            func._cached_points = pts
            func._cache_scale = self.scale
            func._cache_offset = (self.offset_x, self.offset_y)
        
        if len(pts) > 1:
            func_color = self.colors[id(func) % len(self.colors)]
            if func == self.selected_algebra_func:
                func_color = "#FFD700"
            
            # Tek create_line ile çiz (gölge yok - performans için)
            flat_pts = [coord for pt in pts for coord in pt]
            self.content.create_line(flat_pts, fill=func_color, width=func.line_width)
            
        # Referans noktası
        if func == self.selected_algebra_func:
            ref_sx, ref_sy = self.to_screen(func.mx, func.my)
            self.content.create_oval(ref_sx-10, ref_sy-10, ref_sx+10, ref_sy+10, 
                                   outline="#FFD700", width=3)
            self.content.create_text(ref_sx+18, ref_sy-18, text="🎯", 
                                   fill="#FFD700", font=("Segoe UI", 12))

    def _draw_shape_optimized(self, s, color, width):
        """Optimize şekil çizimi"""
        if s['type'] == 'line':
            p1s = self.to_screen(s['p1']['mx'], s['p1']['my'])
            p2s = self.to_screen(s['p2']['mx'], s['p2']['my'])
            self.content.create_line(p1s, p2s, fill=color, width=width)
            # Uç noktaları
            self.content.create_oval(p1s[0]-4, p1s[1]-4, p1s[0]+4, p1s[1]+4, 
                                   fill=color, outline="white", width=2)
            self.content.create_oval(p2s[0]-4, p2s[1]-4, p2s[0]+4, p2s[1]+4, 
                                   fill=color, outline="white", width=2)
            
        elif s['type'] == 'circle':
            p1s = self.to_screen(s['p1']['mx'], s['p1']['my'])
            p2s = self.to_screen(s['p2']['mx'], s['p2']['my'])
            r = math.hypot(p1s[0]-p2s[0], p1s[1]-p2s[1])
            if r > 0:
                self.content.create_oval(p1s[0]-r, p1s[1]-r, p1s[0]+r, p1s[1]+r, 
                                       outline=color, width=width)
            self.content.create_oval(p1s[0]-4, p1s[1]-4, p1s[0]+4, p1s[1]+4, 
                                   fill=color, outline="white", width=2)
            
        elif s['type'] == 'triangle':
            pts = [self.to_screen(s['p1']['mx'], s['p1']['my']), 
                   self.to_screen(s['p2']['mx'], s['p2']['my']), 
                   self.to_screen(s['p3']['mx'], s['p3']['my'])]
            # Sadece kenarları çiz (dolgu yok - performans)
            self.content.create_polygon(pts, outline=color, fill="", width=width)
            # Köşe noktaları
            for px, py in pts:
                self.content.create_oval(px-5, py-5, px+5, py+5, 
                                       fill=color, outline="white", width=2)

    def _draw_point_optimized(self, p):
        """Optimize nokta çizimi"""
        sx, sy = self.to_screen(p['mx'], p['my'])
        color = self.colors[id(p) % len(self.colors)]
        
        if p == self.selected_point or p.get('selected'):
            size = 8
            color = "#FFD700"
            self.content.create_oval(sx-size-2, sy-size-2, sx+size+2, sy+size+2, 
                                   outline="#FFD700", width=2)
        
        # Ana nokta
        self.content.create_oval(sx-6, sy-6, sx+6, sy+6, fill=color, outline="white", width=2)
        
        # Etiket
        if self.show_coordinates:
            text = f"{p['name']}({p['mx']:.1f}, {p['my']:.1f})"
        else:
            text = p['name']
        self.content.create_text(sx+15, sy-15, text=text, 
                               fill="#ffffff", font=("Segoe UI", 9, "bold"), anchor="w")

    def invalidate_function_cache(self):
        """Fonksiyon cache'lerini temizle"""
        for func in self.algebra_functions:
            func._cached_points = None
            func._cache_scale = None
            func._cache_offset = None

    def find_nearest_algebra_ref(self, sx, sy, radius=20):
        for func in self.algebra_functions:
            psx, psy = self.to_screen(func.mx, func.my)
            if math.hypot(sx - psx, sy - psy) < radius:
                return func
        return None

    def find_nearest_point(self, sx, sy, radius=15):
        for p in self.points:
            psx, psy = self.to_screen(p['mx'], p['my'])
            if math.hypot(sx - psx, sy - psy) < radius: 
                return p
        return None
    
    def find_nearest_shape(self, sx, sy, radius=20):
        for s in self.shapes:
            if s['type'] == 'line':
                p1s = self.to_screen(s['p1']['mx'], s['p1']['my'])
                p2s = self.to_screen(s['p2']['mx'], s['p2']['my'])
                dist = self._point_to_line_distance(sx, sy, p1s[0], p1s[1], p2s[0], p2s[1])
                if dist < radius:
                    return s
            elif s['type'] == 'circle':
                p1s = self.to_screen(s['p1']['mx'], s['p1']['my'])
                p2s = self.to_screen(s['p2']['mx'], s['p2']['my'])
                r = math.hypot(p1s[0]-p2s[0], p1s[1]-p2s[1])
                dist = abs(math.hypot(sx-p1s[0], sy-p1s[1]) - r)
                if dist < radius:
                    return s
            elif s['type'] == 'triangle':
                cx = (s['p1']['mx'] + s['p2']['mx'] + s['p3']['mx']) / 3
                cy = (s['p1']['my'] + s['p2']['my'] + s['p3']['my']) / 3
                csx, csy = self.to_screen(cx, cy)
                if math.hypot(sx-csx, sy-csy) < radius * 2:
                    return s
        return None
    
    def _point_to_line_distance(self, px, py, x1, y1, x2, y2):
        return abs((y2-y1)*px - (x2-x1)*py + x2*y1 - y2*x1) / math.hypot(y2-y1, x2-x1)

    def delete_selected(self):
        if self.selected_point:
            self.points.remove(self.selected_point)
            self.selected_point = None
        elif self.selected_shape:
            self.shapes.remove(self.selected_shape)
            self.selected_shape = None
        elif self.selected_algebra_func:
            self.algebra_functions.remove(self.selected_algebra_func)
            self.selected_algebra_func = None
        self.invalidate_function_cache()
        self.schedule_render()
        if self.current_panel == 'algebra':
            self.algebra_panel()

    def deselect_all(self):
        self.selected_point = None
        self.selected_shape = None
        self.selected_algebra_func = None
        for p in self.points:
            p['selected'] = False
        self.schedule_render()

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self.schedule_render()

    def toggle_coordinates(self):
        self.show_coordinates = not self.show_coordinates
        self.schedule_render()

    def on_canvas_click(self, event):
        self.last_mouse_x, self.last_mouse_y = event.x, event.y
        mx, my = self.to_math(event.x, event.y)
        
        if self.tool_mode == "move":
            algebra_func = self.find_nearest_algebra_ref(event.x, event.y)
            if algebra_func:
                self.selected_algebra_func = algebra_func
                self.selected_point = None
                self.selected_shape = None
                self.drag_target = 'algebra_func'
                self.is_dragging = True
                self.schedule_render()
                return
            
            clicked_shape = self.find_nearest_shape(event.x, event.y)
            if clicked_shape:
                self.selected_shape = clicked_shape
                self.selected_point = None
                self.selected_algebra_func = None
                for p in self.points:
                    p['selected'] = False
                for key in ['p1', 'p2', 'p3']:
                    if key in clicked_shape:
                        clicked_shape[key]['selected'] = True
                self.drag_target = 'shape'
                self.is_dragging = True
                self.schedule_render()
                return
            
            clicked_p = self.find_nearest_point(event.x, event.y)
            if clicked_p:
                self.selected_point = clicked_p
                self.selected_shape = None
                self.selected_algebra_func = None
                self.drag_target = 'point'
            else:
                self.drag_target = 'canvas'
                self.selected_point = None
                self.selected_shape = None
                self.selected_algebra_func = None
                for p in self.points:
                    p['selected'] = False
            self.is_dragging = True
        
        elif self.tool_mode == "point":
            if not self.find_nearest_point(event.x, event.y):
                name = string.ascii_uppercase[self.point_counter % 26]
                if self.point_counter >= 26:
                    name = f"P{self.point_counter - 25}"
                self.points.append({'name': name, 'mx': mx, 'my': my, 'selected': False})
                self.point_counter += 1
        
        elif self.tool_mode in ["line", "circle", "triangle"]:
            p = self.find_nearest_point(event.x, event.y)
            if not p:
                name = string.ascii_uppercase[self.point_counter % 26]
                if self.point_counter >= 26:
                    name = f"P{self.point_counter - 25}"
                p = {'name': name, 'mx': mx, 'my': my, 'selected': False}
                self.points.append(p)
                self.point_counter += 1
            
            self.temp_points.append(p)
            
            if self.tool_mode == "line" and len(self.temp_points) == 2:
                self.shapes.append({'type': 'line', 'p1': self.temp_points[0], 'p2': self.temp_points[1]})
                self.temp_points = []
            elif self.tool_mode == "circle" and len(self.temp_points) == 2:
                self.shapes.append({'type': 'circle', 'p1': self.temp_points[0], 'p2': self.temp_points[1]})
                self.temp_points = []
            elif self.tool_mode == "triangle" and len(self.temp_points) == 3:
                self.shapes.append({'type': 'triangle', 'p1': self.temp_points[0], 'p2': self.temp_points[1], 'p3': self.temp_points[2]})
                self.temp_points = []

        self.schedule_render()
        if self.current_panel == 'algebra':
            self.algebra_panel()

    def on_canvas_drag(self, event):
        if not self.is_dragging:
            return
            
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        
        if self.drag_target == 'algebra_func' and self.selected_algebra_func:
            dmx = dx / self.scale
            dmy = -dy / self.scale
            self.selected_algebra_func.mx += dmx
            self.selected_algebra_func.my += dmy
            self.invalidate_function_cache()
            
        elif self.drag_target == 'point' and self.selected_point:
            mx, my = self.to_math(event.x, event.y)
            self.selected_point['mx'], self.selected_point['my'] = mx, my
            
        elif self.drag_target == 'shape' and self.selected_shape:
            dmx = dx / self.scale
            dmy = -dy / self.scale
            for key in ['p1', 'p2', 'p3']:
                if key in self.selected_shape:
                    self.selected_shape[key]['mx'] += dmx
                    self.selected_shape[key]['my'] += dmy
            
        elif self.drag_target == 'canvas':
            self.offset_x += dx
            self.offset_y += dy
            self.invalidate_function_cache()
            
        self.last_mouse_x, self.last_mouse_y = event.x, event.y
        self.schedule_render()

    def on_canvas_release(self, event):
        self.is_dragging = False
        self.drag_target = None
        if self.current_panel == 'algebra':
            self.algebra_panel()
        self.schedule_render()

    def on_canvas_zoom(self, event):
        mx, my = self.to_math(event.x, event.y)
        f = 1.1 if event.delta > 0 else 0.9
        self.scale *= f
        new_mx, new_my = self.to_math(event.x, event.y)
        self.offset_x += (new_mx - mx) * self.scale
        self.offset_y -= (new_my - my) * self.scale
        self.invalidate_function_cache()
        self.schedule_render()

    def add_showcase_example(self):
        self.erease_all()
        
        self.points = [
            {'name': 'A', 'mx': 0, 'my': 0, 'selected': False},
            {'name': 'B', 'mx': 4, 'my': 0, 'selected': False},
            {'name': 'C', 'mx': 2, 'my': 3, 'selected': False},
            {'name': 'D', 'mx': -2, 'my': 2, 'selected': False},
            {'name': 'E', 'mx': -3, 'my': -1, 'selected': False},
        ]
        self.point_counter = 5
        
        self.shapes = [
            {'type': 'triangle', 'p1': self.points[0], 'p2': self.points[1], 'p3': self.points[2]},
            {'type': 'circle', 'p1': self.points[3], 'p2': self.points[0]},
            {'type': 'line', 'p1': self.points[2], 'p2': self.points[4]},
        ]
        
        self.algebra_functions = [
            AlgebraFunction("sin(x)", 0, 0),
            AlgebraFunction("cos(x)", 0, -2),
            AlgebraFunction("0.5*x^2 - 2", 0, 1),
        ]
        
        self.invalidate_function_cache()
        self.render_canvas()
        if self.current_panel == 'algebra':
            self.algebra_panel()

    def home_panel(self):
        self.current_panel = 'home'
        self.clear_panel()
        self.panel_title("MethEngine")
        self.panel_text("🎨 Geometrik Çizim Motoru\n\nÖzellikler:\n• 📍 Nokta, çizgi, üçgen, çember\n• 📈 Fonksiyon grafikleri\n• 🎯 Move tool ile taşıma\n• 🎨 Renkli çizimler\n• ⌨️ Klavye kısayolları\n\nKısayollar:\n• G: Grid göster/gizle\n• C: Koordinatları göster/gizle\n• Delete: Seçili objeyi sil\n• Escape: Seçimi kaldır")
        
        showcase_btn = tk.Button(
            self.panelbar,
            text="🚀 Showcase Örneği Yükle",
            command=self.add_showcase_example,
            bg=THEME["accent"],
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10
        )
        showcase_btn.pack(pady=20)

    def tool_panel(self):
        self.current_panel = 'tools'
        self.clear_panel()
        self.selected_algebra_func = None
        self.selected_point = None
        self.selected_shape = None
        self.panel_title("🛠️ Tools")
        grid = tk.Frame(self.panelbar, bg=THEME["panel_bg"]); grid.pack(padx=12, pady=10)
        
        tools = [
            ("./img/move.png", "Move", lambda: self.set_tool("move")),
            ("./img/point.png", "Point", lambda: self.set_tool("point")),
            ("./img/line.png", "Line", lambda: self.set_tool("line")),
            ("./img/circle.png", "Circle", lambda: self.set_tool("circle")),
            ("./img/triangle.png", "Triangle", lambda: self.set_tool("triangle")),
            ("./img/erease.png", "Clear All", self.erease_all)
        ]
        for i, (icon, name, cmd) in enumerate(tools):
            CustomBtn.add_tool_button(grid, icon, name, cmd, i // 3, i % 3)

    def set_tool(self, mode):
        self.tool_mode = mode
        self.temp_points = []
        self.selected_point = None
        self.selected_shape = None
        for p in self.points:
            p['selected'] = False
        self.schedule_render()

    def erease_all(self):
        self.points = []
        self.shapes = []
        self.algebra_functions = []
        self.point_counter = 0
        self.selected_algebra_func = None
        self.selected_point = None
        self.selected_shape = None
        self.invalidate_function_cache()
        self.render_canvas()
        if self.current_panel == 'algebra':
            self.algebra_panel()

    def algebra_panel(self):
        self.current_panel = 'algebra'
        self.clear_panel()
        self.panel_title("📐 Algebra")
        
        CustomBtn.add_square_button(
            self.panelbar, 
            "./img/plus.png", 
            "New Function", 
            self.add_algebra_entry
        ).pack(pady=10, padx=24)
        
        self.algebra_canvas = tk.Canvas(
            self.panelbar, 
            bg=THEME["panel_bg"], 
            highlightthickness=0
        )
        self.algebra_container = tk.Frame(self.algebra_canvas, bg=THEME["panel_bg"])
        
        scrollbar = tk.Scrollbar(
            self.panelbar, 
            orient="vertical", 
            command=self.algebra_canvas.yview
        )
        self.algebra_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.algebra_canvas.pack(side="left", fill="both", expand=True, padx=(24, 0))
        self.algebra_canvas.create_window(
            (0, 0), 
            window=self.algebra_container, 
            anchor="nw", 
            width=340
        )
        
        self.algebra_container.bind(
            "<Configure>",
            lambda e: self.algebra_canvas.configure(
                scrollregion=self.algebra_canvas.bbox("all")
            )
        )
        
        if self.points:
            self._create_section_header("📌 Points")
            for p in self.points:
                self._create_point_entry(p)
        
        if self.shapes:
            self._create_section_header("📐 Shapes")
            for i, s in enumerate(self.shapes):
                self._create_shape_entry(s, i)
        
        if self.algebra_functions:
            self._create_section_header("📈 Functions")
            for func in self.algebra_functions:
                self._create_algebra_ui_entry(func)
        
        if not self.points and not self.shapes and not self.algebra_functions:
            self.panel_text("Henüz bir obje yok.\nTools menüsünden nokta, çizgi veya şekil ekleyin.")

    def _create_section_header(self, text):
        header_frame = tk.Frame(self.algebra_container, bg=THEME["accent"], height=2)
        header_frame.pack(fill="x", pady=(10, 5), padx=5)
        
        tk.Label(
            header_frame,
            text=text,
            fg=THEME["text"],
            bg=THEME["panel_bg"],
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

    def _create_point_entry(self, point):
        frame = tk.Frame(
            self.algebra_container, 
            bg=THEME["panel_bg"],
            highlightbackground=THEME["border"],
            highlightthickness=1
        )
        frame.pack(fill="x", pady=2, padx=5)
        
        info_frame = tk.Frame(frame, bg=THEME["panel_bg"])
        info_frame.pack(side="left", fill="x", expand=True, padx=8, pady=5)
        
        name_label = tk.Label(
            info_frame,
            text=point['name'],
            fg=THEME["accent"],
            bg=THEME["panel_bg"],
            font=("Segoe UI", 11, "bold"),
            cursor="hand2"
        )
        name_label.pack(anchor="w")
        
        coord_text = f"({point['mx']:.2f}, {point['my']:.2f})"
        coord_label = tk.Label(
            info_frame,
            text=coord_text,
            fg=THEME["subtext"],
            bg=THEME["panel_bg"],
            font=("Segoe UI", 9)
        )
        coord_label.pack(anchor="w")
        
        btn_frame = tk.Frame(frame, bg=THEME["panel_bg"])
        btn_frame.pack(side="right", padx=5, pady=5)
        
        select_btn = tk.Button(
            btn_frame,
            text="📍",
            command=lambda p=point: self.select_point_from_algebra(p),
            bg=THEME["button_bg"],
            fg=THEME["text"],
            font=("Segoe UI", 8),
            relief="flat",
            cursor="hand2",
            width=3
        )
        select_btn.pack(side="left", padx=1)
        
        delete_btn = tk.Button(
            btn_frame,
            text="✕",
            command=lambda p=point, f=frame: self.delete_point_from_algebra(p, f),
            bg=THEME["panel_bg"],
            fg="red",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            width=3
        )
        delete_btn.pack(side="left", padx=1)
        
        for widget in [frame, info_frame, name_label, coord_label]:
            widget.bind("<Button-1>", lambda e, p=point: self.select_point_from_algebra(p))

    def _create_shape_entry(self, shape, index):
        frame = tk.Frame(
            self.algebra_container, 
            bg=THEME["panel_bg"],
            highlightbackground=THEME["border"],
            highlightthickness=1
        )
        frame.pack(fill="x", pady=2, padx=5)
        
        info_frame = tk.Frame(frame, bg=THEME["panel_bg"])
        info_frame.pack(side="left", fill="x", expand=True, padx=8, pady=5)
        
        if shape['type'] == 'line':
            type_text = "Line"
            points_text = f"{shape['p1']['name']}{shape['p2']['name']}"
            detail_text = f"({shape['p1']['name']}({shape['p1']['mx']:.2f},{shape['p1']['my']:.2f}), {shape['p2']['name']}({shape['p2']['mx']:.2f},{shape['p2']['my']:.2f}))"
        elif shape['type'] == 'circle':
            type_text = "Circle"
            points_text = f"{shape['p1']['name']}{shape['p2']['name']}"
            detail_text = f"Center: {shape['p1']['name']}({shape['p1']['mx']:.2f},{shape['p1']['my']:.2f})"
        elif shape['type'] == 'triangle':
            type_text = "Triangle"
            points_text = f"{shape['p1']['name']}{shape['p2']['name']}{shape['p3']['name']}"
            detail_text = f"({shape['p1']['name']}({shape['p1']['mx']:.2f},{shape['p1']['my']:.2f}), {shape['p2']['name']}({shape['p2']['mx']:.2f},{shape['p2']['my']:.2f}), {shape['p3']['name']}({shape['p3']['mx']:.2f},{shape['p3']['my']:.2f}))"
        
        name_label = tk.Label(
            info_frame,
            text=f"{type_text} {points_text}",
            fg=THEME["accent"],
            bg=THEME["panel_bg"],
            font=("Segoe UI", 10, "bold"),
            cursor="hand2"
        )
        name_label.pack(anchor="w")
        
        detail_label = tk.Label(
            info_frame,
            text=detail_text,
            fg=THEME["subtext"],
            bg=THEME["panel_bg"],
            font=("Segoe UI", 8),
            wraplength=280,
            justify="left"
        )
        detail_label.pack(anchor="w")
        
        btn_frame = tk.Frame(frame, bg=THEME["panel_bg"])
        btn_frame.pack(side="right", padx=5, pady=5)
        
        select_btn = tk.Button(
            btn_frame,
            text="👁",
            command=lambda s=shape: self.select_shape_from_algebra(s),
            bg=THEME["button_bg"],
            fg=THEME["text"],
            font=("Segoe UI", 8),
            relief="flat",
            cursor="hand2",
            width=3
        )
        select_btn.pack(side="left", padx=1)
        
        delete_btn = tk.Button(
            btn_frame,
            text="✕",
            command=lambda s=shape, f=frame: self.delete_shape_from_algebra(s, f),
            bg=THEME["panel_bg"],
            fg="red",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            width=3
        )
        delete_btn.pack(side="left", padx=1)
        
        for widget in [frame, info_frame, name_label, detail_label]:
            widget.bind("<Button-1>", lambda e, s=shape: self.select_shape_from_algebra(s))

    def _create_algebra_ui_entry(self, func):
        entry_frame = tk.Frame(
            self.algebra_container, 
            bg=THEME["panel_bg"],
            highlightbackground=THEME["border"],
            highlightthickness=1
        )
        entry_frame.pack(fill="x", pady=2, padx=5)
        
        top_row = tk.Frame(entry_frame, bg=THEME["panel_bg"])
        top_row.pack(fill="x", padx=5, pady=(5, 2))
        
        tk.Label(
            top_row, 
            text="f(x) =", 
            fg=THEME["text"], 
            bg=THEME["panel_bg"],
            font=("Segoe UI", 10)
        ).pack(side="left")
        
        v = tk.StringVar(value=func.expression)
        e = tk.Entry(
            top_row, 
            textvariable=v, 
            font=("Segoe UI", 10),
            width=20,
            bg="white",
            relief="solid",
            borderwidth=1
        )
        e.pack(side="left", fill="x", expand=True, padx=(5, 5))
        e.bind("<Return>", lambda ev, f=func, var=v: self.update_function(f, var.get()))
        
        del_btn = tk.Button(
            top_row,
            text="✕",
            command=lambda f=func, frame=entry_frame: self.delete_function(f, frame),
            bg=THEME["panel_bg"],
            fg="red",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2"
        )
        del_btn.pack(side="right")
        
        bottom_row = tk.Frame(entry_frame, bg=THEME["panel_bg"])
        bottom_row.pack(fill="x", padx=5, pady=(2, 5))
        
        ref_text = f"Ref: ({func.mx:.2f}, {func.my:.2f})"
        ref_label = tk.Label(
            bottom_row,
            text=ref_text,
            fg=THEME["subtext"],
            bg=THEME["panel_bg"],
            font=("Segoe UI", 8)
        )
        ref_label.pack(side="left")
        
        reset_btn = tk.Button(
            bottom_row,
            text="Reset Ref",
            command=lambda f=func, lbl=ref_label: self.reset_reference(f, lbl),
            bg=THEME["button_bg"],
            fg=THEME["text"],
            font=("Segoe UI", 8),
            relief="flat",
            cursor="hand2"
        )
        reset_btn.pack(side="right", padx=2)
        
        vis_var = tk.BooleanVar(value=func.visible)
        vis_btn = tk.Checkbutton(
            bottom_row,
            text="Show",
            variable=vis_var,
            command=lambda f=func, v=vis_var: self.toggle_visibility(f, v.get()),
            bg=THEME["panel_bg"],
            fg=THEME["text"],
            font=("Segoe UI", 8),
            selectcolor=THEME["panel_bg"],
            relief="flat"
        )
        vis_btn.pack(side="right", padx=5)
        
        func._ui_widgets = {
            'frame': entry_frame,
            'ref_label': ref_label,
            'entry_var': v
        }

    def select_point_from_algebra(self, point):
        self.selected_point = point
        self.selected_shape = None
        for p in self.points:
            p['selected'] = (p == point)
        self.schedule_render()

    def select_shape_from_algebra(self, shape):
        self.selected_shape = shape
        self.selected_point = None
        self.selected_algebra_func = None
        for p in self.points:
            p['selected'] = False
        for key in ['p1', 'p2', 'p3']:
            if key in shape:
                shape[key]['selected'] = True
        self.schedule_render()

    def delete_point_from_algebra(self, point, frame):
        if point in self.points:
            shapes_to_remove = []
            for shape in self.shapes:
                for key in ['p1', 'p2', 'p3']:
                    if key in shape and shape[key] == point:
                        shapes_to_remove.append(shape)
                        break
            
            for shape in shapes_to_remove:
                if shape in self.shapes:
                    self.shapes.remove(shape)
            
            self.points.remove(point)
            
        if self.selected_point == point:
            self.selected_point = None
        if self.selected_shape in shapes_to_remove:
            self.selected_shape = None
            
        frame.destroy()
        self.algebra_panel()
        self.invalidate_function_cache()
        self.schedule_render()

    def delete_shape_from_algebra(self, shape, frame):
        if shape in self.shapes:
            self.shapes.remove(shape)
        if self.selected_shape == shape:
            self.selected_shape = None
        frame.destroy()
        self.algebra_panel()
        self.schedule_render()

    def update_function(self, func, expression):
        func.expression = expression.strip()
        self.invalidate_function_cache()
        self.schedule_render()

    def delete_function(self, func, frame):
        if func in self.algebra_functions:
            self.algebra_functions.remove(func)
        frame.destroy()
        if self.selected_algebra_func == func:
            self.selected_algebra_func = None
        self.invalidate_function_cache()
        self.schedule_render()

    def reset_reference(self, func, ref_label):
        func.mx = 0
        func.my = 0
        ref_label.config(text=f"Ref: (0.00, 0.00)")
        self.invalidate_function_cache()
        self.schedule_render()

    def toggle_visibility(self, func, visible):
        func.visible = visible
        self.schedule_render()

    def add_algebra_entry(self):
        func = AlgebraFunction("")
        self.algebra_functions.append(func)
        self.algebra_panel()

    def settings_panel(self):
        self.current_panel = 'settings'
        self.clear_panel()
        self.selected_algebra_func = None
        self.selected_point = None
        self.selected_shape = None
        self.panel_title("⚙️ Settings")
        self.panel_text("Ayarlar yakında...")

    def run(self): 
        self.mainloop()

if __name__ == "__main__":
    app = MainWindow()
    app.run()