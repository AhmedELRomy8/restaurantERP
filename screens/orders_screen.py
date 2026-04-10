"""
Orders Management Screen
"""
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import database as db
from theme import COLORS, FONTS
from widgets import DataTable, Toast


class OrdersScreen(tk.Frame):

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=COLORS["bg_primary"], **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # ── Filter Bar ────────────────────────────────────────────────────────
        filter_bar = tk.Frame(self, bg=COLORS["bg_secondary"], padx=16, pady=12)
        filter_bar.grid(row=0, column=0, sticky="ew")

        tk.Label(filter_bar, text="📦 إدارة الطلبات", fg=COLORS["accent"],
                 bg=COLORS["bg_secondary"], font=FONTS["title_md"]).pack(side="left")

        # Status filter
        self.status_var = tk.StringVar(value="all")
        for val, lbl in [("all", "الكل"), ("open", "مفتوح"), ("completed", "مكتمل"), ("cancelled", "ملغي")]:
            tk.Radiobutton(filter_bar, text=lbl, variable=self.status_var, value=val,
                           bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"],
                           selectcolor=COLORS["accent"], activebackground=COLORS["bg_secondary"],
                           font=FONTS["body_sm"], indicatoron=False,
                           relief="flat", padx=12, pady=5, cursor="hand2",
                           command=self._load_orders).pack(side="right", padx=2)

        tk.Label(filter_bar, text="الحالة:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_secondary"], font=FONTS["body_sm"]).pack(side="right", padx=8)

        # Date filter
        from tkcalendar import DateEntry
        tk.Label(filter_bar, text="إلى:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_secondary"], font=FONTS["body_sm"]).pack(side="right", padx=4)
        self.date_to = DateEntry(filter_bar, font=FONTS["body_sm"],
                                  background=COLORS["accent"], foreground="black",
                                  borderwidth=0, date_pattern="yyyy-mm-dd")
        self.date_to.pack(side="right", padx=4)

        tk.Label(filter_bar, text="من:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_secondary"], font=FONTS["body_sm"]).pack(side="right", padx=4)
        self.date_from = DateEntry(filter_bar, font=FONTS["body_sm"],
                                    background=COLORS["accent"], foreground="black",
                                    borderwidth=0, date_pattern="yyyy-mm-dd")
        self.date_from.pack(side="right", padx=4)

        tk.Button(filter_bar, text="🔍 بحث", bg=COLORS["accent"], fg="black",
                  font=FONTS["body_sm"], bd=0, padx=12, pady=5, relief="flat",
                  cursor="hand2", command=self._load_orders).pack(side="right", padx=8)

        # ── Orders Table ──────────────────────────────────────────────────────
        cols = [
            {"id": "num",      "label": "رقم الطلب",   "width": 160, "anchor": "w"},
            {"id": "time",     "label": "الوقت",        "width": 130, "anchor": "center"},
            {"id": "type",     "label": "النوع",        "width": 90,  "anchor": "center"},
            {"id": "table",    "label": "الطاولة",      "width": 70,  "anchor": "center"},
            {"id": "customer", "label": "العميل",       "width": 120, "anchor": "w"},
            {"id": "items",    "label": "الأصناف",      "width": 60,  "anchor": "center"},
            {"id": "total",    "label": "الإجمالي",     "width": 100, "anchor": "center"},
            {"id": "payment",  "label": "الدفع",        "width": 80,  "anchor": "center"},
            {"id": "cashier",  "label": "الكاشير",      "width": 120, "anchor": "w"},
            {"id": "status",   "label": "الحالة",       "width": 80,  "anchor": "center"},
        ]
        self.table = DataTable(self, cols)
        self.table.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        self.table.tree.bind("<Double-1>", self._view_order)
        self.table.tree.bind("<Button-3>", self._show_context_menu)

        # ── Action Bar ────────────────────────────────────────────────────────
        action_bar = tk.Frame(self, bg=COLORS["bg_secondary"], padx=16, pady=10)
        action_bar.grid(row=2, column=0, sticky="ew")

        self.summary_label = tk.Label(action_bar, text="",
                                       fg=COLORS["text_secondary"],
                                       bg=COLORS["bg_secondary"], font=FONTS["body_sm"])
        self.summary_label.pack(side="left")

        tk.Button(action_bar, text="🔄 طلب مرتجع", bg=COLORS["warning"], fg="black",
                  font=FONTS["body_sm"], bd=0, padx=12, pady=6, relief="flat",
                  cursor="hand2", command=self._refund_order).pack(side="right", padx=4)

        tk.Button(action_bar, text="❌ إلغاء طلب", bg=COLORS["danger"], fg="white",
                  font=FONTS["body_sm"], bd=0, padx=12, pady=6, relief="flat",
                  cursor="hand2", command=self._cancel_order).pack(side="right", padx=4)

        tk.Button(action_bar, text="🖨️ طباعة", bg=COLORS["info"], fg="white",
                  font=FONTS["body_sm"], bd=0, padx=12, pady=6, relief="flat",
                  cursor="hand2", command=self._print_order).pack(side="right", padx=4)

        tk.Button(action_bar, text="✏️ تعديل", bg=COLORS["accent"], fg="black",
                  font=FONTS["body_sm"], bd=0, padx=12, pady=6, relief="flat",
                  cursor="hand2", command=self._edit_order).pack(side="right", padx=4)

        self._load_orders()

    def _load_orders(self):
        self.table.clear()
        date_from = self.date_from.get_date().strftime("%Y-%m-%d")
        date_to   = self.date_to.get_date().strftime("%Y-%m-%d")
        status    = None if self.status_var.get() == "all" else self.status_var.get()
        orders = db.get_all_orders(date_from, date_to, status)
        self._orders = orders

        type_labels = {"dine_in": "صالة", "takeaway": "تيك أواي", "delivery": "ديليفري"}
        status_labels = {"open": "مفتوح", "completed": "مكتمل",
                         "cancelled": "ملغي", "refunded": "مرتجع"}

        total_revenue = 0
        for o in orders:
            items_count = len(db.get_order_items(o["id"]))
            self.table.insert_row((
                o.get("order_number", ""),
                o.get("created_at", "")[:16],
                type_labels.get(o.get("order_type"), o.get("order_type")),
                o.get("table_number") or "—",
                o.get("customer_name") or "—",
                items_count,
                f"{o.get('total', 0):.2f} ج.م",
                o.get("payment_method") or "—",
                o.get("cashier_name", ""),
                status_labels.get(o.get("status"), o.get("status")),
            ))
            if o.get("status") == "completed":
                total_revenue += o.get("total", 0)

        self.summary_label.config(
            text=f"إجمالي: {len(orders)} طلب  |  الإيرادات: {total_revenue:.2f} ج.م"
        )

    def _get_selected_order(self):
        sel = self.table.tree.selection()
        if not sel:
            Toast(self, "اختر طلباً أولاً", "warning")
            return None
        idx = self.table.tree.index(sel[0])
        return self._orders[idx] if idx < len(self._orders) else None

    def _view_order(self, event=None):
        order = self._get_selected_order()
        if not order:
            return
        self._show_order_detail(order)

    def _show_order_detail(self, order):
        win = tk.Toplevel(self)
        win.title(f"تفاصيل الطلب {order.get('order_number')}")
        win.config(bg=COLORS["bg_primary"])
        win.geometry("520x500")
        win.transient(self.winfo_toplevel())

        tk.Label(win, text=f"🧾 {order.get('order_number')}", fg=COLORS["accent"],
                 bg=COLORS["bg_primary"], font=FONTS["title_md"]).pack(pady=16)

        info_frame = tk.Frame(win, bg=COLORS["bg_card"], padx=20, pady=14)
        info_frame.pack(fill="x", padx=16)

        def info_row(label, value, row):
            tk.Label(info_frame, text=label, fg=COLORS["text_secondary"],
                     bg=COLORS["bg_card"], font=FONTS["body_sm"]).grid(row=row, column=0,
                                                                         sticky="w", pady=3)
            tk.Label(info_frame, text=value, fg=COLORS["text_primary"],
                     bg=COLORS["bg_card"], font=FONTS["body_sm"]).grid(row=row, column=1,
                                                                         sticky="w", padx=16, pady=3)

        info_row("الحالة:", order.get("status", ""), 0)
        info_row("التاريخ:", order.get("created_at", "")[:16], 1)
        info_row("الكاشير:", order.get("cashier_name", ""), 2)
        info_row("العميل:", order.get("customer_name") or "—", 3)
        info_row("الطاولة:", order.get("table_number") or "—", 4)
        info_row("طريقة الدفع:", order.get("payment_method") or "—", 5)

        items = db.get_order_items(order["id"])
        items_frame = tk.Frame(win, bg=COLORS["bg_primary"], pady=10, padx=16)
        items_frame.pack(fill="both", expand=True)

        tk.Label(items_frame, text="الأصناف:", fg=COLORS["accent"],
                 bg=COLORS["bg_primary"], font=FONTS["title_sm"]).pack(anchor="w")

        for it in items:
            row = tk.Frame(items_frame, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=it["item_name"], fg=COLORS["text_primary"],
                     bg=COLORS["bg_card"], font=FONTS["body_sm"], padx=10).pack(side="left")
            tk.Label(row, text=f"× {it['quantity']}", fg=COLORS["text_secondary"],
                     bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(side="left")
            tk.Label(row, text=f"{it['quantity'] * it['unit_price']:.2f} ج.م",
                     fg=COLORS["accent"], bg=COLORS["bg_card"],
                     font=FONTS["body_sm"]).pack(side="right", padx=10)

        totals_frame = tk.Frame(win, bg=COLORS["bg_card"], padx=20, pady=10)
        totals_frame.pack(fill="x", padx=16, pady=8)
        totals_frame.columnconfigure(1, weight=1)

        for i, (lbl, val) in enumerate([
            ("المجموع الفرعي:", f"{order.get('subtotal', 0):.2f} ج.م"),
            ("الخصم:", f"-{order.get('discount', 0):.2f} ج.م"),
            ("الضريبة:", f"{order.get('tax_amount', 0):.2f} ج.م"),
            ("💰 الإجمالي:", f"{order.get('total', 0):.2f} ج.م"),
        ]):
            bold = i == 3
            font = FONTS["title_sm"] if bold else FONTS["body_sm"]
            fg = COLORS["accent"] if bold else COLORS["text_secondary"]
            tk.Label(totals_frame, text=lbl, fg=fg, bg=COLORS["bg_card"],
                     font=font).grid(row=i, column=0, sticky="w", pady=2)
            tk.Label(totals_frame, text=val, fg=fg, bg=COLORS["bg_card"],
                     font=font).grid(row=i, column=1, sticky="e", pady=2)

        tk.Button(win, text="إغلاق", bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                  font=FONTS["body_sm"], bd=0, padx=20, pady=8, relief="flat",
                  cursor="hand2", command=win.destroy).pack(pady=12)

    def _edit_order(self):
        order = self._get_selected_order()
        if not order:
            return
        if order.get("status") != "open":
            Toast(self, "يمكن تعديل الطلبات المفتوحة فقط", "warning")
            return
        self.app.screens["cashier"].load_order(order["id"])

    def _cancel_order(self):
        order = self._get_selected_order()
        if not order:
            return
        if order.get("status") not in ("open", "completed"):
            Toast(self, "لا يمكن إلغاء هذا الطلب", "warning")
            return
        if messagebox.askyesno("تأكيد الإلغاء", f"إلغاء الطلب {order.get('order_number')}؟"):
            conn = db.get_connection()
            conn.execute("UPDATE orders SET status='cancelled' WHERE id=?", (order["id"],))
            conn.commit()
            conn.close()
            if order.get("table_id"):
                db.update_table_status(order["table_id"], "free")
            self._load_orders()
            Toast(self, "تم إلغاء الطلب", "success")

    def _refund_order(self):
        order = self._get_selected_order()
        if not order:
            return
        if order.get("status") != "completed":
            Toast(self, "يمكن الاسترجاع للطلبات المكتملة فقط", "warning")
            return
        if messagebox.askyesno("تأكيد الاسترجاع", f"استرجاع الطلب {order.get('order_number')}؟"):
            conn = db.get_connection()
            conn.execute("UPDATE orders SET status='refunded' WHERE id=?", (order["id"],))
            conn.commit()
            conn.close()
            self._load_orders()
            Toast(self, "تم تسجيل الاسترجاع", "success")

    def _print_order(self):
        order = self._get_selected_order()
        if not order:
            return
        self.app.screens["cashier"]._print_receipt_direct(order["id"])

    def _show_context_menu(self, event):
        menu = tk.Menu(self, tearoff=0, bg=COLORS["bg_card"],
                       fg=COLORS["text_primary"], activebackground=COLORS["accent"],
                       activeforeground="black", font=FONTS["body_sm"])
        menu.add_command(label="👁️ عرض التفاصيل", command=self._view_order)
        menu.add_command(label="✏️ تعديل", command=self._edit_order)
        menu.add_command(label="🖨️ طباعة الإيصال", command=self._print_order)
        menu.add_separator()
        menu.add_command(label="❌ إلغاء", command=self._cancel_order)
        menu.add_command(label="🔄 استرجاع", command=self._refund_order)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def on_show(self):
        self._load_orders()
