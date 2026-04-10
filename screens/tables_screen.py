"""
Tables Management Screen
Visual floor plan of restaurant tables
"""
import tkinter as tk
from tkinter import messagebox
import database as db
from theme import COLORS, FONTS
from widgets import Toast


class TablesScreen(tk.Frame):

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

        tk.Label(hdr, text="🪑 إدارة الطاولات", fg=COLORS["accent"],
                 bg=COLORS["bg_secondary"], font=FONTS["title_md"]).pack(side="left")

        tk.Button(hdr, text="➕ إضافة طاولة", bg=COLORS["success"], fg="white",
                  font=FONTS["body_sm"], bd=0, padx=14, pady=7, relief="flat",
                  cursor="hand2", command=self._add_table).pack(side="right", padx=4)

        tk.Button(hdr, text="🔄 تحديث", bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                  font=FONTS["body_sm"], bd=0, padx=14, pady=7, relief="flat",
                  cursor="hand2", command=self._load_tables).pack(side="right", padx=4)

        # Legend
        legend = tk.Frame(hdr, bg=COLORS["bg_secondary"])
        legend.pack(side="right", padx=20)
        for color, label in [
            (COLORS["success"], "فارغة"),
            (COLORS["danger"],  "مشغولة"),
            (COLORS["warning"], "محجوزة"),
        ]:
            dot = tk.Frame(legend, bg=color, width=12, height=12)
            dot.pack(side="left", padx=2)
            tk.Label(legend, text=label, fg=COLORS["text_secondary"],
                     bg=COLORS["bg_secondary"], font=FONTS["body_sm"]).pack(side="left", padx=4)

        # ── Tables Grid ───────────────────────────────────────────────────────
        canvas = tk.Canvas(self, bg=COLORS["bg_primary"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        self.grid_frame = tk.Frame(canvas, bg=COLORS["bg_primary"])
        self._canvas_window = canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.grid_frame.bind("<Configure>",
                              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(self._canvas_window, width=e.width))

        # ── Stats Bar ─────────────────────────────────────────────────────────
        self.stats_bar = tk.Frame(self, bg=COLORS["bg_card"], padx=16, pady=10)
        self.stats_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.stats_label = tk.Label(self.stats_bar, text="",
                                    fg=COLORS["text_secondary"],
                                    bg=COLORS["bg_card"], font=FONTS["body_sm"])
        self.stats_label.pack(side="left")

        self._load_tables()

    def _load_tables(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        tables = db.get_tables()
        self._tables = tables

        COLS = 5
        status_colors = {
            "free":     COLORS["success"],
            "occupied": COLORS["danger"],
            "reserved": COLORS["warning"],
        }
        status_labels = {
            "free":     "فارغة",
            "occupied": "مشغولة",
            "reserved": "محجوزة",
        }
        status_icons = {"free": "✅", "occupied": "⛔", "reserved": "🔒"}

        free = sum(1 for t in tables if t["status"] == "free")
        occupied = sum(1 for t in tables if t["status"] == "occupied")
        reserved = sum(1 for t in tables if t["status"] == "reserved")
        self.stats_label.config(
            text=f"الكل: {len(tables)}  |  فارغة: {free}  |  مشغولة: {occupied}  |  محجوزة: {reserved}"
        )

        for idx, t in enumerate(tables):
            row, col = divmod(idx, COLS)
            color = status_colors.get(t["status"], COLORS["text_muted"])

            card = tk.Frame(self.grid_frame, bg=COLORS["bg_card"],
                            bd=0, highlightthickness=2, highlightbackground=color,
                            cursor="hand2", width=150, height=130)
            card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
            card.grid_propagate(False)
            self.grid_frame.columnconfigure(col, weight=1)

            # Top accent
            tk.Frame(card, bg=color, height=5).pack(fill="x")

            inner = tk.Frame(card, bg=COLORS["bg_card"], padx=10, pady=10)
            inner.pack(fill="both", expand=True)

            tk.Label(inner, text=f"🪑 طاولة {t['number']}",
                     fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                     font=FONTS["title_sm"]).pack(pady=(4, 0))

            tk.Label(inner, text=f"سعة: {t['capacity']} أشخاص",
                     fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                     font=FONTS["body_sm"]).pack()

            status_row = tk.Frame(inner, bg=COLORS["bg_card"])
            status_row.pack(pady=(6, 0))
            tk.Label(status_row,
                     text=f"{status_icons.get(t['status'], '')} {status_labels.get(t['status'], t['status'])}",
                     fg=color, bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(side="left")

            # Bind click
            for widget in [card, inner] + inner.winfo_children() + [status_row] + status_row.winfo_children():
                widget.bind("<Button-1>", lambda e, tbl=t: self._table_action(tbl))
            card.bind("<Button-3>", lambda e, tbl=t: self._show_context_menu(e, tbl))

    def _table_action(self, table):
        """Show quick action popup for a table."""
        win = tk.Toplevel(self)
        win.title(f"طاولة {table['number']}")
        win.config(bg=COLORS["bg_primary"])
        win.geometry("280x260")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        status_colors = {"free": COLORS["success"], "occupied": COLORS["danger"], "reserved": COLORS["warning"]}
        color = status_colors.get(table["status"], COLORS["text_muted"])

        tk.Label(win, text=f"🪑 طاولة {table['number']}",
                 fg=COLORS["accent"], bg=COLORS["bg_primary"],
                 font=FONTS["title_md"]).pack(pady=12)

        for label, status, bg in [
            ("✅ تحديد كـ: فارغة",   "free",     COLORS["success"]),
            ("⛔ تحديد كـ: مشغولة", "occupied", COLORS["danger"]),
            ("🔒 تحديد كـ: محجوزة", "reserved", COLORS["warning"]),
        ]:
            tk.Button(win, text=label, bg=bg,
                      fg="white" if bg != COLORS["warning"] else "black",
                      font=FONTS["body_md"], bd=0, pady=9, relief="flat", cursor="hand2",
                      command=lambda s=status, w=win: self._set_status(table, s, w)
                      ).pack(fill="x", padx=20, pady=4)

        if table["status"] == "free":
            tk.Button(win, text="🛒 فتح طلب جديد", bg=COLORS["info"], fg="white",
                      font=FONTS["body_md"], bd=0, pady=9, relief="flat", cursor="hand2",
                      command=lambda w=win: self._open_order_for_table(table, w)
                      ).pack(fill="x", padx=20, pady=4)

        tk.Button(win, text="إغلاق", bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                  font=FONTS["body_sm"], bd=0, pady=6, relief="flat",
                  cursor="hand2", command=win.destroy).pack(pady=8)

    def _set_status(self, table, status, win):
        db.update_table_status(table["id"], status)
        self._load_tables()
        win.destroy()
        Toast(self, f"طاولة {table['number']} → {status}", "success")

    def _open_order_for_table(self, table, win):
        win.destroy()
        cashier = self.app.screens["cashier"]
        cashier.new_order()
        cashier.selected_table = table
        cashier.table_btn.config(text=f"🪑 {table['number']}")
        cashier.order_type.set("dine_in")
        self.app.show_screen("cashier")

    def _show_context_menu(self, event, table):
        menu = tk.Menu(self, tearoff=0, bg=COLORS["bg_card"],
                       fg=COLORS["text_primary"], activebackground=COLORS["accent"],
                       activeforeground="black", font=FONTS["body_sm"])
        menu.add_command(label="✅ فارغة",   command=lambda: (db.update_table_status(table["id"], "free"),    self._load_tables()))
        menu.add_command(label="⛔ مشغولة", command=lambda: (db.update_table_status(table["id"], "occupied"), self._load_tables()))
        menu.add_command(label="🔒 محجوزة", command=lambda: (db.update_table_status(table["id"], "reserved"), self._load_tables()))
        menu.add_separator()
        menu.add_command(label="🗑️ حذف الطاولة", command=lambda: self._delete_table(table))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _add_table(self):
        win = tk.Toplevel(self)
        win.title("إضافة طاولة")
        win.config(bg=COLORS["bg_primary"])
        win.geometry("340x220")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        tk.Label(win, text="➕ طاولة جديدة", fg=COLORS["accent"],
                 bg=COLORS["bg_primary"], font=FONTS["title_md"]).pack(pady=14)

        form = tk.Frame(win, bg=COLORS["bg_card"], padx=24, pady=16)
        form.pack(fill="x", padx=16)

        tk.Label(form, text="رقم / اسم الطاولة:*", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w")
        num_var = tk.StringVar()
        tk.Entry(form, textvariable=num_var, bg=COLORS["bg_hover"],
                 fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                 font=FONTS["body_md"], bd=0, relief="flat").pack(fill="x", ipady=8, pady=4)

        tk.Label(form, text="عدد المقاعد:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w", pady=(8, 0))
        cap_var = tk.StringVar(value="4")
        tk.Entry(form, textvariable=cap_var, bg=COLORS["bg_hover"],
                 fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                 font=FONTS["body_md"], bd=0, relief="flat", width=8).pack(anchor="w", ipady=8)

        def save():
            num = num_var.get().strip()
            if not num:
                Toast(win, "رقم الطاولة مطلوب", "error"); return
            try:
                cap = int(cap_var.get())
            except ValueError:
                cap = 4
            conn = db.get_connection()
            conn.execute("INSERT INTO restaurant_tables (number, capacity) VALUES (?,?)", (num, cap))
            conn.commit()
            conn.close()
            self._load_tables()
            Toast(self, f"تمت إضافة طاولة {num}", "success")
            win.destroy()

        tk.Button(win, text="💾 حفظ", bg=COLORS["success"], fg="white",
                  font=FONTS["body_md"], bd=0, padx=24, pady=8, relief="flat",
                  cursor="hand2", command=save).pack(pady=12)

    def _delete_table(self, table):
        if table["status"] == "occupied":
            Toast(self, "لا يمكن حذف طاولة مشغولة", "error"); return
        if messagebox.askyesno("حذف", f"حذف طاولة {table['number']}؟"):
            conn = db.get_connection()
            conn.execute("DELETE FROM restaurant_tables WHERE id=?", (table["id"],))
            conn.commit()
            conn.close()
            self._load_tables()
            Toast(self, "تم الحذف", "success")

    def on_show(self):
        self._load_tables()
