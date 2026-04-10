"""
Menu Management Screen
Add / edit / delete menu items and categories
"""
import tkinter as tk
from tkinter import messagebox
import database as db
from theme import COLORS, FONTS
from widgets import DataTable, Toast


class MenuScreen(tk.Frame):

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=COLORS["bg_primary"], **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=COLORS["bg_secondary"], padx=16, pady=12)
        hdr.grid(row=0, column=0, sticky="ew")

        tk.Label(hdr, text="🍽️ إدارة قائمة الطعام", fg=COLORS["accent"],
                 bg=COLORS["bg_secondary"], font=FONTS["title_md"]).pack(side="left")

        tk.Button(hdr, text="➕ صنف جديد", bg=COLORS["success"], fg="white",
                  font=FONTS["body_sm"], bd=0, padx=14, pady=7, relief="flat",
                  cursor="hand2", command=self._add_item).pack(side="right", padx=4)

        tk.Button(hdr, text="📂 فئة جديدة", bg=COLORS["info"], fg="white",
                  font=FONTS["body_sm"], bd=0, padx=14, pady=7, relief="flat",
                  cursor="hand2", command=self._add_category).pack(side="right", padx=4)

        # Category filter
        self.cat_var = tk.StringVar(value="0")
        self.cat_combo_frame = tk.Frame(hdr, bg=COLORS["bg_secondary"])
        self.cat_combo_frame.pack(side="right", padx=12)
        tk.Label(self.cat_combo_frame, text="الفئة:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_secondary"], font=FONTS["body_sm"]).pack(side="left")

        self.cat_menu = tk.OptionMenu(self.cat_combo_frame, self.cat_var, "0")
        self.cat_menu.config(bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                              activebackground=COLORS["accent"], activeforeground="black",
                              font=FONTS["body_sm"], bd=0, relief="flat",
                              highlightthickness=0)
        self.cat_menu["menu"].config(bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                                      activebackground=COLORS["accent"])
        self.cat_menu.pack(side="left")
        self.cat_var.trace_add("write", lambda *a: self._load_items())

        # Search
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._load_items())
        tk.Entry(hdr, textvariable=self.search_var,
                 bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                 insertbackground=COLORS["text_primary"],
                 font=FONTS["body_sm"], bd=0, relief="flat",
                 width=20).pack(side="right", padx=8, ipady=6)
        tk.Label(hdr, text="🔍", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_secondary"], font=FONTS["body_md"]).pack(side="right")

        # ── Items Table ───────────────────────────────────────────────────────
        cols = [
            {"id": "id",       "label": "#",         "width": 50,  "anchor": "center", "stretch": False},
            {"id": "name",     "label": "اسم الصنف", "width": 180, "anchor": "w"},
            {"id": "cat",      "label": "الفئة",     "width": 100, "anchor": "center"},
            {"id": "desc",     "label": "الوصف",     "width": 220, "anchor": "w"},
            {"id": "price",    "label": "السعر",     "width": 90,  "anchor": "center"},
            {"id": "cost",     "label": "التكلفة",   "width": 90,  "anchor": "center"},
            {"id": "profit",   "label": "هامش الربح","width": 90,  "anchor": "center"},
            {"id": "tax",      "label": "الضريبة",   "width": 70,  "anchor": "center"},
            {"id": "avail",    "label": "متاح",      "width": 70,  "anchor": "center"},
        ]
        self.table = DataTable(self, cols)
        self.table.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        self.table.tree.bind("<Double-1>", self._edit_item)

        # ── Action Bar ────────────────────────────────────────────────────────
        act = tk.Frame(self, bg=COLORS["bg_secondary"], padx=16, pady=10)
        act.grid(row=2, column=0, sticky="ew")

        self.count_label = tk.Label(act, text="", fg=COLORS["text_secondary"],
                                     bg=COLORS["bg_secondary"], font=FONTS["body_sm"])
        self.count_label.pack(side="left")

        tk.Button(act, text="🗑️ حذف الصنف", bg=COLORS["danger"], fg="white",
                  font=FONTS["body_sm"], bd=0, padx=12, pady=6, relief="flat",
                  cursor="hand2", command=self._delete_item).pack(side="right", padx=4)

        tk.Button(act, text="✏️ تعديل الصنف", bg=COLORS["accent"], fg="black",
                  font=FONTS["body_sm"], bd=0, padx=12, pady=6, relief="flat",
                  cursor="hand2", command=self._edit_item).pack(side="right", padx=4)

        tk.Button(act, text="🔄 تغيير التوفر", bg=COLORS["warning"], fg="black",
                  font=FONTS["body_sm"], bd=0, padx=12, pady=6, relief="flat",
                  cursor="hand2", command=self._toggle_availability).pack(side="right", padx=4)

        self._load_categories_combo()
        self._load_items()

    def _load_categories_combo(self):
        cats = db.get_categories()
        self._categories = {str(c["id"]): c for c in cats}
        menu = self.cat_menu["menu"]
        menu.delete(0, "end")
        menu.add_command(label="الكل", command=lambda: self.cat_var.set("0"))
        for c in cats:
            cid = str(c["id"])
            menu.add_command(label=f"{c['icon']} {c['name']}",
                             command=lambda v=cid: self.cat_var.set(v))

    def _load_items(self):
        self.table.clear()
        cat_id = int(self.cat_var.get()) if self.cat_var.get() != "0" else None
        items = db.get_menu_items(cat_id, available_only=False)
        search = self.search_var.get().lower()
        if search:
            items = [i for i in items if search in i["name"].lower()]
        self._items = items

        for it in items:
            margin = (it["price"] - it["cost"]) / it["price"] * 100 if it["price"] else 0
            self.table.insert_row((
                it["id"],
                it["name"],
                it.get("category_name", ""),
                (it.get("description") or "")[:40],
                f"{it['price']:.2f} ج.م",
                f"{it['cost']:.2f} ج.م",
                f"{margin:.0f}%",
                f"{it.get('tax_rate', 0)*100:.0f}%",
                "✅" if it["is_available"] else "❌",
            ))
        self.count_label.config(text=f"إجمالي الأصناف: {len(items)}")

    def _get_selected_item(self):
        sel = self.table.tree.selection()
        if not sel:
            Toast(self, "اختر صنفاً أولاً", "warning")
            return None
        idx = self.table.tree.index(sel[0])
        return self._items[idx] if idx < len(self._items) else None

    def _add_item(self):
        self._open_item_form(None)

    def _edit_item(self, event=None):
        item = self._get_selected_item()
        if item:
            self._open_item_form(item)

    def _open_item_form(self, item=None):
        cats = db.get_categories()
        win = tk.Toplevel(self)
        win.title("إضافة صنف" if not item else "تعديل صنف")
        win.config(bg=COLORS["bg_primary"])
        win.geometry("480x520")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        tk.Label(win, text="➕ بيانات الصنف" if not item else "✏️ تعديل الصنف",
                 fg=COLORS["accent"], bg=COLORS["bg_primary"],
                 font=FONTS["title_md"]).pack(pady=16)

        form = tk.Frame(win, bg=COLORS["bg_card"], padx=24, pady=20)
        form.pack(fill="both", expand=True, padx=16)
        form.columnconfigure(1, weight=1)

        def field(label, row, default="", width=28):
            tk.Label(form, text=label, fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                     font=FONTS["body_sm"]).grid(row=row, column=0, sticky="w", pady=8, padx=(0, 12))
            var = tk.StringVar(value=default)
            e = tk.Entry(form, textvariable=var, bg=COLORS["bg_hover"],
                         fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                         font=FONTS["body_md"], bd=0, relief="flat", width=width)
            e.grid(row=row, column=1, sticky="ew", pady=8, ipady=6)
            return var

        # Category
        tk.Label(form, text="الفئة:", fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                 font=FONTS["body_sm"]).grid(row=0, column=0, sticky="w", pady=8)
        cat_var = tk.StringVar(value=str(item["category_id"]) if item else str(cats[0]["id"]))
        cat_names = {str(c["id"]): f"{c['icon']} {c['name']}" for c in cats}
        cat_om = tk.OptionMenu(form, cat_var, *[str(c["id"]) for c in cats])
        cat_om.config(bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                      activebackground=COLORS["accent"], font=FONTS["body_md"],
                      bd=0, relief="flat", highlightthickness=0)
        cat_om["menu"].config(bg=COLORS["bg_hover"], fg=COLORS["text_primary"])
        for c in cats:
            cat_om["menu"].entryconfigure(cats.index(c), label=f"{c['icon']} {c['name']}")
        cat_om.grid(row=0, column=1, sticky="ew", pady=8)

        name_var  = field("اسم الصنف:*",  1, item["name"] if item else "")
        desc_var  = field("الوصف:",        2, item.get("description") or "" if item else "")
        price_var = field("السعر:*",       3, str(item["price"]) if item else "")
        cost_var  = field("التكلفة:",      4, str(item["cost"]) if item else "0")
        tax_var   = field("الضريبة (%):",  5, str(int(item.get("tax_rate", 0.14)*100)) if item else "14")

        # Available toggle
        avail_var = tk.BooleanVar(value=bool(item["is_available"]) if item else True)
        tk.Checkbutton(form, text="✅ متاح للبيع", variable=avail_var,
                       bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                       selectcolor=COLORS["accent"], activebackground=COLORS["bg_card"],
                       font=FONTS["body_md"]).grid(row=6, column=0, columnspan=2, sticky="w", pady=8)

        def save():
            name  = name_var.get().strip()
            price = price_var.get().strip()
            if not name or not price:
                Toast(win, "اسم الصنف والسعر مطلوبان", "error"); return
            try:
                price_f = float(price)
                cost_f  = float(cost_var.get() or "0")
                tax_f   = float(tax_var.get() or "14") / 100
            except ValueError:
                Toast(win, "قيم غير صحيحة", "error"); return

            data = {
                "id": item["id"] if item else None,
                "category_id": int(cat_var.get()),
                "name": name,
                "description": desc_var.get().strip() or None,
                "price": price_f,
                "cost": cost_f,
                "tax_rate": tax_f,
                "is_available": 1 if avail_var.get() else 0,
            }
            db.save_menu_item(data)
            self._load_items()
            Toast(self, "تم الحفظ بنجاح ✅", "success")
            win.destroy()

        btn_row = tk.Frame(win, bg=COLORS["bg_primary"])
        btn_row.pack(pady=12)
        tk.Button(btn_row, text="💾 حفظ", bg=COLORS["success"], fg="white",
                  font=FONTS["body_md"], bd=0, padx=24, pady=8, relief="flat",
                  cursor="hand2", command=save).pack(side="left", padx=8)
        tk.Button(btn_row, text="إلغاء", bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                  font=FONTS["body_md"], bd=0, padx=24, pady=8, relief="flat",
                  cursor="hand2", command=win.destroy).pack(side="left")

    def _delete_item(self):
        item = self._get_selected_item()
        if not item:
            return
        if messagebox.askyesno("حذف الصنف", f"حذف '{item['name']}'؟ لن يظهر في القائمة."):
            db.delete_menu_item(item["id"])
            self._load_items()
            Toast(self, "تم إخفاء الصنف", "success")

    def _toggle_availability(self):
        item = self._get_selected_item()
        if not item:
            return
        new_val = 0 if item["is_available"] else 1
        conn = db.get_connection()
        conn.execute("UPDATE menu_items SET is_available=? WHERE id=?", (new_val, item["id"]))
        conn.commit()
        conn.close()
        self._load_items()
        state = "متاح" if new_val else "غير متاح"
        Toast(self, f"'{item['name']}' أصبح {state}", "success")

    def _add_category(self):
        win = tk.Toplevel(self)
        win.title("فئة جديدة")
        win.config(bg=COLORS["bg_primary"])
        win.geometry("380x300")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        tk.Label(win, text="📂 إضافة فئة جديدة", fg=COLORS["accent"],
                 bg=COLORS["bg_primary"], font=FONTS["title_md"]).pack(pady=16)

        form = tk.Frame(win, bg=COLORS["bg_card"], padx=24, pady=20)
        form.pack(fill="both", expand=True, padx=16)

        tk.Label(form, text="اسم الفئة:*", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w")
        name_var = tk.StringVar()
        tk.Entry(form, textvariable=name_var, bg=COLORS["bg_hover"],
                 fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                 font=FONTS["body_md"], bd=0, relief="flat").pack(fill="x", ipady=8, pady=4)

        tk.Label(form, text="الأيقونة:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w", pady=(8, 0))
        icon_var = tk.StringVar(value="🍽️")
        tk.Entry(form, textvariable=icon_var, bg=COLORS["bg_hover"],
                 fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                 font=FONTS["body_md"], bd=0, relief="flat", width=6).pack(anchor="w", ipady=8)

        tk.Label(form, text="اللون (Hex):", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w", pady=(8, 0))
        color_var = tk.StringVar(value="#4A90D9")
        tk.Entry(form, textvariable=color_var, bg=COLORS["bg_hover"],
                 fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                 font=FONTS["body_md"], bd=0, relief="flat").pack(fill="x", ipady=8)

        def save():
            name = name_var.get().strip()
            if not name:
                Toast(win, "اسم الفئة مطلوب", "error"); return
            conn = db.get_connection()
            conn.execute("INSERT INTO categories (name, icon, color) VALUES (?,?,?)",
                         (name, icon_var.get(), color_var.get()))
            conn.commit()
            conn.close()
            self._load_categories_combo()
            self._load_items()
            Toast(self, f"تمت إضافة الفئة '{name}'", "success")
            win.destroy()

        tk.Button(win, text="💾 حفظ", bg=COLORS["success"], fg="white",
                  font=FONTS["body_md"], bd=0, padx=24, pady=8, relief="flat",
                  cursor="hand2", command=save).pack(pady=12)

    def on_show(self):
        self._load_categories_combo()
        self._load_items()
