"""
Inventory Management Screen
Track stock levels, low-stock alerts, and transactions
"""
import tkinter as tk
from tkinter import messagebox
import database as db
from theme import COLORS, FONTS
from widgets import DataTable, Toast


class InventoryScreen(tk.Frame):

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=COLORS["bg_primary"], **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # ── Top Bar ───────────────────────────────────────────────────────────
        top = tk.Frame(self, bg=COLORS["bg_secondary"], padx=16, pady=12)
        top.grid(row=0, column=0, sticky="ew")

        tk.Label(top, text="📦 إدارة المخزون",
                 fg=COLORS["accent"], bg=COLORS["bg_secondary"],
                 font=FONTS["title_md"]).pack(side="left")

        tk.Button(top, text="➕ إضافة صنف",
                  bg=COLORS["success"], fg="white",
                  font=FONTS["body_sm"], bd=0, padx=14, pady=7,
                  relief="flat", cursor="hand2",
                  command=self._add_item).pack(side="right", padx=4)

        tk.Button(top, text="⬆️ إضافة كمية",
                  bg=COLORS["info"], fg="white",
                  font=FONTS["body_sm"], bd=0, padx=14, pady=7,
                  relief="flat", cursor="hand2",
                  command=self._stock_in).pack(side="right", padx=4)

        tk.Button(top, text="⬇️ سحب كمية",
                  bg=COLORS["warning"], fg="black",
                  font=FONTS["body_sm"], bd=0, padx=14, pady=7,
                  relief="flat", cursor="hand2",
                  command=self._stock_out).pack(side="right", padx=4)

        # Search
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._load())
        search = tk.Entry(top, textvariable=self.search_var,
                          bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                          insertbackground=COLORS["text_primary"],
                          font=FONTS["body_sm"], bd=0, relief="flat", width=20)
        search.pack(side="right", padx=12, ipady=6)
        tk.Label(top, text="🔍", fg=COLORS["text_muted"],
                 bg=COLORS["bg_secondary"], font=FONTS["body_md"]).pack(side="right")

        # ── Summary Cards ─────────────────────────────────────────────────────
        summary = tk.Frame(self, bg=COLORS["bg_primary"], padx=16, pady=8)
        summary.grid(row=1, column=0, sticky="ew")

        self.card_total   = self._stat_card(summary, "إجمالي الأصناف", "—", "📦", COLORS["info"])
        self.card_low     = self._stat_card(summary, "أصناف منخفضة",  "—", "⚠️",  COLORS["warning"])
        self.card_out     = self._stat_card(summary, "نفذ من المخزن",  "—", "❌",  COLORS["danger"])
        self.card_value   = self._stat_card(summary, "قيمة المخزون",   "—", "💰",  COLORS["success"])

        for i, c in enumerate([self.card_total, self.card_low, self.card_out, self.card_value]):
            c.grid(row=0, column=i, sticky="ew", padx=6)
        summary.columnconfigure((0, 1, 2, 3), weight=1)

        # ── Table ─────────────────────────────────────────────────────────────
        cols = [
            {"id": "name",     "label": "اسم الصنف",       "width": 200, "anchor": "w"},
            {"id": "category", "label": "الفئة",            "width": 100, "anchor": "center"},
            {"id": "qty",      "label": "الكمية",           "width": 80,  "anchor": "center"},
            {"id": "unit",     "label": "الوحدة",           "width": 70,  "anchor": "center"},
            {"id": "min",      "label": "الحد الأدنى",      "width": 90,  "anchor": "center"},
            {"id": "cost",     "label": "تكلفة / وحدة",     "width": 100, "anchor": "center"},
            {"id": "total_val","label": "القيمة الإجمالية", "width": 120, "anchor": "center"},
            {"id": "status",   "label": "الحالة",           "width": 90,  "anchor": "center"},
        ]
        self.table = DataTable(self, cols)
        self.table.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 8))
        self.rowconfigure(2, weight=1)
        self.table.tree.bind("<Double-1>", lambda e: self._edit_item())

        # ── Action Bar ────────────────────────────────────────────────────────
        action = tk.Frame(self, bg=COLORS["bg_secondary"], padx=16, pady=8)
        action.grid(row=3, column=0, sticky="ew")

        self.status_label = tk.Label(action, text="",
                                      fg=COLORS["text_secondary"],
                                      bg=COLORS["bg_secondary"], font=FONTS["body_sm"])
        self.status_label.pack(side="left")

        tk.Button(action, text="✏️ تعديل", bg=COLORS["accent"], fg="black",
                  font=FONTS["body_sm"], bd=0, padx=12, pady=6, relief="flat",
                  cursor="hand2", command=self._edit_item).pack(side="right", padx=4)

        self._load()

    def _stat_card(self, parent, title, value, icon, color):
        f = tk.Frame(parent, bg=COLORS["bg_card"], bd=0,
                     highlightthickness=1, highlightbackground=COLORS["border"],
                     padx=16, pady=12)
        accent = tk.Frame(f, bg=color, width=4)
        accent.pack(side="left", fill="y")
        body = tk.Frame(f, bg=COLORS["bg_card"], padx=12)
        body.pack(side="left", fill="both", expand=True)
        tk.Label(body, text=f"{icon} {title}", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w")
        f.val_lbl = tk.Label(body, text=value, fg=color,
                              bg=COLORS["bg_card"], font=FONTS["title_md"])
        f.val_lbl.pack(anchor="w", pady=(4, 0))
        return f

    def _load(self):
        self.table.clear()
        items = db.get_inventory()
        search = self.search_var.get().lower()
        if search:
            items = [i for i in items if search in i["name"].lower()]

        total_val = 0
        low_count = 0
        out_count = 0

        for item in items:
            qty   = item["quantity"]
            min_q = item["min_quantity"]
            val   = qty * item["cost_per_unit"]
            total_val += val

            if qty <= 0:
                status = "نفذ ❌"
                out_count += 1
                low_count += 1
            elif qty <= min_q:
                status = "منخفض ⚠️"
                low_count += 1
            else:
                status = "جيد ✅"

            self.table.insert_row((
                item["name"],
                item["category"],
                f"{qty:.1f}",
                item["unit"],
                f"{min_q:.1f}",
                f"{item['cost_per_unit']:.2f} ج.م",
                f"{val:.2f} ج.م",
                status,
            ))

        # Update stat cards
        all_items = db.get_inventory()
        self.card_total.val_lbl.config(text=str(len(all_items)))
        self.card_low.val_lbl.config(text=str(low_count))
        self.card_out.val_lbl.config(text=str(out_count))
        self.card_value.val_lbl.config(text=f"{total_val:.0f} ج.م")
        self.status_label.config(text=f"{len(items)} صنف")
        self._items = items

    def _get_selected(self):
        sel = self.table.tree.selection()
        if not sel:
            Toast(self, "اختر صنفاً أولاً", "warning")
            return None
        idx = self.table.tree.index(sel[0])
        all_items = db.get_inventory()
        if idx < len(all_items):
            return all_items[idx]
        return None

    def _add_item(self):
        self._item_form(None)

    def _edit_item(self):
        item = self._get_selected()
        if item:
            self._item_form(item)

    def _item_form(self, item=None):
        win = tk.Toplevel(self)
        win.title("إضافة صنف" if not item else "تعديل صنف")
        win.config(bg=COLORS["bg_primary"])
        win.geometry("440x480")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        title = "➕ إضافة صنف جديد" if not item else f"✏️ تعديل: {item['name']}"
        tk.Label(win, text=title, fg=COLORS["accent"],
                 bg=COLORS["bg_primary"], font=FONTS["title_md"]).pack(pady=16)

        form = tk.Frame(win, bg=COLORS["bg_card"], padx=24, pady=20)
        form.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        def field(parent, label, default=""):
            tk.Label(parent, text=label, fg=COLORS["text_secondary"],
                     bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w", pady=(8, 2))
            var = tk.StringVar(value=str(default))
            e = tk.Entry(parent, textvariable=var, bg=COLORS["bg_hover"],
                         fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                         font=FONTS["body_md"], bd=0, relief="flat", justify="right")
            e.pack(fill="x", ipady=7, padx=0)
            return var

        v_name  = field(form, "اسم الصنف",   item["name"]          if item else "")
        v_cat   = field(form, "الفئة",        item["category"]      if item else "عام")
        v_unit  = field(form, "الوحدة",       item["unit"]          if item else "كيلو")
        v_qty   = field(form, "الكمية الحالية", item["quantity"]    if item else "0")
        v_min   = field(form, "الحد الأدنى",  item["min_quantity"]  if item else "0")
        v_cost  = field(form, "تكلفة / وحدة", item["cost_per_unit"] if item else "0")

        def save():
            try:
                data = {
                    "id":           item["id"] if item else None,
                    "name":         v_name.get().strip(),
                    "category":     v_cat.get().strip() or "عام",
                    "unit":         v_unit.get().strip() or "كيلو",
                    "quantity":     float(v_qty.get() or 0),
                    "min_quantity": float(v_min.get() or 0),
                    "cost_per_unit":float(v_cost.get() or 0),
                }
                if not data["name"]:
                    Toast(win, "أدخل اسم الصنف", "warning")
                    return
                db.save_inventory_item(data)
                win.destroy()
                self._load()
                Toast(self, "تم الحفظ بنجاح", "success")
            except ValueError:
                Toast(win, "تحقق من القيم العددية", "error")

        tk.Button(form, text="💾 حفظ", bg=COLORS["success"], fg="white",
                  font=FONTS["title_sm"], bd=0, pady=10, relief="flat",
                  cursor="hand2", command=save).pack(fill="x", pady=(16, 0))

    def _stock_in(self):
        self._stock_movement("in")

    def _stock_out(self):
        self._stock_movement("out")

    def _stock_movement(self, direction):
        item = self._get_selected()
        if not item:
            return

        win = tk.Toplevel(self)
        title = f"⬆️ إضافة كمية: {item['name']}" if direction == "in" else f"⬇️ سحب كمية: {item['name']}"
        win.title(title)
        win.config(bg=COLORS["bg_primary"])
        win.geometry("380x280")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        tk.Label(win, text=title, fg=COLORS["accent"],
                 bg=COLORS["bg_primary"], font=FONTS["title_sm"]).pack(pady=16)

        form = tk.Frame(win, bg=COLORS["bg_card"], padx=24, pady=20)
        form.pack(fill="both", expand=True, padx=16)

        tk.Label(form, text=f"الكمية الحالية: {item['quantity']} {item['unit']}",
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                 font=FONTS["body_md"]).pack(anchor="w", pady=(0, 12))

        tk.Label(form, text="الكمية:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w")

        qty_var = tk.StringVar(value="1")
        tk.Entry(form, textvariable=qty_var, bg=COLORS["bg_hover"],
                 fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                 font=FONTS["title_md"], bd=0, relief="flat", justify="center").pack(
                 fill="x", ipady=10, pady=(4, 12))

        tk.Label(form, text="ملاحظة:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w")
        notes_var = tk.StringVar()
        tk.Entry(form, textvariable=notes_var, bg=COLORS["bg_hover"],
                 fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                 font=FONTS["body_sm"], bd=0, relief="flat", justify="right").pack(
                 fill="x", ipady=6, pady=(4, 16))

        def do_movement():
            try:
                qty = float(qty_var.get() or 0)
                if qty <= 0:
                    Toast(win, "أدخل كمية أكبر من صفر", "warning")
                    return
                if direction == "out" and qty > item["quantity"]:
                    Toast(win, "الكمية المسحوبة أكبر من المخزون!", "error")
                    return
                conn = db.get_connection()
                new_qty = item["quantity"] + qty if direction == "in" else item["quantity"] - qty
                conn.execute("UPDATE inventory SET quantity=?, updated_at=datetime('now') WHERE id=?",
                             (new_qty, item["id"]))
                conn.execute("""
                    INSERT INTO inventory_transactions (inventory_id, type, quantity, notes, user_id)
                    VALUES (?,?,?,?,?)
                """, (item["id"], direction, qty, notes_var.get(), 1))
                conn.commit()
                conn.close()
                win.destroy()
                self._load()
                Toast(self, f"تم {'إضافة' if direction == 'in' else 'سحب'} {qty} {item['unit']}", "success")
            except ValueError:
                Toast(win, "أدخل قيمة صحيحة", "error")

        color = COLORS["info"] if direction == "in" else COLORS["warning"]
        tk.Button(form, text="✅ تأكيد", bg=color, fg="black" if direction == "out" else "white",
                  font=FONTS["title_sm"], bd=0, pady=10, relief="flat",
                  cursor="hand2", command=do_movement).pack(fill="x")

    def on_show(self):
        self._load()
