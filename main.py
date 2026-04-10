"""
Restaurant ERP System - Main Entry Point
A complete POS & management system for restaurants
Author: Antigravity AI
"""
import sys
import os

# ── Path fix for PyInstaller ───────────────────────────────────────────────────
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
    os.chdir(os.path.dirname(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, BASE_DIR)

# ── Imports ────────────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import messagebox
import database as db
from theme import COLORS, FONTS, SIDEBAR_WIDTH, HEADER_HEIGHT, ROLE_PERMISSIONS
from widgets import SidebarButton, Toast

# Screen imports
from screens.login_screen    import LoginScreen
from screens.dashboard_screen import DashboardScreen
from screens.cashier_screen  import CashierScreen
from screens.orders_screen   import OrdersScreen
from screens.delivery_screen import DeliveryScreen
from screens.menu_screen     import MenuScreen
from screens.tables_screen   import TablesScreen
from screens.inventory_screen import InventoryScreen
from screens.reports_screen  import ReportsScreen
from screens.settings_screen import SettingsScreen


# ══════════════════════════════════════════════════════════════════════════════
class RestaurantERP(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Initialize DB first
        db.init_database()

        self.current_user = None
        self.current_shift_id = None

        # Window setup
        self.title("مطعم الأصالة — نظام ERP")
        self.geometry("1280x780")
        self.minsize(1100, 680)
        self.configure(bg=COLORS["bg_primary"])
        self.resizable(True, True)

        # Set RTL layout direction (Arabic)
        try:
            self.tk.call("tk", "scaling", 1.1)
        except Exception:
            pass

        # Icon (if available)
        ico = os.path.join(BASE_DIR, "icon.ico")
        if os.path.exists(ico):
            self.iconbitmap(ico)

        # Center window
        self._center_window()

        # Show login first
        self._show_login()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width() or 1280
        h = self.winfo_height() or 780
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Login ──────────────────────────────────────────────────────────────────
    def _show_login(self):
        for w in self.winfo_children():
            w.destroy()
        self._login_frame = LoginScreen(self, on_login=self._on_login)
        self._login_frame.pack(fill="both", expand=True)

    def _on_login(self, user: dict):
        self.current_user = user
        self._build_main_ui()
        self._open_shift_dialog()

    # ── Shift ──────────────────────────────────────────────────────────────────
    def _open_shift_dialog(self):
        """Ask for opening cash when starting a shift."""
        win = tk.Toplevel(self)
        win.title("بدء وردية")
        win.config(bg=COLORS["bg_primary"])
        win.geometry("380x280")
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        # Center
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 380) // 2
        y = self.winfo_y() + (self.winfo_height() - 280) // 2
        win.geometry(f"+{x}+{y}")

        tk.Label(win, text="🏪 بدء وردية جديدة",
                 fg=COLORS["accent"], bg=COLORS["bg_primary"],
                 font=FONTS["title_md"]).pack(pady=20)

        tk.Label(win, text=f"مرحباً، {self.current_user['full_name']}",
                 fg=COLORS["text_secondary"], bg=COLORS["bg_primary"],
                 font=FONTS["body_md"]).pack()

        form = tk.Frame(win, bg=COLORS["bg_card"], padx=24, pady=20)
        form.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(form, text="نقدية بداية الوردية (ج.م):",
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                 font=FONTS["body_sm"]).pack(anchor="w")

        cash_var = tk.StringVar(value="0")
        tk.Entry(form, textvariable=cash_var,
                 bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                 insertbackground=COLORS["text_primary"],
                 font=FONTS["title_md"], bd=0, relief="flat",
                 justify="center").pack(fill="x", ipady=10, pady=(4, 16))

        def start():
            try:
                cash = float(cash_var.get() or 0)
                self.current_shift_id = db.open_shift(self.current_user["id"], cash)
                win.destroy()
                self.show_screen("dashboard")
                Toast(self, f"تم فتح الوردية بنجاح 🏪", "success")
            except ValueError:
                Toast(win, "أدخل قيمة رقمية", "error")

        def skip():
            win.destroy()
            self.show_screen("dashboard")

        tk.Button(form, text="✅ بدء الوردية",
                  bg=COLORS["success"], fg="white",
                  font=FONTS["title_sm"], bd=0, pady=10, relief="flat",
                  cursor="hand2", command=start).pack(fill="x")

        tk.Button(form, text="تخطي",
                  bg=COLORS["bg_hover"], fg=COLORS["text_secondary"],
                  font=FONTS["body_sm"], bd=0, pady=6, relief="flat",
                  cursor="hand2", command=skip).pack(fill="x", pady=(6, 0))

    # ── Main UI ────────────────────────────────────────────────────────────────
    def _build_main_ui(self):
        for w in self.winfo_children():
            w.destroy()

        # Root layout: sidebar | main area
        self.main_frame = tk.Frame(self, bg=COLORS["bg_primary"])
        self.main_frame.pack(fill="both", expand=True)

        self._build_sidebar()
        self._build_content_area()
        self._build_header()

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self.main_frame, bg=COLORS["bg_sidebar"],
                                width=SIDEBAR_WIDTH)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"], pady=20)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="🍽️", fg=COLORS["accent"],
                 bg=COLORS["bg_sidebar"], font=("Cairo", 32)).pack()
        tk.Label(logo_frame, text="مطعم الأصالة",
                 fg=COLORS["accent"], bg=COLORS["bg_sidebar"],
                 font=FONTS["title_sm"]).pack()
        tk.Label(logo_frame, text=f"[{self.current_user['role'].upper()}]",
                 fg=COLORS["text_muted"], bg=COLORS["bg_sidebar"],
                 font=FONTS["body_sm"]).pack()

        tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=12)

        # Nav items
        nav_items = [
            ("dashboard",  "لوحة التحكم", "📊"),
            ("cashier",    "الكاشير",     "💵"),
            ("orders",     "الطلبات",     "📦"),
            ("delivery",   "الدليفري",    "🚗"),
            ("menu",       "المنيو",      "🍽️"),
            ("tables",     "الطاولات",    "🪑"),
            ("inventory",  "المخزون",     "📋"),
            ("reports",    "التقارير",    "📈"),
            ("settings",   "الإعدادات",   "⚙️"),
        ]

        permissions = ROLE_PERMISSIONS.get(self.current_user["role"], [])
        self._nav_buttons = {}

        for key, label, icon in nav_items:
            if key not in permissions:
                continue
            btn = SidebarButton(self.sidebar, text=label, icon=icon,
                                command=lambda k=key: self.show_screen(k))
            btn.pack(fill="x")
            self._nav_buttons[key] = btn

        # Bottom: close shift + logout
        bottom = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"])
        bottom.pack(side="bottom", fill="x", padx=8, pady=12)

        tk.Button(bottom, text="🔐 إغلاق الوردية",
                  bg=COLORS["warning"], fg="black",
                  font=FONTS["body_sm"], bd=0, pady=8, relief="flat",
                  cursor="hand2", command=self._close_shift).pack(fill="x", pady=2)

        tk.Button(bottom, text="🚪 تسجيل الخروج",
                  bg=COLORS["danger"], fg="white",
                  font=FONTS["body_sm"], bd=0, pady=8, relief="flat",
                  cursor="hand2", command=self._logout).pack(fill="x", pady=2)

    def _build_header(self):
        self.header = tk.Frame(self.content_area, bg=COLORS["bg_secondary"],
                               height=HEADER_HEIGHT)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.header_title = tk.Label(self.header, text="",
                                      fg=COLORS["text_primary"],
                                      bg=COLORS["bg_secondary"],
                                      font=FONTS["title_sm"])
        self.header_title.pack(side="right", padx=20, pady=12)

        # Clock
        self.clock_label = tk.Label(self.header, text="",
                                     fg=COLORS["text_secondary"],
                                     bg=COLORS["bg_secondary"],
                                     font=FONTS["body_sm"])
        self.clock_label.pack(side="left", padx=20)
        self._tick()

        # User badge
        tk.Label(self.header,
                 text=f"👤 {self.current_user['full_name']}",
                 fg=COLORS["accent"], bg=COLORS["bg_secondary"],
                 font=FONTS["body_sm"]).pack(side="left", padx=12)

    def _tick(self):
        from datetime import datetime
        self.clock_label.config(text=datetime.now().strftime("🕐 %H:%M:%S   %d/%m/%Y"))
        self.after(1000, self._tick)

    def _build_content_area(self):
        self.content_area = tk.Frame(self.main_frame, bg=COLORS["bg_primary"])
        self.content_area.pack(side="left", fill="both", expand=True)
        self.content_area.rowconfigure(1, weight=1)
        self.content_area.columnconfigure(0, weight=1)

        # Screen container (below header)
        self.screen_container = tk.Frame(self.content_area, bg=COLORS["bg_primary"])
        self.screen_container.pack(fill="both", expand=True)

        # Build all allowed screens
        permissions = ROLE_PERMISSIONS.get(self.current_user["role"], [])
        self.screens = {}

        screen_map = {
            "dashboard": (DashboardScreen,  "📊 لوحة التحكم"),
            "cashier":   (CashierScreen,    "💵 الكاشير"),
            "orders":    (OrdersScreen,     "📦 الطلبات"),
            "delivery":  (DeliveryScreen,   "🚗 الدليفري"),
            "menu":      (MenuScreen,       "🍽️ المنيو"),
            "tables":    (TablesScreen,     "🪑 الطاولات"),
            "inventory": (InventoryScreen,  "📋 المخزون"),
            "reports":   (ReportsScreen,    "📈 التقارير"),
            "settings":  (SettingsScreen,   "⚙️ الإعدادات"),
        }

        for key, (cls, title) in screen_map.items():
            if key in permissions:
                frame = cls(self.screen_container, self)
                frame.place(relwidth=1, relheight=1, x=0, y=0)
                frame.place_forget()
                self.screens[key] = (frame, title)

        self._current_screen = None

    def show_screen(self, key: str):
        if key not in self.screens:
            return

        # Hide current
        if self._current_screen and self._current_screen in self.screens:
            self.screens[self._current_screen][0].place_forget()

        # Update sidebar active state
        for k, btn in self._nav_buttons.items():
            btn.set_active(k == key)

        # Show new screen
        frame, title = self.screens[key]
        frame.place(relwidth=1, relheight=1)
        self.header_title.config(text=title)
        self._current_screen = key

        # Call on_show if defined
        if hasattr(frame, "on_show"):
            frame.on_show()

    # ── Shift / Logout ─────────────────────────────────────────────────────────
    def _close_shift(self):
        if not self.current_shift_id:
            Toast(self, "لا توجد وردية مفتوحة", "warning")
            return

        win = tk.Toplevel(self)
        win.title("إغلاق الوردية")
        win.config(bg=COLORS["bg_primary"])
        win.geometry("380x260")
        win.transient(self)
        win.grab_set()

        tk.Label(win, text="🔐 إغلاق الوردية",
                 fg=COLORS["accent"], bg=COLORS["bg_primary"],
                 font=FONTS["title_md"]).pack(pady=16)

        form = tk.Frame(win, bg=COLORS["bg_card"], padx=24, pady=20)
        form.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        tk.Label(form, text="نقدية نهاية الوردية (ج.م):",
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                 font=FONTS["body_sm"]).pack(anchor="w")

        cash_var = tk.StringVar(value="0")
        tk.Entry(form, textvariable=cash_var,
                 bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                 insertbackground=COLORS["text_primary"],
                 font=FONTS["title_md"], bd=0, relief="flat",
                 justify="center").pack(fill="x", ipady=10, pady=(4, 16))

        def close():
            try:
                cash = float(cash_var.get() or 0)
                db.close_shift(self.current_shift_id, cash)
                self.current_shift_id = None
                win.destroy()
                Toast(self, "تم إغلاق الوردية بنجاح ✅", "success")
            except ValueError:
                Toast(win, "أدخل قيمة رقمية", "error")

        tk.Button(form, text="✅ تأكيد الإغلاق",
                  bg=COLORS["warning"], fg="black",
                  font=FONTS["title_sm"], bd=0, pady=10, relief="flat",
                  cursor="hand2", command=close).pack(fill="x")

    def _logout(self):
        if messagebox.askyesno("تأكيد الخروج", "تسجيل الخروج من النظام؟"):
            self.current_user = None
            self.current_shift_id = None
            self._show_login()


# ══════════════════════════════════════════════════════════════════════════════
def main():
    app = RestaurantERP()
    app.mainloop()


if __name__ == "__main__":
    main()
