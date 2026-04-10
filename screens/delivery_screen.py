"""
Delivery Management Screen
"""
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import database as db
from theme import COLORS, FONTS
from widgets import DataTable, Toast


class DeliveryScreen(tk.Frame):

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

        tk.Label(filter_bar, text="🚗 إدارة الدليفري", fg=COLORS["accent"],
                 bg=COLORS["bg_secondary"], font=FONTS["title_md"]).pack(side="left")

        # Status filter
        self.status_var = tk.StringVar(value="all")
        for val, lbl in [("all", "الكل"), ("pending", "قيد الانتظار"), 
                         ("assigned", "مخصصة"), ("in_transit", "في الطريق"), 
                         ("delivered", "تم التسليم"), ("cancelled", "ملغاة")]:
            tk.Radiobutton(filter_bar, text=lbl, variable=self.status_var, value=val,
                           bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"],
                           selectcolor=COLORS["accent"], activebackground=COLORS["bg_secondary"],
                           font=FONTS["body_sm"], indicatoron=False,
                           relief="flat", padx=12, pady=5, cursor="hand2",
                           command=self._load_deliveries).pack(side="right", padx=2)

        tk.Label(filter_bar, text="الحالة:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_secondary"], font=FONTS["body_sm"]).pack(side="right", padx=8)

        # ── Deliveries Table ──────────────────────────────────────────────────
        cols = [
            {"id": "num",      "label": "رقم الطلب",   "width": 140, "anchor": "w"},
            {"id": "time",     "label": "الوقت",        "width": 130, "anchor": "center"},
            {"id": "customer", "label": "العميل",       "width": 120, "anchor": "w"},
            {"id": "phone",    "label": "الهاتف",       "width": 120, "anchor": "center"},
            {"id": "address",  "label": "العنوان",      "width": 200, "anchor": "w"},
            {"id": "driver",   "label": "سائق التوصيل", "width": 140, "anchor": "w"},
            {"id": "fee",      "label": "رسم التوصيل",  "width": 100, "anchor": "center"},
            {"id": "total",    "label": "الإجمالي",     "width": 100, "anchor": "center"},
            {"id": "status",   "label": "الحالة",       "width": 100, "anchor": "center"},
        ]
        self.table = DataTable(self, cols)
        self.table.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        self.table.tree.bind("<Double-1>", self._edit_delivery)
        self.table.tree.bind("<Button-3>", self._show_context_menu)

        # ── Action Bar ────────────────────────────────────────────────────────
        action_bar = tk.Frame(self, bg=COLORS["bg_secondary"], padx=16, pady=10)
        action_bar.grid(row=2, column=0, sticky="ew")

        self.summary_label = tk.Label(action_bar, text="",
                                       fg=COLORS["text_secondary"],
                                       bg=COLORS["bg_secondary"], font=FONTS["body_sm"])
        self.summary_label.pack(side="left")

        tk.Button(action_bar, text="✅ تم التسليم", bg=COLORS["success"], fg="white",
                  font=FONTS["body_sm"], bd=0, padx=12, pady=6, relief="flat",
                  cursor="hand2", command=self._mark_delivered).pack(side="right", padx=4)

        tk.Button(action_bar, text="🚗 في الطريق", bg=COLORS["info"], fg="white",
                  font=FONTS["body_sm"], bd=0, padx=12, pady=6, relief="flat",
                  cursor="hand2", command=self._mark_in_transit).pack(side="right", padx=4)

        tk.Button(action_bar, text="✏️ تعديل", bg=COLORS["accent"], fg="black",
                  font=FONTS["body_sm"], bd=0, padx=12, pady=6, relief="flat",
                  cursor="hand2", command=self._edit_delivery).pack(side="right", padx=4)

        tk.Button(action_bar, text="➕ أضف توصيل", bg=COLORS["success"], fg="white",
                  font=FONTS["body_sm"], bd=0, padx=12, pady=6, relief="flat",
                  cursor="hand2", command=self._new_delivery).pack(side="right", padx=4)

        self._load_deliveries()

    def _load_deliveries(self):
        self.table.clear()
        status = None if self.status_var.get() == "all" else self.status_var.get()
        deliveries = db.get_all_deliveries(status)
        self._deliveries = deliveries

        status_labels = {"pending": "قيد الانتظار", "assigned": "مخصصة",
                         "in_transit": "في الطريق", "delivered": "تم التسليم", 
                         "cancelled": "ملغاة"}

        total_fee = 0
        for d in deliveries:
            self.table.insert_row((
                d.get("order_number", ""),
                d.get("order_time", "")[:16],
                d.get("customer_name") or "—",
                d.get("customer_phone") or "—",
                d.get("delivery_address", ""),
                d.get("delivery_person") or "—",
                f"{d.get('delivery_fee', 0):.2f} ج.م",
                f"{d.get('total', 0):.2f} ج.م",
                status_labels.get(d.get("status"), d.get("status")),
            ))
            if d.get("status") == "delivered":
                total_fee += d.get("delivery_fee", 0)

        self.summary_label.config(
            text=f"إجمالي: {len(deliveries)} توصيل  |  رسوم التوصيل: {total_fee:.2f} ج.م"
        )

    def _get_selected_delivery(self):
        sel = self.table.tree.selection()
        if not sel:
            Toast(self, "اختر توصيلاً أولاً", "warning")
            return None
        idx = self.table.tree.index(sel[0])
        return self._deliveries[idx] if idx < len(self._deliveries) else None

    def _new_delivery(self):
        delivery = self._get_selected_delivery()
        if not delivery:
            Toast(self, "يجب أن تكون هناك طلبية أولاً", "warning")
            return
        self._show_delivery_form(delivery["order_id"])

    def _edit_delivery(self, event=None):
        delivery = self._get_selected_delivery()
        if not delivery:
            return
        self._show_delivery_form(delivery["order_id"], delivery)

    def _show_delivery_form(self, order_id: int, delivery=None):
        """Show delivery form dialog."""
        win = tk.Toplevel(self)
        win.title("توصيل" if not delivery else f"تعديل التوصيل - {delivery.get('order_number')}")
        win.config(bg=COLORS["bg_primary"])
        win.geometry("500x600")
        win.transient(self)
        win.grab_set()

        # Center
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 500) // 2
        y = self.winfo_y() + (self.winfo_height() - 600) // 2
        win.geometry(f"+{x}+{y}")

        # Head
        tk.Label(win, text="🚗 تفاصيل التوصيل",
                 fg=COLORS["accent"], bg=COLORS["bg_primary"],
                 font=FONTS["title_md"]).pack(pady=20)

        form = tk.Frame(win, bg=COLORS["bg_card"], padx=24, pady=20)
        form.pack(fill="both", expand=True, padx=20, pady=10)

        # Fields
        fields = {}

        tk.Label(form, text="سائق التوصيل:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w")
        fields["driver"] = tk.Entry(form, bg=COLORS["bg_hover"], 
                                     fg=COLORS["text_primary"],
                                     insertbackground=COLORS["text_primary"],
                                     font=FONTS["body_md"], bd=0, relief="flat")
        fields["driver"].pack(fill="x", ipady=10, pady=(4, 12))
        if delivery:
            fields["driver"].insert(0, delivery.get("delivery_person", ""))

        tk.Label(form, text="رقم الهاتف:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w")
        fields["phone"] = tk.Entry(form, bg=COLORS["bg_hover"],
                                    fg=COLORS["text_primary"],
                                    insertbackground=COLORS["text_primary"],
                                    font=FONTS["body_md"], bd=0, relief="flat")
        fields["phone"].pack(fill="x", ipady=10, pady=(4, 12))
        if delivery:
            fields["phone"].insert(0, delivery.get("driver_phone", ""))

        tk.Label(form, text="عنوان التوصيل:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w")
        fields["address"] = tk.Text(form, bg=COLORS["bg_hover"],
                                     fg=COLORS["text_primary"],
                                     insertbackground=COLORS["text_primary"],
                                     font=FONTS["body_md"], bd=0, relief="flat",
                                     height=3)
        fields["address"].pack(fill="x", ipady=10, pady=(4, 12))
        if delivery:
            fields["address"].insert("1.0", delivery.get("delivery_address", ""))

        tk.Label(form, text="رسم التوصيل (ج.م):", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w")
        fields["fee"] = tk.Entry(form, bg=COLORS["bg_hover"],
                                 fg=COLORS["text_primary"],
                                 insertbackground=COLORS["text_primary"],
                                 font=FONTS["body_md"], bd=0, relief="flat")
        fields["fee"].pack(fill="x", ipady=10, pady=(4, 12))
        fields["fee"].insert(0, str(delivery.get("delivery_fee", 0) if delivery else 0))

        tk.Label(form, text="ملاحظات:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w")
        fields["notes"] = tk.Text(form, bg=COLORS["bg_hover"],
                                   fg=COLORS["text_primary"],
                                   insertbackground=COLORS["text_primary"],
                                   font=FONTS["body_md"], bd=0, relief="flat",
                                   height=2)
        fields["notes"].pack(fill="x", ipady=8, pady=(4, 16))
        if delivery:
            fields["notes"].insert("1.0", delivery.get("delivery_notes", ""))

        def save():
            try:
                data = {
                    "id": delivery["id"] if delivery else None,
                    "delivery_person": fields["driver"].get(),
                    "driver_phone": fields["phone"].get(),
                    "delivery_address": fields["address"].get("1.0", "end").strip(),
                    "delivery_fee": float(fields["fee"].get() or 0),
                    "delivery_notes": fields["notes"].get("1.0", "end").strip(),
                }
                db.save_delivery(order_id, data)
                win.destroy()
                self._load_deliveries()
                Toast(self, "تم الحفظ بنجاح ✅", "success")
            except ValueError:
                Toast(win, "تحقق من القيم المدخلة", "error")

        tk.Button(form, text="✅ حفظ",
                  bg=COLORS["success"], fg="white",
                  font=FONTS["title_sm"], bd=0, pady=10, relief="flat",
                  cursor="hand2", command=save).pack(fill="x")

        tk.Button(form, text="إلغاء",
                  bg=COLORS["bg_hover"], fg=COLORS["text_secondary"],
                  font=FONTS["body_sm"], bd=0, pady=6, relief="flat",
                  cursor="hand2", command=win.destroy).pack(fill="x", pady=(6, 0))

    def _mark_in_transit(self):
        delivery = self._get_selected_delivery()
        if not delivery:
            return
        db.update_delivery_status(delivery["id"], "in_transit", "started_at")
        self._load_deliveries()
        Toast(self, f"تم تحديث الحالة: في الطريق 🚗", "success")

    def _mark_delivered(self):
        delivery = self._get_selected_delivery()
        if not delivery:
            return
        db.update_delivery_status(delivery["id"], "delivered", "delivered_at")
        self._load_deliveries()
        Toast(self, f"تم تحديث الحالة: تم التسليم ✅", "success")

    def _show_context_menu(self, event):
        """Right-click context menu."""
        menu = tk.Menu(self, tearoff=0, bg=COLORS["bg_secondary"],
                       fg=COLORS["text_primary"], activebackground=COLORS["accent"])
        menu.add_command(label="تعديل", command=self._edit_delivery)
        menu.add_command(label="في الطريق", command=self._mark_in_transit)
        menu.add_command(label="تم التسليم", command=self._mark_delivered)
        menu.post(event.x_root, event.y_root)
