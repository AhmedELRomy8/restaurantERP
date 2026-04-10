"""
Reusable UI widgets for Restaurant ERP
"""
import tkinter as tk
from tkinter import ttk
from theme import COLORS, FONTS


class RoundedButton(tk.Canvas):
    """A button with rounded corners and hover effect."""

    def __init__(self, parent, text="", command=None, width=120, height=40,
                 radius=10, bg=None, fg=None, hover_bg=None,
                 font=None, icon="", **kwargs):
        bg = bg or COLORS["accent"]
        fg = fg or "#000000"
        hover_bg = hover_bg or COLORS["accent_dark"]
        font = font or FONTS["body_md"]

        super().__init__(parent, width=width, height=height,
                         bg=parent.cget("bg") if hasattr(parent, 'cget') else COLORS["bg_primary"],
                         highlightthickness=0, **kwargs)
        self._bg = bg
        self._fg = fg
        self._hover_bg = hover_bg
        self._radius = radius
        self._text = (icon + " " if icon else "") + text
        self._font = font
        self._command = command
        self._w = width
        self._h = height
        self._draw(bg)

        self.bind("<Enter>", lambda e: self._draw(hover_bg))
        self.bind("<Leave>", lambda e: self._draw(bg))
        self.bind("<Button-1>", self._click)

    def _draw(self, color):
        self.delete("all")
        r = self._radius
        w, h = self._w, self._h
        self.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill=color, outline=color)
        self.create_arc(w-r*2, 0, w, r*2, start=0, extent=90, fill=color, outline=color)
        self.create_arc(0, h-r*2, r*2, h, start=180, extent=90, fill=color, outline=color)
        self.create_arc(w-r*2, h-r*2, w, h, start=270, extent=90, fill=color, outline=color)
        self.create_rectangle(r, 0, w-r, h, fill=color, outline=color)
        self.create_rectangle(0, r, w, h-r, fill=color, outline=color)
        self.create_text(w//2, h//2, text=self._text, fill=self._fg,
                         font=self._font, anchor="center")

    def _click(self, event=None):
        if self._command:
            self._command()

    def configure_text(self, text):
        self._text = text
        self._draw(self._bg)


class StatCard(tk.Frame):
    """A KPI / stat card for the dashboard."""

    def __init__(self, parent, title="", value="", icon="", color=None, **kwargs):
        color = color or COLORS["accent"]
        super().__init__(parent, bg=COLORS["bg_card"],
                         bd=0, highlightthickness=1,
                         highlightbackground=COLORS["border"], **kwargs)

        # Left accent bar
        accent = tk.Frame(self, bg=color, width=5)
        accent.pack(side="left", fill="y")

        body = tk.Frame(self, bg=COLORS["bg_card"], padx=16, pady=14)
        body.pack(side="left", fill="both", expand=True)

        tk.Label(body, text=icon + " " + title,
                 fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                 font=FONTS["body_sm"]).pack(anchor="w")

        self.value_label = tk.Label(body, text=value,
                                    fg=color, bg=COLORS["bg_card"],
                                    font=FONTS["title_lg"])
        self.value_label.pack(anchor="w", pady=(4, 0))

    def update_value(self, value, color=None):
        self.value_label.config(text=value)
        if color:
            self.value_label.config(fg=color)


class SidebarButton(tk.Frame):
    """Sidebar navigation button."""

    def __init__(self, parent, text="", icon="", command=None, active=False, **kwargs):
        super().__init__(parent, bg=COLORS["bg_sidebar"], cursor="hand2", **kwargs)
        self._command = command
        self._active = active
        self._text = text
        self._icon = icon

        self.inner = tk.Frame(self, bg=COLORS["sidebar_active"] if active else COLORS["bg_sidebar"],
                               padx=16, pady=10)
        self.inner.pack(fill="x")

        # Active indicator bar
        self.indicator = tk.Frame(self.inner, bg=COLORS["sidebar_active"] if active else COLORS["bg_sidebar"],
                                   width=4)
        self.indicator.pack(side="left", fill="y")

        tk.Label(self.inner, text=icon, fg=COLORS["sidebar_active"] if active else COLORS["text_secondary"],
                 bg=COLORS["sidebar_active"] if active else COLORS["bg_sidebar"],
                 font=FONTS["title_sm"], width=3).pack(side="left")

        tk.Label(self.inner, text=text, fg=COLORS["text_primary"] if active else COLORS["text_secondary"],
                 bg=COLORS["sidebar_active"] if active else COLORS["bg_sidebar"],
                 font=FONTS["body_md"]).pack(side="left", padx=(4, 0))

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.inner.bind("<Enter>", self._on_enter)
        self.inner.bind("<Leave>", self._on_leave)
        self.inner.bind("<Button-1>", self._on_click)
        for child in self.inner.winfo_children():
            child.bind("<Button-1>", self._on_click)
            child.bind("<Enter>", self._on_enter)
            child.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        if not self._active:
            self.inner.config(bg=COLORS["sidebar_hover"])
            for child in self.inner.winfo_children():
                child.config(bg=COLORS["sidebar_hover"])

    def _on_leave(self, e):
        if not self._active:
            self.inner.config(bg=COLORS["bg_sidebar"])
            for child in self.inner.winfo_children():
                child.config(bg=COLORS["bg_sidebar"])

    def _on_click(self, e):
        if self._command:
            self._command()

    def set_active(self, active: bool):
        self._active = active
        color = COLORS["sidebar_active"] if active else COLORS["bg_sidebar"]
        self.inner.config(bg=color)
        for child in self.inner.winfo_children():
            child.config(bg=color)


class StyledEntry(tk.Frame):
    """Styled input field with label."""

    def __init__(self, parent, label="", placeholder="", width=200, password=False, **kwargs):
        super().__init__(parent, bg=parent.cget("bg") if hasattr(parent, 'cget') else COLORS["bg_card"])

        if label:
            tk.Label(self, text=label, fg=COLORS["text_secondary"],
                     bg=self.cget("bg"), font=FONTS["body_sm"]).pack(anchor="w", pady=(0, 4))

        frame = tk.Frame(self, bg=COLORS["bg_hover"], bd=0,
                         highlightthickness=1, highlightbackground=COLORS["border"])
        frame.pack(fill="x")

        show = "*" if password else ""
        self.entry = tk.Entry(frame, bg=COLORS["bg_hover"], fg=COLORS["text_primary"],
                               insertbackground=COLORS["text_primary"],
                               font=FONTS["body_md"], bd=0, width=width,
                               relief="flat", show=show)
        self.entry.pack(padx=10, pady=8, fill="x")

        if placeholder:
            self._ph = placeholder
            self._ph_active = True
            self.entry.insert(0, placeholder)
            self.entry.config(fg=COLORS["text_muted"])
            self.entry.bind("<FocusIn>", self._clear_ph)
            self.entry.bind("<FocusOut>", self._restore_ph)

        frame.bind("<FocusIn>", lambda e: frame.config(highlightbackground=COLORS["accent"]))
        self.entry.bind("<FocusIn>", lambda e: frame.config(highlightbackground=COLORS["accent"]))
        self.entry.bind("<FocusOut>", lambda e: frame.config(highlightbackground=COLORS["border"]))

    def _clear_ph(self, e):
        if hasattr(self, '_ph_active') and self._ph_active:
            self.entry.delete(0, "end")
            self.entry.config(fg=COLORS["text_primary"])
            self._ph_active = False

    def _restore_ph(self, e):
        if hasattr(self, '_ph') and not self.entry.get():
            self.entry.insert(0, self._ph)
            self.entry.config(fg=COLORS["text_muted"])
            self._ph_active = True

    def get(self):
        if hasattr(self, '_ph_active') and self._ph_active:
            return ""
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))
        self.entry.config(fg=COLORS["text_primary"])
        if hasattr(self, '_ph_active'):
            self._ph_active = False


class DataTable(tk.Frame):
    """Styled data table using ttk.Treeview."""

    def __init__(self, parent, columns: list, **kwargs):
        super().__init__(parent, bg=COLORS["bg_card"])

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview",
                         background=COLORS["bg_card"],
                         foreground=COLORS["text_primary"],
                         fieldbackground=COLORS["bg_card"],
                         rowheight=36,
                         font=FONTS["body_md"])
        style.configure("Dark.Treeview.Heading",
                         background=COLORS["bg_hover"],
                         foreground=COLORS["accent"],
                         font=FONTS["body_sm"],
                         relief="flat")
        style.map("Dark.Treeview",
                  background=[("selected", COLORS["accent"])],
                  foreground=[("selected", "#000000")])
        style.layout("Dark.Treeview", [('Dark.Treeview.treearea', {'sticky': 'nswe'})])

        scroll = tk.Scrollbar(self, bg=COLORS["bg_card"], troughcolor=COLORS["bg_hover"],
                               activebackground=COLORS["accent"])
        scroll.pack(side="right", fill="y")

        col_ids = [c["id"] for c in columns]
        self.tree = ttk.Treeview(self, columns=col_ids, show="headings",
                                  style="Dark.Treeview", yscrollcommand=scroll.set)
        scroll.config(command=self.tree.yview)

        for col in columns:
            self.tree.heading(col["id"], text=col["label"],
                               anchor=col.get("anchor", "center"))
            self.tree.column(col["id"], width=col.get("width", 100),
                              anchor=col.get("anchor", "center"),
                              stretch=col.get("stretch", True))

        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure("odd", background=COLORS["bg_secondary"])
        self.tree.tag_configure("even", background=COLORS["bg_card"])

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def insert_row(self, values: tuple, tags=None):
        count = len(self.tree.get_children())
        tag = ("odd" if count % 2 else "even",)
        if tags:
            tag = tag + tuple(tags)
        return self.tree.insert("", "end", values=values, tags=tag)

    def get_selected(self):
        sel = self.tree.selection()
        if sel:
            return self.tree.item(sel[0])
        return None


class Toast(tk.Toplevel):
    """Temporary notification popup."""

    def __init__(self, parent, message: str, type_: str = "success", duration: int = 2500):
        super().__init__(parent)
        self.overrideredirect(True)
        colors = {
            "success": COLORS["success"],
            "error":   COLORS["danger"],
            "warning": COLORS["warning"],
            "info":    COLORS["info"],
        }
        icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
        bg = colors.get(type_, COLORS["info"])

        self.config(bg=bg)
        frame = tk.Frame(self, bg=bg, padx=16, pady=12)
        frame.pack()
        tk.Label(frame, text=f"{icons.get(type_, '')} {message}",
                 bg=bg, fg="white", font=FONTS["body_md"]).pack()

        # Position at bottom-right of parent
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.95)
        self.update_idletasks()
        pw = parent.winfo_rootx() + parent.winfo_width()
        ph = parent.winfo_rooty() + parent.winfo_height()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{pw - w - 30}+{ph - h - 80}")

        self.after(duration, self.destroy)
