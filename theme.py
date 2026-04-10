"""
Theme and Style Constants for Restaurant ERP
Dark mode with premium restaurant feel
"""

# ── Color Palette ──────────────────────────────────────────────────────────────
COLORS = {
    # Primary Backgrounds
    "bg_primary":    "#0F1419",
    "bg_secondary":  "#1A1F26",
    "bg_card":       "#242933",
    "bg_hover":      "#2E3542",
    "bg_sidebar":    "#0F1419",

    # Accent Colors - Modern Gold/Orange
    "accent":        "#FF8C42",
    "accent_dark":   "#E67A2C",
    "accent_light":  "#FFB380",

    # Status Colors
    "success":       "#4CAF50",
    "warning":       "#FFA726",
    "danger":        "#EF5350",
    "info":          "#42A5F5",

    # Text Colors
    "text_primary":  "#ECEFF1",
    "text_secondary":"#90A4AE",
    "text_muted":    "#607D8B",

    # Borders & Dividers
    "border":        "#37474F",
    "border_light":  "#2E3542",

    # Sidebar
    "sidebar_active":"#FF8C42",
    "sidebar_hover": "#37474F",

    # Category Colors - More Vibrant
    "cat_1": "#FF6B6B",    # Red
    "cat_2": "#4ECDC4",    # Cyan
    "cat_3": "#45B7D1",    # Blue
    "cat_4": "#FFA07A",    # Orange
    "cat_5": "#98D8C8",    # Green
    "cat_6": "#F7DC6F",    # Yellow
    "cat_7": "#BB8FCE",    # Purple
    "cat_8": "#F8B195",    # Peach
}

# ── Fonts ──────────────────────────────────────────────────────────────────────
FONTS = {
    "title_xl":  ("Cairo", 28, "bold"),
    "title_lg":  ("Cairo", 22, "bold"),
    "title_md":  ("Cairo", 18, "bold"),
    "title_sm":  ("Cairo", 14, "bold"),
    "body_lg":   ("Cairo", 14),
    "body_md":   ("Cairo", 12),
    "body_sm":   ("Cairo", 10),
    "mono":      ("Consolas", 12),
}

# ── Dimensions ────────────────────────────────────────────────────────────────
SIDEBAR_WIDTH = 220
HEADER_HEIGHT = 60

# ── Role Permissions ──────────────────────────────────────────────────────────
ROLE_PERMISSIONS = {
    "admin":   ["dashboard", "cashier", "orders", "delivery", "menu", "tables", "inventory", "expenses", "reports", "settings"],
    "manager": ["dashboard", "cashier", "orders", "delivery", "menu", "tables", "inventory", "expenses", "reports"],
    "cashier": ["dashboard", "cashier", "orders", "delivery", "tables"],
}
