"""
Dashboard Screen - KPIs and overview
"""
import tkinter as tk
from datetime import datetime
import database as db
from theme import COLORS, FONTS
from widgets import StatCard


class DashboardScreen(tk.Frame):

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=COLORS["bg_primary"], **kwargs)
        self.app = app
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        # Header
        hdr = tk.Frame(self, bg=COLORS["bg_primary"], pady=20, padx=24)
        hdr.grid(row=0, column=0, sticky="ew")
        self.date_label = tk.Label(hdr, text="", fg=COLORS["accent"],
                                    bg=COLORS["bg_primary"], font=FONTS["title_lg"])
        self.date_label.pack(side="left")
        tk.Label(hdr, text="لوحة التحكم", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_primary"], font=FONTS["body_md"]).pack(side="right")

        # KPI Cards row
        kpi_frame = tk.Frame(self, bg=COLORS["bg_primary"], pady=0, padx=16)
        kpi_frame.grid(row=1, column=0, sticky="ew")
        kpi_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.kpi_today_orders = StatCard(kpi_frame, "طلبات اليوم", "—", "📋",
                                          COLORS["info"])
        self.kpi_today_orders.grid(row=0, column=0, sticky="ew", padx=6, pady=8)

        self.kpi_today_rev = StatCard(kpi_frame, "إيرادات اليوم", "—", "💰",
                                       COLORS["success"])
        self.kpi_today_rev.grid(row=0, column=1, sticky="ew", padx=6, pady=8)

        self.kpi_monthly = StatCard(kpi_frame, "إيرادات الشهر", "—", "📅",
                                     COLORS["accent"])
        self.kpi_monthly.grid(row=0, column=2, sticky="ew", padx=6, pady=8)

        self.kpi_tables = StatCard(kpi_frame, "الطاولات المشغولة", "—", "🪑",
                                    COLORS["warning"])
        self.kpi_tables.grid(row=0, column=3, sticky="ew", padx=6, pady=8)

        # Secondary row
        self.kpi_open = StatCard(kpi_frame, "طلبات مفتوحة", "—", "⏳",
                                  COLORS["danger"])
        self.kpi_open.grid(row=1, column=0, sticky="ew", padx=6, pady=4)

        # Middle section: Top items + Recent orders
        mid = tk.Frame(self, bg=COLORS["bg_primary"], padx=16)
        mid.grid(row=2, column=0, sticky="nsew", pady=8)
        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)

        # Top selling items
        top_frame = tk.Frame(mid, bg=COLORS["bg_card"], bd=0,
                              highlightthickness=1, highlightbackground=COLORS["border"],
                              padx=16, pady=12)
        top_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(top_frame, text="🏆 الأكثر مبيعاً اليوم",
                 fg=COLORS["accent"], bg=COLORS["bg_card"],
                 font=FONTS["title_sm"]).pack(anchor="w", pady=(0, 12))

        self.top_items_frame = tk.Frame(top_frame, bg=COLORS["bg_card"])
        self.top_items_frame.pack(fill="both", expand=True)

        # Recent orders
        recent_frame = tk.Frame(mid, bg=COLORS["bg_card"], bd=0,
                                 highlightthickness=1, highlightbackground=COLORS["border"],
                                 padx=16, pady=12)
        recent_frame.grid(row=0, column=1, sticky="nsew")

        hdr_row = tk.Frame(recent_frame, bg=COLORS["bg_card"])
        hdr_row.pack(fill="x", pady=(0, 12))
        tk.Label(hdr_row, text="🕐 آخر الطلبات",
                 fg=COLORS["accent"], bg=COLORS["bg_card"],
                 font=FONTS["title_sm"]).pack(side="left")
        tk.Button(hdr_row, text="تحديث ↺",
                  bg=COLORS["bg_hover"], fg=COLORS["text_secondary"],
                  font=FONTS["body_sm"], bd=0, padx=10, pady=4, relief="flat",
                  cursor="hand2", command=self.refresh).pack(side="right")

        self.recent_frame = tk.Frame(recent_frame, bg=COLORS["bg_card"])
        self.recent_frame.pack(fill="both", expand=True)

        # Hourly chart placeholder
        chart_frame = tk.Frame(self, bg=COLORS["bg_card"], bd=0,
                                highlightthickness=1, highlightbackground=COLORS["border"],
                                padx=16, pady=12, height=160)
        chart_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 16))
        chart_frame.grid_propagate(False)

        tk.Label(chart_frame, text="📊 المبيعات بالساعة (اليوم)",
                 fg=COLORS["accent"], bg=COLORS["bg_card"],
                 font=FONTS["title_sm"]).pack(anchor="w")

        self.chart_canvas = tk.Canvas(chart_frame, bg=COLORS["bg_card"],
                                       height=110, highlightthickness=0)
        self.chart_canvas.pack(fill="x", expand=True, pady=6)

    def refresh(self):
        now = datetime.now()
        self.date_label.config(text=f"يوم {now.strftime('%A')} ─ {now.strftime('%d/%m/%Y')} {now.strftime('%H:%M')}")

        stats = db.get_dashboard_stats(now.strftime("%Y-%m-%d"))

        self.kpi_today_orders.update_value(str(stats["today_orders"]))
        self.kpi_today_rev.update_value(f"{stats['today_revenue']:.2f} ج.م")
        self.kpi_monthly.update_value(f"{stats['monthly_revenue']:.2f} ج.م")
        self.kpi_tables.update_value(f"{stats['occupied_tables']} / {stats['total_tables']}")
        self.kpi_open.update_value(str(stats["open_orders"]))

        # Top items
        for w in self.top_items_frame.winfo_children():
            w.destroy()
        for i, item in enumerate(stats["top_items"]):
            row = tk.Frame(self.top_items_frame, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"{i+1}.", fg=COLORS["accent"],
                     bg=COLORS["bg_card"], font=FONTS["body_sm"], width=3).pack(side="left")
            tk.Label(row, text=item["name"], fg=COLORS["text_primary"],
                     bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(side="left")
            tk.Label(row, text=f"{item['qty']} قطعة", fg=COLORS["text_secondary"],
                     bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(side="right")

        # Recent orders
        orders = db.get_all_orders(limit=8)
        for w in self.recent_frame.winfo_children():
            w.destroy()

        status_colors = {
            "open": COLORS["info"],
            "completed": COLORS["success"],
            "cancelled": COLORS["danger"],
        }
        status_labels = {"open": "مفتوح", "completed": "مكتمل", "cancelled": "ملغي"}

        for o in orders:
            row = tk.Frame(self.recent_frame, bg=COLORS["bg_hover"],
                           bd=0, highlightthickness=0)
            row.pack(fill="x", pady=2, padx=2)
            inner = tk.Frame(row, bg=COLORS["bg_hover"], padx=10, pady=6)
            inner.pack(fill="x")

            tk.Label(inner, text=o.get("order_number", "")[-8:],
                     fg=COLORS["text_secondary"], bg=COLORS["bg_hover"],
                     font=FONTS["body_sm"], width=14, anchor="w").pack(side="left")
            tk.Label(inner, text=o.get("cashier_name", "")[:16],
                     fg=COLORS["text_primary"], bg=COLORS["bg_hover"],
                     font=FONTS["body_sm"], width=14, anchor="w").pack(side="left")
            tk.Label(inner, text=f"{o.get('total', 0):.2f} ج.م",
                     fg=COLORS["accent"], bg=COLORS["bg_hover"],
                     font=FONTS["body_sm"]).pack(side="left", padx=12)

            sc = status_colors.get(o.get("status"), COLORS["text_muted"])
            sl = status_labels.get(o.get("status"), o.get("status"))
            tk.Label(inner, text=sl, fg=sc, bg=COLORS["bg_hover"],
                     font=FONTS["body_sm"]).pack(side="right")

            # Edit button for open orders
            if o.get("status") == "open":
                tk.Button(inner, text="فتح", bg=COLORS["info"], fg="white",
                          font=FONTS["body_sm"], bd=0, padx=8, pady=2, relief="flat",
                          cursor="hand2",
                          command=lambda oid=o["id"]: self._open_order(oid)).pack(side="right", padx=4)

        # Hourly bar chart
        self._draw_chart(stats["hourly_sales"])

        # Auto-refresh every 60 seconds
        self.after(60000, self.refresh)

    def _draw_chart(self, hourly):
        c = self.chart_canvas
        c.delete("all")
        if not hourly:
            c.create_text(c.winfo_width()//2 or 300, 55,
                          text="لا توجد بيانات اليوم", fill=COLORS["text_muted"],
                          font=FONTS["body_sm"])
            return

        c.update_idletasks()
        w, h = c.winfo_width() or 600, c.winfo_height() or 110
        max_cnt = max(r["cnt"] for r in hourly) or 1
        bar_w = min(30, w // max(len(hourly), 1) - 6)
        pad_l, pad_b = 20, 25

        for i, row in enumerate(hourly):
            x = pad_l + i * (bar_w + 6)
            bar_h = int((row["cnt"] / max_cnt) * (h - pad_b - 10))
            y1, y2 = h - pad_b - bar_h, h - pad_b
            c.create_rectangle(x, y1, x + bar_w, y2,
                                fill=COLORS["accent"], outline="", width=0)
            c.create_text(x + bar_w//2, h - pad_b + 10,
                          text=f"{row['hour']}:00", fill=COLORS["text_muted"],
                          font=("Cairo", 7))
            c.create_text(x + bar_w//2, y1 - 6,
                          text=str(row["cnt"]), fill=COLORS["text_secondary"],
                          font=("Cairo", 7))

    def _open_order(self, order_id):
        self.app.screens["cashier"].load_order(order_id)
