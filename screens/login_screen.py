"""
Login Screen - Restaurant ERP
Animated premium login with role-based access
"""
import tkinter as tk
from tkinter import messagebox
import database as db
from theme import COLORS, FONTS


class LoginScreen(tk.Frame):

    def __init__(self, parent, on_login, **kwargs):
        super().__init__(parent, bg=COLORS["bg_primary"], **kwargs)
        self.on_login = on_login
        self._build_ui()
        self.after(100, self._animate_in)

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Center card
        card = tk.Frame(self, bg=COLORS["bg_card"], bd=0,
                        highlightthickness=1,
                        highlightbackground=COLORS["border"],
                        padx=60, pady=50)
        card.place(relx=0.5, rely=0.5, anchor="center", width=460)

        # Logo / Brand
        logo_frame = tk.Frame(card, bg=COLORS["bg_card"])
        logo_frame.pack(pady=(0, 8))

        self.logo_label = tk.Label(logo_frame, text="🍽️",
                                   bg=COLORS["bg_card"], fg=COLORS["accent"],
                                   font=("Cairo", 52))
        self.logo_label.pack()

        tk.Label(card, text="مطعم الأصالة",
                 fg=COLORS["accent"], bg=COLORS["bg_card"],
                 font=FONTS["title_xl"]).pack()

        tk.Label(card, text="نظام إدارة المطعم ERP",
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                 font=FONTS["body_md"]).pack(pady=(4, 28))

        # Divider
        tk.Frame(card, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 24))

        # Username
        tk.Label(card, text="اسم المستخدم", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w")

        user_frame = tk.Frame(card, bg=COLORS["bg_hover"], bd=0,
                              highlightthickness=1,
                              highlightbackground=COLORS["border"])
        user_frame.pack(fill="x", pady=(4, 16))

        tk.Label(user_frame, text="👤", bg=COLORS["bg_hover"],
                 fg=COLORS["text_muted"], font=FONTS["body_md"],
                 padx=10).pack(side="left")
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(user_frame, textvariable=self.username_var,
                                       bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                                       insertbackground=COLORS["text_primary"],
                                       font=FONTS["body_lg"], bd=0, relief="flat",
                                       justify="right")
        self.username_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 10))

        user_frame.bind("<FocusIn>", lambda e: user_frame.config(highlightbackground=COLORS["accent"]))
        self.username_entry.bind("<FocusIn>",  lambda e: user_frame.config(highlightbackground=COLORS["accent"]))
        self.username_entry.bind("<FocusOut>", lambda e: user_frame.config(highlightbackground=COLORS["border"]))

        # Password
        tk.Label(card, text="كلمة المرور", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=FONTS["body_sm"]).pack(anchor="w")

        pass_frame = tk.Frame(card, bg=COLORS["bg_hover"], bd=0,
                              highlightthickness=1,
                              highlightbackground=COLORS["border"])
        pass_frame.pack(fill="x", pady=(4, 24))

        tk.Label(pass_frame, text="🔒", bg=COLORS["bg_hover"],
                 fg=COLORS["text_muted"], font=FONTS["body_md"],
                 padx=10).pack(side="left")
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(pass_frame, textvariable=self.password_var,
                                       show="●",
                                       bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                                       insertbackground=COLORS["text_primary"],
                                       font=FONTS["body_lg"], bd=0, relief="flat",
                                       justify="right")
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 10))

        pass_frame.bind("<FocusIn>", lambda e: pass_frame.config(highlightbackground=COLORS["accent"]))
        self.password_entry.bind("<FocusIn>",  lambda e: pass_frame.config(highlightbackground=COLORS["accent"]))
        self.password_entry.bind("<FocusOut>", lambda e: pass_frame.config(highlightbackground=COLORS["border"]))

        # Error label
        self.error_label = tk.Label(card, text="", fg=COLORS["danger"],
                                     bg=COLORS["bg_card"], font=FONTS["body_sm"])
        self.error_label.pack(pady=(0, 8))

        # Login button
        self.login_btn = tk.Button(card, text="تسجيل الدخول  ➔",
                                   bg=COLORS["accent"], fg="#000000",
                                   font=FONTS["title_sm"], bd=0,
                                   padx=0, pady=12, relief="flat",
                                   cursor="hand2", command=self._do_login,
                                   activebackground=COLORS["accent_dark"],
                                   activeforeground="#000000")
        self.login_btn.pack(fill="x")

        # Hint
        tk.Label(card, text="admin / admin123   •   cashier1 / 1234",
                 fg=COLORS["text_muted"], bg=COLORS["bg_card"],
                 font=FONTS["body_sm"]).pack(pady=(16, 0))

        # Bind Enter
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self._do_login())

        # Version
        tk.Label(self, text="v1.0.0  |  Restaurant ERP System",
                 fg=COLORS["text_muted"], bg=COLORS["bg_primary"],
                 font=FONTS["body_sm"]).place(relx=0.5, rely=0.97, anchor="center")

        self.username_entry.focus()

    def _animate_in(self):
        """Subtle pulse animation on logo."""
        sizes = [52, 56, 52]
        self._pulse(sizes, 0)

    def _pulse(self, sizes, idx):
        if idx < len(sizes):
            try:
                self.logo_label.config(font=("Cairo", sizes[idx]))
                self.after(120, lambda: self._pulse(sizes, idx + 1))
            except Exception:
                pass

    def _do_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            self._show_error("يرجى إدخال اسم المستخدم وكلمة المرور")
            return

        self.login_btn.config(text="جاري التحقق...", state="disabled")
        self.after(300, lambda: self._authenticate(username, password))

    def _authenticate(self, username, password):
        user = db.authenticate_user(username, password)
        if user:
            self.error_label.config(text="")
            self.on_login(user)
        else:
            self._show_error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
            self.login_btn.config(text="تسجيل الدخول  ➔", state="normal")
            self.password_var.set("")
            self.password_entry.focus()

    def _show_error(self, msg):
        self.error_label.config(text=msg)
        self.login_btn.config(text="تسجيل الدخول  ➔", state="normal")
