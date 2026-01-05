import csv
from pathlib import Path

def load_theme(csv_path=None):
    """Load theme from CSV file"""
    # Try to find theme.csv in common locations
    if csv_path is None:
        possible_paths = [
            Path("theme.csv"),  # Current directory
            Path(__file__).parent / "theme.csv",  # Same dir as this module
            Path(__file__).parent.parent / "theme.csv",  # Parent dir
        ]
        
        for path in possible_paths:
            if path.exists():
                csv_path = path
                break
    
    theme = {}
    
    if csv_path and Path(csv_path).exists():
        try:
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    theme[row['contents'].strip()] = row['color'].strip()
            print(f"✓ Theme loaded from {csv_path}")
        except Exception as e:
            print(f"Error reading theme file: {e}")
    
    # Use defaults if not loaded
    if not theme:
        print("Using default theme")
        theme = {
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
    
    return theme

# Global theme instance
THEME = load_theme()