"""
Settings Screen
User management, restaurant info, and system configuration
"""
import tkinter as tk
from tkinter import messagebox
import database as db
from theme import COLORS, FONTS
from widgets import DataTable, Toast


class SettingsScreen(tk.Frame):

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=COLORS["bg_primary"], **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # ── Header ────────────────────────────────────────────────────────────
        top = tk.Frame(self, bg=COLORS["bg_secondary"], padx=16, pady=12)
        top.grid(row=0, column=0, sticky="ew")

        tk.Label(top, text="⚙️ الإعدادات",
                 fg=COLORS["accent"], bg=COLORS["bg_secondary"],
                 font=FONTS["title_md"]).pack(side="left")

        # ── Tabs ──────────────────────────────────────────────────────────────
        tab_bar = tk.Frame(self, bg=COLORS["bg_secondary"])
        tab_bar.grid(row=1, column=0, sticky="ew")

        self.tab_content = tk.Frame(self, bg=COLORS["bg_primary"])
        self.tab_content.grid(row=2, column=0, sticky="nsew")
        self.rowconfigure(2, weight=1)

        self._tabs = {}
        self._active_tab = None
        for key, label in [("users", "👥 المستخدمون"),
                             ("restaurant", "🍽️ بيانات المطعم"),
                             ("tables", "🪑 الطاولات"),
                             ("backup", "💾 النسخ الاحتياطي")]:
            btn = tk.Button(tab_bar, text=label,
                            bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                            font=FONTS["body_sm"], bd=0, padx=20, pady=10,
                            relief="flat", cursor="hand2",
                            command=lambda k=key: self._show_tab(k))
            btn.pack(side="left", padx=2, pady=6)
            self._tabs[key] = btn

        self._show_tab("users")

    def _show_tab(self, key):
        # Reset all tab colors
        for k, btn in self._tabs.items():
            btn.config(bg=COLORS["bg_card"] if k != key else COLORS["accent"],
                       fg=COLORS["text_secondary"] if k != key else "#000000")

        for w in self.tab_content.winfo_children():
            w.destroy()

        self._active_tab = key
        if key == "users":
            self._build_users_tab()
        elif key == "restaurant":
            self._build_restaurant_tab()
        elif key == "tables":
            self._build_tables_tab()
        elif key == "backup":
            self._build_backup_tab()

    # ── Users Tab ─────────────────────────────────────────────────────────────
    def _build_users_tab(self):
        f = self.tab_content
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)

        # Action bar
        abar = tk.Frame(f, bg=COLORS["bg_secondary"], padx=16, pady=10)
        abar.grid(row=0, column=0, sticky="ew")

        tk.Label(abar, text="إدارة المستخدمين", fg=COLORS["text_primary"],
                 bg=COLORS["bg_secondary"], font=FONTS["title_sm"]).pack(side="left")

        tk.Button(abar, text="➕ مستخدم جديد",
                  bg=COLORS["success"], fg="white",
                  font=FONTS["body_sm"], bd=0, padx=14, pady=7,
                  relief="flat", cursor="hand2",
                  command=self._add_user).pack(side="right", padx=4)

        tk.Button(abar, text="✏️ تعديل",
                  bg=COLORS["accent"], fg="black",
                  font=FONTS["body_sm"], bd=0, padx=14, pady=7,
                  relief="flat", cursor="hand2",
                  command=self._edit_user).pack(side="right", padx=4)

        tk.Button(abar, text="🔒 تفعيل / تعطيل",
                  bg=COLORS["warning"], fg="black",
                  font=FONTS["body_sm"], bd=0, padx=14, pady=7,
                  relief="flat", cursor="hand2",
                  command=self._toggle_user).pack(side="right", padx=4)

        # Table
        cols = [
            {"id": "id",       "label": "ID",          "width": 40,  "anchor": "center"},
            {"id": "username", "label": "اسم المستخدم","width": 140, "anchor": "w"},
            {"id": "name",     "label": "الاسم الكامل","width": 180, "anchor": "w"},
            {"id": "role",     "label": "الدور",       "width": 100, "anchor": "center"},
            {"id": "active",   "label": "الحالة",      "width": 80,  "anchor": "center"},
            {"id": "created",  "label": "تاريخ الإنشاء","width": 130,"anchor": "center"},
        ]
        self.users_table = DataTable(f, cols)
        self.users_table.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        self.users_table.tree.bind("<Double-1>", lambda e: self._edit_user())
        self._load_users()

    def _load_users(self):
        self.users_table.clear()
        users = db.get_users()
        self._users = users
        role_map = {"admin": "مدير", "manager": "مشرف", "cashier": "كاشير"}
        for u in users:
            self.users_table.insert_row((
                u["id"],
                u["username"],
                u["full_name"],
                role_map.get(u["role"], u["role"]),
                "✅ نشط" if u["is_active"] else "❌ معطل",
                u["created_at"][:10],
            ))

    def _get_selected_user(self):
        sel = self.users_table.tree.selection()
        if not sel:
            Toast(self, "اختر مستخدماً أولاً", "warning")
            return None
        idx = self.users_table.tree.index(sel[0])
        return self._users[idx] if idx < len(self._users) else None

    def _add_user(self):
        self._user_form(None)

    def _edit_user(self):
        user = self._get_selected_user()
        if user:
            self._user_form(user)

    def _user_form(self, user=None):
        win = tk.Toplevel(self)
        win.title("إضافة مستخدم" if not user else f"تعديل: {user['username']}")
        win.config(bg=COLORS["bg_primary"])
        win.geometry("440x500")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        tk.Label(win, text="👤 " + ("مستخدم جديد" if not user else f"تعديل {user['full_name']}"),
                 fg=COLORS["accent"], bg=COLORS["bg_primary"],
                 font=FONTS["title_md"]).pack(pady=16)

        form = tk.Frame(win, bg=COLORS["bg_card"], padx=24, pady=20)
        form.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        def field(lbl, default="", password=False):
            tk.Label(form, text=lbl, fg=COLORS["text_secondary"],
                     bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w", pady=(8, 2))
            var = tk.StringVar(value=str(default))
            show = "●" if password else ""
            e = tk.Entry(form, textvariable=var, show=show,
                         bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                         insertbackground=COLORS["text_primary"],
                         font=FONTS["body_md"], bd=0, relief="flat", justify="right")
            e.pack(fill="x", ipady=7)
            return var

        v_username = field("اسم المستخدم",  user["username"]  if user else "")
        v_fullname = field("الاسم الكامل",  user["full_name"] if user else "")
        v_password = field("كلمة المرور (اتركها فارغة للإبقاء)", "", password=True)

        tk.Label(form, text="الدور:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w", pady=(8, 4))
        role_var = tk.StringVar(value=user["role"] if user else "cashier")
        role_frame = tk.Frame(form, bg=COLORS["bg_card"])
        role_frame.pack(anchor="w")
        for val, lbl in [("admin", "مدير"), ("manager", "مشرف"), ("cashier", "كاشير")]:
            tk.Radiobutton(role_frame, text=lbl, variable=role_var, value=val,
                           bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                           selectcolor=COLORS["accent"], font=FONTS["body_sm"],
                           activebackground=COLORS["bg_card"]).pack(side="left", padx=8)

        active_var = tk.BooleanVar(value=bool(user["is_active"]) if user else True)
        tk.Checkbutton(form, text="مستخدم نشط", variable=active_var,
                       bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                       selectcolor=COLORS["accent"], font=FONTS["body_sm"],
                       activebackground=COLORS["bg_card"]).pack(anchor="w", pady=(12, 0))

        def save():
            data = {
                "id":        user["id"] if user else None,
                "username":  v_username.get().strip(),
                "full_name": v_fullname.get().strip(),
                "role":      role_var.get(),
                "is_active": 1 if active_var.get() else 0,
            }
            if v_password.get():
                data["password"] = v_password.get()
            elif not user:
                Toast(win, "أدخل كلمة مرور للمستخدم الجديد", "warning")
                return
            if not data["username"] or not data["full_name"]:
                Toast(win, "أدخل اسم المستخدم والاسم الكامل", "warning")
                return
            try:
                db.save_user(data)
                win.destroy()
                self._load_users()
                Toast(self, "تم الحفظ بنجاح", "success")
            except Exception as e:
                Toast(win, f"خطأ: {e}", "error")

        tk.Button(form, text="💾 حفظ",
                  bg=COLORS["success"], fg="white",
                  font=FONTS["title_sm"], bd=0, pady=10, relief="flat",
                  cursor="hand2", command=save).pack(fill="x", pady=(16, 0))

    def _toggle_user(self):
        user = self._get_selected_user()
        if not user:
            return
        if user["id"] == self.app.current_user["id"]:
            Toast(self, "لا يمكن تعطيل حسابك الحالي", "warning")
            return
        new_state = 0 if user["is_active"] else 1
        action = "تعطيل" if not new_state else "تفعيل"
        if messagebox.askyesno("تأكيد", f"{action} المستخدم {user['username']}؟"):
            conn = db.get_connection()
            conn.execute("UPDATE users SET is_active=? WHERE id=?", (new_state, user["id"]))
            conn.commit()
            conn.close()
            self._load_users()
            Toast(self, f"تم {action} المستخدم", "success")

    # ── Restaurant Tab ────────────────────────────────────────────────────────
    def _build_restaurant_tab(self):
        f = self.tab_content
        f.columnconfigure(0, weight=1)

        tk.Label(f, text="🍽️ بيانات المطعم", fg=COLORS["accent"],
                 bg=COLORS["bg_primary"], font=FONTS["title_md"]).pack(pady=16)

        form = tk.Frame(f, bg=COLORS["bg_card"], padx=32, pady=24)
        form.pack(padx=40, fill="x")

        fields_data = [
            ("اسم المطعم",          "مطعم الأصالة"),
            ("العنوان",             "القاهرة، مصر"),
            ("رقم الهاتف",          "01000000000"),
            ("الرقم الضريبي",       "123456789"),
            ("نسبة الضريبة الافتراضية (%)","14"),
            ("رسالة الإيصال",       "شكراً لزيارتكم ❤️"),
        ]

        self._rest_vars = {}
        for label, default in fields_data:
            tk.Label(form, text=label + ":", fg=COLORS["text_secondary"],
                     bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w", pady=(10, 2))
            var = tk.StringVar(value=default)
            tk.Entry(form, textvariable=var,
                     bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                     insertbackground=COLORS["text_primary"],
                     font=FONTS["body_md"], bd=0, relief="flat", justify="right").pack(
                     fill="x", ipady=8)
            self._rest_vars[label] = var

        tk.Button(form, text="💾 حفظ الإعدادات",
                  bg=COLORS["success"], fg="white",
                  font=FONTS["title_sm"], bd=0, pady=10, relief="flat",
                  cursor="hand2",
                  command=lambda: Toast(self, "تم حفظ إعدادات المطعم ✅", "success")).pack(
                  fill="x", pady=(20, 0))

    # ── Tables Tab ────────────────────────────────────────────────────────────
    def _build_tables_tab(self):
        f = self.tab_content
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)

        abar = tk.Frame(f, bg=COLORS["bg_secondary"], padx=16, pady=10)
        abar.grid(row=0, column=0, sticky="ew")

        tk.Label(abar, text="🪑 إدارة الطاولات",
                 fg=COLORS["text_primary"], bg=COLORS["bg_secondary"],
                 font=FONTS["title_sm"]).pack(side="left")

        tk.Button(abar, text="➕ إضافة طاولة",
                  bg=COLORS["success"], fg="white",
                  font=FONTS["body_sm"], bd=0, padx=14, pady=7,
                  relief="flat", cursor="hand2",
                  command=self._add_table).pack(side="right", padx=4)

        cols = [
            {"id": "id",       "label": "ID",       "width": 50,  "anchor": "center"},
            {"id": "number",   "label": "رقم الطاولة","width": 120,"anchor": "center"},
            {"id": "capacity", "label": "السعة",    "width": 80,  "anchor": "center"},
            {"id": "status",   "label": "الحالة",   "width": 100, "anchor": "center"},
        ]
        self.tables_table = DataTable(f, cols)
        self.tables_table.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        self._load_tables()

    def _load_tables(self):
        self.tables_table.clear()
        tables = db.get_tables()
        self._tables_list = tables
        status_map = {"free": "فارغة ✅", "occupied": "مشغولة 🔴", "reserved": "محجوزة 🟡"}
        for t in tables:
            self.tables_table.insert_row((
                t["id"], t["number"], t["capacity"],
                status_map.get(t["status"], t["status"])
            ))

    def _add_table(self):
        win = tk.Toplevel(self)
        win.title("إضافة طاولة")
        win.config(bg=COLORS["bg_primary"])
        win.geometry("360x260")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        tk.Label(win, text="🪑 طاولة جديدة", fg=COLORS["accent"],
                 bg=COLORS["bg_primary"], font=FONTS["title_md"]).pack(pady=16)

        form = tk.Frame(win, bg=COLORS["bg_card"], padx=24, pady=20)
        form.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        tk.Label(form, text="رقم / اسم الطاولة:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w")
        num_var = tk.StringVar()
        tk.Entry(form, textvariable=num_var, bg=COLORS["bg_hover"],
                 fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                 font=FONTS["body_md"], bd=0, relief="flat", justify="center").pack(
                 fill="x", ipady=8, pady=(4, 12))

        tk.Label(form, text="السعة (عدد الأشخاص):", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w")
        cap_var = tk.StringVar(value="4")
        tk.Entry(form, textvariable=cap_var, bg=COLORS["bg_hover"],
                 fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                 font=FONTS["body_md"], bd=0, relief="flat", justify="center").pack(
                 fill="x", ipady=8, pady=(4, 16))

        def save():
            num = num_var.get().strip()
            if not num:
                Toast(win, "أدخل رقم الطاولة", "warning")
                return
            try:
                cap = int(cap_var.get() or 4)
                conn = db.get_connection()
                conn.execute("INSERT INTO restaurant_tables (number, capacity) VALUES (?,?)",
                             (num, cap))
                conn.commit()
                conn.close()
                win.destroy()
                self._load_tables()
                Toast(self, f"تمت إضافة الطاولة {num}", "success")
            except Exception as e:
                Toast(win, f"خطأ: {e}", "error")

        tk.Button(form, text="➕ إضافة", bg=COLORS["success"], fg="white",
                  font=FONTS["title_sm"], bd=0, pady=10, relief="flat",
                  cursor="hand2", command=save).pack(fill="x")

    # ── Backup Tab ────────────────────────────────────────────────────────────
    def _build_backup_tab(self):
        import os
        f = self.tab_content
        f.columnconfigure(0, weight=1)

        tk.Label(f, text="💾 النسخ الاحتياطي والاسترجاع",
                 fg=COLORS["accent"], bg=COLORS["bg_primary"],
                 font=FONTS["title_md"]).pack(pady=20)

        card = tk.Frame(f, bg=COLORS["bg_card"], padx=32, pady=24)
        card.pack(padx=40, fill="x")

        db_path = db.DB_PATH
        size_kb = os.path.getsize(db_path) // 1024 if os.path.exists(db_path) else 0

        tk.Label(card, text=f"📂 ملف قاعدة البيانات: {db_path}",
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                 font=FONTS["body_sm"], wraplength=500).pack(anchor="w")
        tk.Label(card, text=f"📏 الحجم: {size_kb} KB",
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                 font=FONTS["body_sm"]).pack(anchor="w", pady=(4, 16))

        def backup():
            from tkinter import filedialog
            import shutil
            target = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database", "*.db")],
                initialfile=f"backup_{datetime_str()}.db"
            )
            if target:
                shutil.copy2(db_path, target)
                Toast(self, "تم عمل النسخة الاحتياطية ✅", "success")

        def restore():
            from tkinter import filedialog
            import shutil
            src = filedialog.askopenfilename(filetypes=[("Database", "*.db")])
            if src and messagebox.askyesno("تأكيد", "سيتم استبدال قاعدة البيانات الحالية. هل أنت متأكد؟"):
                shutil.copy2(src, db_path)
                Toast(self, "تم الاسترجاع. أعد تشغيل البرنامج.", "success")

        tk.Button(card, text="📤 نسخ احتياطي",
                  bg=COLORS["info"], fg="white",
                  font=FONTS["title_sm"], bd=0, pady=12, relief="flat",
                  cursor="hand2", command=backup).pack(fill="x", pady=(0, 8))

        tk.Button(card, text="📥 استرجاع نسخة",
                  bg=COLORS["warning"], fg="black",
                  font=FONTS["title_sm"], bd=0, pady=12, relief="flat",
                  cursor="hand2", command=restore).pack(fill="x")

        tk.Label(card,
                 text="⚠️ تحذير: الاسترجاع سيحذف جميع البيانات الحالية ويستبدلها بالنسخة المختارة.",
                 fg=COLORS["warning"], bg=COLORS["bg_card"], font=FONTS["body_sm"],
                 wraplength=480).pack(anchor="w", pady=(16, 0))

    def on_show(self):
        if self._active_tab:
            self._show_tab(self._active_tab)


def datetime_str():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


from datetime import datetime
