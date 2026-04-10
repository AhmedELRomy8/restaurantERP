"""
Cashier / POS Screen
Main point-of-sale interface for taking orders
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import database as db
from theme import COLORS, FONTS
from widgets import RoundedButton, Toast


class CashierScreen(tk.Frame):

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=COLORS["bg_primary"], **kwargs)
        self.app = app
        self.current_order = []          # list of dicts
        self.current_order_id = None
        self.order_type = tk.StringVar(value="dine_in")
        self.selected_table = None
        self.discount_var = tk.StringVar(value="0")
        self.discount_type = tk.StringVar(value="amount")  # amount | percent
        self._build_ui()

    # ─────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self._build_menu_panel()
        self._build_order_panel()

    # ── Left: Menu Panel ──────────────────────────────────────────────────────
    def _build_menu_panel(self):
        left = tk.Frame(self, bg=COLORS["bg_primary"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 1))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        # Top bar: search + order type
        top = tk.Frame(left, bg=COLORS["bg_secondary"], pady=10, padx=14)
        top.grid(row=0, column=0, sticky="ew")

        tk.Label(top, text="🔍", bg=COLORS["bg_secondary"],
                 fg=COLORS["text_secondary"], font=FONTS["body_lg"]).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._filter_items())
        search_entry = tk.Entry(top, textvariable=self.search_var,
                                bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                                insertbackground=COLORS["text_primary"],
                                font=FONTS["body_md"], bd=0, relief="flat", width=22)
        search_entry.pack(side="left", padx=8, ipady=6)

        # Order type toggle
        for val, lbl in [("dine_in", "🪑 صالة"), ("takeaway", "📦 تيك أواي"), ("delivery", "🛵 ديليفري")]:
            rb = tk.Radiobutton(top, text=lbl, variable=self.order_type, value=val,
                                bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"],
                                selectcolor=COLORS["accent"], activebackground=COLORS["bg_secondary"],
                                font=FONTS["body_sm"], indicatoron=False,
                                relief="flat", padx=10, pady=4,
                                command=self._on_order_type_change)
            rb.pack(side="right", padx=2)

        # Category tabs
        self.cat_frame = tk.Frame(left, bg=COLORS["bg_secondary"])
        self.cat_frame.grid(row=1, column=0, sticky="new")

        # Items grid
        items_outer = tk.Frame(left, bg=COLORS["bg_primary"])
        items_outer.grid(row=2, column=0, sticky="nsew", pady=0)
        left.rowconfigure(2, weight=1)

        canvas = tk.Canvas(items_outer, bg=COLORS["bg_primary"], highlightthickness=0)
        scrollbar = tk.Scrollbar(items_outer, orient="vertical", command=canvas.yview)
        self.items_frame = tk.Frame(canvas, bg=COLORS["bg_primary"])
        self.items_frame.bind("<Configure>",
                               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.items_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._selected_cat = None
        self._load_categories()
        self._load_items()

    def _load_categories(self):
        for w in self.cat_frame.winfo_children():
            w.destroy()

        cats = db.get_categories()
        # "All" button
        btn = tk.Button(self.cat_frame, text="🍽️ الكل",
                        bg=COLORS["accent"] if self._selected_cat is None else COLORS["bg_hover"],
                        fg="#000" if self._selected_cat is None else COLORS["text_primary"],
                        font=FONTS["body_sm"], bd=0, padx=14, pady=8,
                        relief="flat", cursor="hand2",
                        command=lambda: self._select_category(None))
        btn.pack(side="left", padx=2, pady=6)

        for cat in cats:
            c = cat["id"]
            is_sel = self._selected_cat == c
            btn = tk.Button(self.cat_frame,
                            text=f"{cat['icon']} {cat['name']}",
                            bg=cat["color"] if is_sel else COLORS["bg_hover"],
                            fg="white" if is_sel else COLORS["text_primary"],
                            font=FONTS["body_sm"], bd=0, padx=14, pady=8,
                            relief="flat", cursor="hand2",
                            command=lambda cid=c: self._select_category(cid))
            btn.pack(side="left", padx=2, pady=6)

    def _select_category(self, cat_id):
        self._selected_cat = cat_id
        self._load_categories()
        self._load_items()

    def _load_items(self):
        for w in self.items_frame.winfo_children():
            w.destroy()

        search = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        items = db.get_menu_items(self._selected_cat)
        if search:
            items = [i for i in items if search in i["name"].lower()]

        COLS = 4
        for idx, item in enumerate(items):
            row, col = divmod(idx, COLS)
            card = tk.Frame(self.items_frame, bg=COLORS["bg_card"],
                            bd=0, highlightthickness=1,
                            highlightbackground=COLORS["border"],
                            cursor="hand2", width=155, height=110)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            card.grid_propagate(False)

            color = item.get("cat_color", COLORS["accent"])
            bar = tk.Frame(card, bg=color, height=4)
            bar.pack(fill="x")

            inner = tk.Frame(card, bg=COLORS["bg_card"], padx=10, pady=8)
            inner.pack(fill="both", expand=True)

            tk.Label(inner, text=item["name"], fg=COLORS["text_primary"],
                     bg=COLORS["bg_card"], font=FONTS["body_sm"],
                     wraplength=130, justify="center").pack()

            tk.Label(inner, text=f"ج.م {item['price']:.2f}",
                     fg=COLORS["accent"], bg=COLORS["bg_card"],
                     font=FONTS["title_sm"]).pack(pady=(4, 0))

            for w in [card, inner, bar]:
                w.bind("<Button-1>", lambda e, it=item: self._add_item(it))
            for child in inner.winfo_children():
                child.bind("<Button-1>", lambda e, it=item: self._add_item(it))

        # Fill remaining columns to keep grid even
        total = len(items)
        rem = COLS - (total % COLS) if total % COLS else 0
        for i in range(rem):
            ph = tk.Frame(self.items_frame, bg=COLORS["bg_primary"], width=155, height=110)
            ph.grid(row=(total // COLS), column=(total % COLS) + i, padx=6, pady=6)

    def _filter_items(self):
        self._load_items()

    # ── Right: Order Panel ─────────────────────────────────────────────────────
    def _build_order_panel(self):
        right = tk.Frame(self, bg=COLORS["bg_secondary"])
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)

        # Header
        header = tk.Frame(right, bg=COLORS["bg_card"], pady=12, padx=16)
        header.grid(row=0, column=0, sticky="ew")

        self.order_num_label = tk.Label(header, text="طلب جديد",
                                         fg=COLORS["accent"], bg=COLORS["bg_card"],
                                         font=FONTS["title_md"])
        self.order_num_label.pack(side="left")

        self.table_btn = tk.Button(header, text="🪑 اختر طاولة",
                                   bg=COLORS["bg_hover"], fg=COLORS["text_secondary"],
                                   font=FONTS["body_sm"], bd=0, padx=12, pady=6,
                                   relief="flat", cursor="hand2",
                                   command=self._select_table)
        self.table_btn.pack(side="right")

        # Customer info
        cust = tk.Frame(right, bg=COLORS["bg_secondary"], padx=16, pady=8)
        cust.grid(row=1, column=0, sticky="ew")

        tk.Label(cust, text="👤 العميل:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_secondary"], font=FONTS["body_sm"]).pack(side="left")
        self.cust_name = tk.Entry(cust, bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                                   insertbackground=COLORS["text_primary"],
                                   font=FONTS["body_sm"], bd=0, relief="flat", width=16)
        self.cust_name.pack(side="left", padx=8, ipady=4)

        tk.Label(cust, text="📞", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_secondary"], font=FONTS["body_sm"]).pack(side="left")
        self.cust_phone = tk.Entry(cust, bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                                    insertbackground=COLORS["text_primary"],
                                    font=FONTS["body_sm"], bd=0, relief="flat", width=14)
        self.cust_phone.pack(side="left", padx=6, ipady=4)

        # Order items list
        list_frame = tk.Frame(right, bg=COLORS["bg_secondary"])
        list_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=8)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        cols = [
            {"id": "name",  "label": "الصنف",     "width": 160, "anchor": "w",      "stretch": True},
            {"id": "qty",   "label": "الكمية",    "width": 60,  "anchor": "center", "stretch": False},
            {"id": "price", "label": "السعر",     "width": 80,  "anchor": "center", "stretch": False},
            {"id": "total", "label": "الإجمالي",  "width": 90,  "anchor": "center", "stretch": False},
        ]
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("POS.Treeview",
                         background=COLORS["bg_card"],
                         foreground=COLORS["text_primary"],
                         fieldbackground=COLORS["bg_card"],
                         rowheight=40, font=FONTS["body_md"])
        style.configure("POS.Treeview.Heading",
                         background=COLORS["bg_hover"],
                         foreground=COLORS["accent"],
                         font=FONTS["body_sm"], relief="flat")
        style.map("POS.Treeview",
                  background=[("selected", COLORS["accent_dark"])],
                  foreground=[("selected", "white")])

        scroll = tk.Scrollbar(list_frame, bg=COLORS["bg_card"])
        scroll.grid(row=0, column=1, sticky="ns")

        self.order_tree = ttk.Treeview(list_frame,
                                        columns=["name", "qty", "price", "total"],
                                        show="headings", style="POS.Treeview",
                                        yscrollcommand=scroll.set)
        scroll.config(command=self.order_tree.yview)
        for col in cols:
            self.order_tree.heading(col["id"], text=col["label"], anchor=col["anchor"])
            self.order_tree.column(col["id"], width=col["width"], anchor=col["anchor"],
                                   stretch=col["stretch"])
        self.order_tree.grid(row=0, column=0, sticky="nsew")
        self.order_tree.bind("<Double-1>", self._edit_item)
        self.order_tree.bind("<Delete>", self._remove_item)

        # Quick action buttons for selected item
        action_bar = tk.Frame(right, bg=COLORS["bg_secondary"], pady=4)
        action_bar.grid(row=3, column=0, sticky="ew", padx=12)

        for icon, txt, cmd in [
            ("➕", "+1", lambda: self._change_qty(1)),
            ("➖", "-1", lambda: self._change_qty(-1)),
            ("📝", "ملاحظة", self._add_note),
            ("🗑️", "حذف", self._remove_item),
            ("🔄", "مسح الكل", self._clear_order),
        ]:
            tk.Button(action_bar, text=f"{icon} {txt}",
                      bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                      font=FONTS["body_sm"], bd=0, padx=10, pady=6,
                      relief="flat", cursor="hand2", command=cmd).pack(side="left", padx=3)

        # Totals section
        tot_frame = tk.Frame(right, bg=COLORS["bg_card"], padx=16, pady=12)
        tot_frame.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 6))
        tot_frame.columnconfigure(1, weight=1)

        def tot_row(text, var_name, row, bold=False, accent=False):
            fg = COLORS["accent"] if accent else (COLORS["text_primary"] if bold else COLORS["text_secondary"])
            font = FONTS["title_sm"] if bold else FONTS["body_md"]
            tk.Label(tot_frame, text=text, fg=fg, bg=COLORS["bg_card"], font=font).grid(
                row=row, column=0, sticky="w", pady=2)
            lbl = tk.Label(tot_frame, text="0.00 ج.م", fg=fg, bg=COLORS["bg_card"], font=font)
            lbl.grid(row=row, column=1, sticky="e", pady=2)
            return lbl

        self.lbl_subtotal  = tot_row("المجموع الفرعي:", "subtotal", 0)
        self.lbl_discount  = tot_row("الخصم:", "discount", 1)

        # Discount row
        disc_row = tk.Frame(tot_frame, bg=COLORS["bg_card"])
        disc_row.grid(row=2, column=0, columnspan=2, sticky="ew", pady=4)
        tk.Label(disc_row, text="خصم:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(side="left")
        self.disc_entry = tk.Entry(disc_row, textvariable=self.discount_var,
                                    bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                                    insertbackground=COLORS["text_primary"],
                                    font=FONTS["body_sm"], bd=0, relief="flat", width=8)
        self.disc_entry.pack(side="left", padx=6, ipady=4)
        self.discount_var.trace_add("write", lambda *a: self._recalculate())

        for val, lbl in [("amount", "ج.م"), ("percent", "%")]:
            tk.Radiobutton(disc_row, text=lbl, variable=self.discount_type, value=val,
                           bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                           selectcolor=COLORS["accent"], activebackground=COLORS["bg_card"],
                           font=FONTS["body_sm"], command=self._recalculate).pack(side="left", padx=4)

        self.lbl_tax      = tot_row("الضريبة (14%):", "tax", 3)

        sep = tk.Frame(tot_frame, bg=COLORS["border"], height=1)
        sep.grid(row=4, column=0, columnspan=2, sticky="ew", pady=6)

        self.lbl_total    = tot_row("💰 الإجمالي:", "total", 5, bold=True, accent=True)

        # Payment section
        pay_frame = tk.Frame(right, bg=COLORS["bg_secondary"], padx=16, pady=10)
        pay_frame.grid(row=5, column=0, sticky="ew", padx=12)

        tk.Label(pay_frame, text="طريقة الدفع:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_secondary"], font=FONTS["body_sm"]).pack(anchor="w")

        pm_row = tk.Frame(pay_frame, bg=COLORS["bg_secondary"])
        pm_row.pack(fill="x", pady=6)

        self.payment_method = tk.StringVar(value="cash")
        for val, lbl, icon in [("cash", "نقدي", "💵"), ("card", "بطاقة", "💳"), ("wallet", "محفظة", "📱")]:
            rb = tk.Radiobutton(pm_row, text=f"{icon} {lbl}", variable=self.payment_method, value=val,
                                bg=COLORS["bg_secondary"], fg=COLORS["text_secondary"],
                                selectcolor=COLORS["bg_card"], activebackground=COLORS["bg_secondary"],
                                font=FONTS["body_sm"], indicatoron=False,
                                relief="flat", padx=12, pady=6, cursor="hand2",
                                command=self._on_payment_change)
            rb.pack(side="left", padx=3)

        paid_row = tk.Frame(pay_frame, bg=COLORS["bg_secondary"])
        paid_row.pack(fill="x", pady=4)

        tk.Label(paid_row, text="المبلغ المدفوع:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_secondary"], font=FONTS["body_sm"]).pack(side="left")
        self.paid_var = tk.StringVar(value="0")
        self.paid_entry = tk.Entry(paid_row, textvariable=self.paid_var,
                                    bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                                    insertbackground=COLORS["text_primary"],
                                    font=FONTS["body_md"], bd=0, relief="flat", width=12)
        self.paid_entry.pack(side="left", padx=8, ipady=6)
        self.paid_var.trace_add("write", lambda *a: self._calc_change())

        self.lbl_change = tk.Label(paid_row, text="الباقي: 0.00 ج.م",
                                    fg=COLORS["success"], bg=COLORS["bg_secondary"],
                                    font=FONTS["body_sm"])
        self.lbl_change.pack(side="left")

        # Action buttons
        btn_frame = tk.Frame(right, bg=COLORS["bg_secondary"], padx=12, pady=12)
        btn_frame.grid(row=6, column=0, sticky="ew")
        btn_frame.columnconfigure((0, 1, 2), weight=1)

        save_btn = tk.Button(btn_frame, text="💾 حفظ طلب",
                              bg=COLORS["info"], fg="white",
                              font=FONTS["body_md"], bd=0, padx=0, pady=10,
                              relief="flat", cursor="hand2", command=self._save_order)
        save_btn.grid(row=0, column=0, sticky="ew", padx=3)

        print_btn = tk.Button(btn_frame, text="🖨️ طباعة",
                               bg=COLORS["warning"], fg="white",
                               font=FONTS["body_md"], bd=0, padx=0, pady=10,
                               relief="flat", cursor="hand2", command=self._print_receipt)
        print_btn.grid(row=0, column=1, sticky="ew", padx=3)

        pay_btn = tk.Button(btn_frame, text="✅ دفع وإغلاق",
                             bg=COLORS["success"], fg="white",
                             font=FONTS["title_sm"], bd=0, padx=0, pady=10,
                             relief="flat", cursor="hand2", command=self._complete_order)
        pay_btn.grid(row=0, column=2, sticky="ew", padx=3)

        new_btn = tk.Button(btn_frame, text="➕ طلب جديد",
                             bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                             font=FONTS["body_sm"], bd=0, pady=6,
                             relief="flat", cursor="hand2", command=self.new_order)
        new_btn.grid(row=1, column=0, columnspan=3, sticky="ew", padx=3, pady=(6, 0))

    # ─────────────────────────────────────────────────────────────────────────
    def _on_order_type_change(self):
        ot = self.order_type.get()
        if ot != "dine_in":
            self.selected_table = None
            self.table_btn.config(text="—")

    def _on_payment_change(self):
        pm = self.payment_method.get()
        if pm != "cash":
            self._set_paid(self._get_total())

    def _add_item(self, item: dict):
        # Check if item already exists
        for existing in self.current_order:
            if existing["menu_item_id"] == item["id"]:
                existing["quantity"] += 1
                self._refresh_tree()
                self._recalculate()
                return

        self.current_order.append({
            "menu_item_id": item["id"],
            "item_name": item["name"],
            "quantity": 1,
            "unit_price": item["price"],
            "tax_rate": item.get("tax_rate", 0.14),
            "notes": "",
        })
        self._refresh_tree()
        self._recalculate()

    def _refresh_tree(self):
        for row in self.order_tree.get_children():
            self.order_tree.delete(row)
        for i, it in enumerate(self.current_order):
            total = it["quantity"] * it["unit_price"]
            tag = "odd" if i % 2 else "even"
            self.order_tree.insert("", "end", iid=str(i),
                                    values=(it["item_name"], it["quantity"],
                                            f"{it['unit_price']:.2f}", f"{total:.2f}"),
                                    tags=(tag,))
        self.order_tree.tag_configure("odd", background=COLORS["bg_hover"])
        self.order_tree.tag_configure("even", background=COLORS["bg_card"])

    def _get_selected_idx(self):
        sel = self.order_tree.selection()
        if not sel:
            return None
        return int(sel[0])

    def _change_qty(self, delta: int):
        idx = self._get_selected_idx()
        if idx is None:
            return
        self.current_order[idx]["quantity"] += delta
        if self.current_order[idx]["quantity"] <= 0:
            self.current_order.pop(idx)
        self._refresh_tree()
        self._recalculate()

    def _edit_item(self, event=None):
        idx = self._get_selected_idx()
        if idx is None:
            return
        it = self.current_order[idx]
        qty = simpledialog.askinteger("تعديل الكمية", f"كمية '{it['item_name']}':",
                                      initialvalue=it["quantity"], minvalue=1)
        if qty:
            it["quantity"] = qty
            self._refresh_tree()
            self._recalculate()

    def _add_note(self):
        idx = self._get_selected_idx()
        if idx is None:
            return
        it = self.current_order[idx]
        note = simpledialog.askstring("ملاحظة", f"ملاحظة على '{it['item_name']}':",
                                       initialvalue=it.get("notes", ""))
        if note is not None:
            it["notes"] = note

    def _remove_item(self, event=None):
        idx = self._get_selected_idx()
        if idx is None:
            return
        self.current_order.pop(idx)
        self._refresh_tree()
        self._recalculate()

    def _clear_order(self):
        if not self.current_order:
            return
        if messagebox.askyesno("تأكيد", "مسح الطلب الحالي؟"):
            self.new_order()

    def _recalculate(self):
        subtotal = sum(it["quantity"] * it["unit_price"] for it in self.current_order)
        try:
            disc_val = float(self.discount_var.get() or 0)
        except ValueError:
            disc_val = 0

        if self.discount_type.get() == "percent":
            discount = subtotal * disc_val / 100
        else:
            discount = min(disc_val, subtotal)

        after_disc = subtotal - discount
        tax = sum(
            it["quantity"] * it["unit_price"] * it.get("tax_rate", 0) * (1 - (
                disc_val/100 if self.discount_type.get() == "percent" else 0))
            for it in self.current_order
        )
        total = after_disc + tax

        self.lbl_subtotal.config(text=f"{subtotal:.2f} ج.م")
        self.lbl_discount.config(text=f"-{discount:.2f} ج.م")
        self.lbl_tax.config(text=f"{tax:.2f} ج.م")
        self.lbl_total.config(text=f"{total:.2f} ج.م")

        self._current_subtotal = subtotal
        self._current_discount = discount
        self._current_tax = tax
        self._current_total = total

        if self.payment_method.get() != "cash":
            self._set_paid(total)
        self._calc_change()

    def _get_total(self):
        return getattr(self, "_current_total", 0)

    def _set_paid(self, amount):
        self.paid_var.set(f"{amount:.2f}")

    def _calc_change(self):
        try:
            paid = float(self.paid_var.get() or 0)
        except ValueError:
            paid = 0
        total = self._get_total()
        change = paid - total
        color = COLORS["success"] if change >= 0 else COLORS["danger"]
        self.lbl_change.config(text=f"الباقي: {change:.2f} ج.م", fg=color)

    def _select_table(self):
        tables = db.get_tables()
        win = tk.Toplevel(self)
        win.title("اختر طاولة")
        win.config(bg=COLORS["bg_primary"])
        win.geometry("500x400")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        tk.Label(win, text="🪑 اختر الطاولة", fg=COLORS["accent"],
                 bg=COLORS["bg_primary"], font=FONTS["title_md"]).pack(pady=16)

        grid_frame = tk.Frame(win, bg=COLORS["bg_primary"])
        grid_frame.pack(fill="both", expand=True, padx=16)

        for i, t in enumerate(tables):
            row, col = divmod(i, 4)
            status_colors = {
                "free": COLORS["success"],
                "occupied": COLORS["danger"],
                "reserved": COLORS["warning"],
            }
            status_labels = {"free": "فارغة", "occupied": "مشغولة", "reserved": "محجوزة"}
            color = status_colors.get(t["status"], COLORS["text_muted"])

            card = tk.Frame(grid_frame, bg=COLORS["bg_card"], bd=0,
                            highlightthickness=2, highlightbackground=color,
                            cursor="hand2" if t["status"] != "occupied" else "no",
                            width=100, height=80)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            card.grid_propagate(False)

            tk.Label(card, text=f"🪑 {t['number']}", fg=color, bg=COLORS["bg_card"],
                     font=FONTS["title_sm"]).place(relx=0.5, rely=0.35, anchor="center")
            tk.Label(card, text=status_labels.get(t["status"], ""), fg=COLORS["text_secondary"],
                     bg=COLORS["bg_card"], font=FONTS["body_sm"]).place(relx=0.5, rely=0.7, anchor="center")

            if t["status"] != "occupied":
                card.bind("<Button-1>", lambda e, tbl=t: self._on_table_selected(tbl, win))
                for child in card.winfo_children():
                    child.bind("<Button-1>", lambda e, tbl=t: self._on_table_selected(tbl, win))

    def _on_table_selected(self, table, win):
        self.selected_table = table
        self.table_btn.config(text=f"🪑 {table['number']}")
        win.destroy()

    def _get_order_data(self, status="open"):
        return {
            "id": self.current_order_id,
            "order_number": getattr(self, "_order_number", db.generate_order_number()),
            "table_id": self.selected_table["id"] if self.selected_table else None,
            "order_type": self.order_type.get(),
            "customer_name": self.cust_name.get(),
            "customer_phone": self.cust_phone.get(),
            "status": status,
            "user_id": self.app.current_user["id"],
            "subtotal": getattr(self, "_current_subtotal", 0),
            "discount": getattr(self, "_current_discount", 0),
            "discount_type": self.discount_type.get(),
            "tax_amount": getattr(self, "_current_tax", 0),
            "total": getattr(self, "_current_total", 0),
            "payment_method": self.payment_method.get(),
            "amount_paid": float(self.paid_var.get() or 0),
            "change_due": float(self.paid_var.get() or 0) - getattr(self, "_current_total", 0),
            "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "completed" else None,
        }

    def _save_order(self):
        if not self.current_order:
            Toast(self, "لا توجد أصناف في الطلب!", "warning")
            return
        order_data = self._get_order_data("open")
        if not hasattr(self, "_order_number"):
            self._order_number = order_data["order_number"]
        order_id = db.save_order(order_data, self.current_order)
        self.current_order_id = order_id
        if self.selected_table:
            db.update_table_status(self.selected_table["id"], "occupied")
        self.order_num_label.config(text=f"# {self._order_number}")
        Toast(self, f"تم حفظ الطلب {self._order_number}", "success")

    def _complete_order(self):
        if not self.current_order:
            Toast(self, "لا توجد أصناف في الطلب!", "warning")
            return
        total = self._get_total()
        try:
            paid = float(self.paid_var.get() or 0)
        except ValueError:
            paid = 0
        if self.payment_method.get() == "cash" and paid < total:
            Toast(self, "المبلغ المدفوع أقل من الإجمالي!", "error")
            return

        order_data = self._get_order_data("completed")
        if not hasattr(self, "_order_number"):
            self._order_number = order_data["order_number"]
        order_id = db.save_order(order_data, self.current_order)
        self.current_order_id = order_id

        if self.selected_table:
            db.update_table_status(self.selected_table["id"], "free")

        Toast(self, f"تم إغلاق الطلب بنجاح! 💰 الباقي: {paid - total:.2f} ج.م", "success")
        self._print_receipt_direct(order_id)
        self.new_order()

    def _print_receipt(self):
        if not self.current_order:
            return
        self._save_order()
        self._print_receipt_direct(self.current_order_id)

    def _print_receipt_direct(self, order_id):
        """Show receipt in a popup window."""
        items = db.get_order_items(order_id)
        conn_rows = db.get_all_orders(limit=1)
        order = None
        import database as _db
        conn = _db.get_connection()
        row = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
        if row:
            order = dict(row)
        conn.close()
        if not order:
            return

        win = tk.Toplevel(self)
        win.title("إيصال")
        win.config(bg="white")
        win.geometry("380x600")
        win.resizable(False, False)

        def add(text, font_size=11, bold=False, center=True, color="black"):
            fw = "bold" if bold else "normal"
            lbl = tk.Label(win, text=text, bg="white", fg=color,
                           font=("Cairo", font_size, fw))
            if center:
                lbl.pack(anchor="center")
            else:
                lbl.pack(anchor="w", padx=20)

        add("🍽️ مطعم الأصالة", 16, bold=True)
        add("فاتورة ضريبية مبسطة", 10)
        add("─" * 40, 9)
        add(f"رقم الطلب: {order.get('order_number', '')}", 10)
        add(f"التاريخ: {order.get('created_at', '')[:16]}", 10)
        if order.get("customer_name"):
            add(f"العميل: {order['customer_name']}", 10)
        add("─" * 40, 9)

        for it in items:
            line = f"{it['item_name']:<20} {it['quantity']}x  {it['unit_price']:.2f}"
            add(line, 10, center=False)

        add("─" * 40, 9)
        add(f"المجموع الفرعي: {order.get('subtotal', 0):.2f} ج.م", 10)
        if order.get("discount", 0) > 0:
            add(f"الخصم: -{order['discount']:.2f} ج.م", 10, color="red")
        add(f"الضريبة (14%): {order.get('tax_amount', 0):.2f} ج.م", 10)
        add(f"─" * 40, 9)
        add(f"💰 الإجمالي: {order.get('total', 0):.2f} ج.م", 13, bold=True)
        add(f"طريقة الدفع: {order.get('payment_method', '')}", 10)
        add(f"المدفوع: {order.get('amount_paid', 0):.2f} ج.م", 10)
        if order.get("change_due", 0) > 0:
            add(f"الباقي: {order['change_due']:.2f} ج.م", 10)
        add("─" * 40, 9)
        add("شكراً لزيارتكم ❤️", 12, bold=True)
        add("نتمنى لكم وجبة شهية", 10)

        tk.Button(win, text="طباعة / إغلاق", command=win.destroy,
                  bg=COLORS["accent"], fg="black", font=("Cairo", 11, "bold"),
                  bd=0, padx=20, pady=8, relief="flat", cursor="hand2").pack(pady=12)

    def new_order(self):
        self.current_order.clear()
        self.current_order_id = None
        if hasattr(self, "_order_number"):
            del self._order_number
        self.selected_table = None
        self.table_btn.config(text="🪑 اختر طاولة")
        self.order_num_label.config(text="طلب جديد")
        self.cust_name.delete(0, "end")
        self.cust_phone.delete(0, "end")
        self.discount_var.set("0")
        self.paid_var.set("0")
        self.order_type.set("dine_in")
        self._refresh_tree()
        self._recalculate()

    def load_order(self, order_id: int):
        """Load an existing open order for editing."""
        import database as _db
        conn = _db.get_connection()
        row = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
        conn.close()
        if not row:
            return
        order = dict(row)
        items = db.get_order_items(order_id)

        self.current_order = []
        for it in items:
            self.current_order.append({
                "menu_item_id": it["menu_item_id"],
                "item_name": it["item_name"],
                "quantity": it["quantity"],
                "unit_price": it["unit_price"],
                "tax_rate": it.get("tax_rate", 0.14),
                "notes": it.get("notes", ""),
            })

        self.current_order_id = order_id
        self._order_number = order["order_number"]
        self.order_type.set(order.get("order_type", "dine_in"))
        self.cust_name.delete(0, "end")
        self.cust_name.insert(0, order.get("customer_name") or "")
        self.cust_phone.delete(0, "end")
        self.cust_phone.insert(0, order.get("customer_phone") or "")
        self.discount_var.set(str(order.get("discount", 0)))
        self.order_num_label.config(text=f"# {self._order_number}")
        self._refresh_tree()
        self._recalculate()
        self.app.show_screen("cashier")
