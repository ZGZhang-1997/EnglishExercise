"""书目选择窗口：列出 books 文件夹里的全部书籍供用户挑选。"""

import os
import tkinter.messagebox as messagebox
from pathlib import Path

import customtkinter as ctk

from ..bookshelf import list_books, load_last_book, save_last_book
from ..paths import BOOKS_DIR
from ..theme import (
    Theme,
    apply_dark_titlebar,
    bind_click,
    bind_double_click,
    bind_hover,
    center_window,
)


class BookPicker(ctk.CTkToplevel):
    """从 books 文件夹里挑选一本书并开始练习。"""

    WIDTH, HEIGHT = 760, 620

    def __init__(self, master, on_start):
        """创建书目窗口；on_start 返回 True 表示已成功进入练习。"""
        super().__init__(master)
        self.on_start = on_start
        self.selected_path = None
        self._rows = {}
        self._books = []

        self.title("TypeType · 选择书目")
        self.configure(fg_color=Theme.BG)
        self.resizable(False, False)
        center_window(self, self.WIDTH, self.HEIGHT, y_offset=-24)
        self.transient(master)

        self._build()
        self.refresh(preselect=load_last_book())

        self.protocol("WM_DELETE_WINDOW", self._close)
        self.after(120, lambda: apply_dark_titlebar(self))
        self.after(260, self._focus_self)

    def _focus_self(self):
        """书目窗口获得焦点（窗口可能已被销毁）。"""
        try:
            if self.winfo_exists():
                self.focus_force()
        except Exception:
            pass

    # ── 布局 ──────────────────────────────────────────────────────

    def _build(self):
        """搭建标题、书单区域和底部操作栏。"""
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=34, pady=(28, 22))
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(2, weight=1)

        # ── 标题 ──
        head = ctk.CTkFrame(root, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew")
        head.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            head,
            text="选择一本书",
            font=(Theme.FONT_UI, 24, "bold"),
            text_color=Theme.FG,
        ).grid(row=0, column=0, sticky="w")

        self.lbl_count = ctk.CTkLabel(
            head, text="", font=(Theme.FONT_UI, 11), text_color=Theme.MUTED
        )
        self.lbl_count.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            root,
            text="把 .txt 书籍放进 books 文件夹，这里会自动列出全部可练习的书。",
            font=(Theme.FONT_UI, 12),
            text_color=Theme.MUTED,
            anchor="w",
            justify="left",
        ).grid(row=1, column=0, sticky="ew", pady=(8, 0))

        # ── 书单 ──
        self.list_frame = ctk.CTkScrollableFrame(
            root,
            fg_color=Theme.SURFACE,
            corner_radius=14,
            border_width=1,
            border_color=Theme.BORDER,
            scrollbar_button_color=Theme.BORDER,
            scrollbar_button_hover_color=Theme.MUTED,
        )
        self.list_frame.grid(row=2, column=0, sticky="nsew", pady=(18, 0))

        # ── 底部操作栏 ──
        footer = ctk.CTkFrame(root, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", pady=(18, 0))
        footer.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(
            footer,
            text="打开 books 文件夹",
            width=132,
            height=36,
            corner_radius=10,
            font=(Theme.FONT_UI, 12),
            fg_color="transparent",
            hover_color=Theme.BORDER,
            border_width=1,
            border_color=Theme.BORDER,
            text_color=Theme.MUTED,
            command=self._open_folder,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            footer,
            text="刷新",
            width=78,
            height=36,
            corner_radius=10,
            font=(Theme.FONT_UI, 12),
            fg_color="transparent",
            hover_color=Theme.BORDER,
            border_width=1,
            border_color=Theme.BORDER,
            text_color=Theme.MUTED,
            command=self.refresh,
        ).grid(row=0, column=1, sticky="w", padx=(10, 0))

        self.btn_start = ctk.CTkButton(
            footer,
            text="开始练习",
            width=132,
            height=40,
            corner_radius=10,
            font=(Theme.FONT_UI, 13, "bold"),
            fg_color=Theme.BORDER,
            hover_color=Theme.ACCENT_HOVER,
            text_color=Theme.MUTED,
            state="disabled",
            command=self._start,
        )
        self.btn_start.grid(row=0, column=3, sticky="e")

    # ── 书单渲染 ──────────────────────────────────────────────────

    def refresh(self, preselect=None):
        """重新扫描 books 文件夹并重建书单。"""
        previous = preselect or self.selected_path
        for child in self.list_frame.winfo_children():
            child.destroy()
        self._rows.clear()

        self._books = list_books()
        self.lbl_count.configure(
            text=f"共 {len(self._books)} 本" if self._books else "暂无书籍"
        )

        if not self._books:
            self._render_empty()
            self._select(None)
            return

        for book in self._books:
            self._rows[book.path] = self._make_row(book)

        paths = {book.path for book in self._books}
        if previous in paths:
            self._select(previous)
        else:
            self._select(None)

    def _render_empty(self):
        """书单为空时的引导界面。"""
        box = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        box.pack(fill="both", expand=True, pady=70)

        ctk.CTkLabel(
            box,
            text="书架还是空的",
            font=(Theme.FONT_UI, 16, "bold"),
            text_color=Theme.FG,
        ).pack()

        ctk.CTkLabel(
            box,
            text="把 .txt 格式的英文书籍复制到 books 文件夹，然后点「刷新」。",
            font=(Theme.FONT_UI, 12),
            text_color=Theme.MUTED,
        ).pack(pady=(8, 20))

        ctk.CTkButton(
            box,
            text="打开 books 文件夹",
            width=150,
            height=36,
            corner_radius=10,
            font=(Theme.FONT_UI, 12),
            fg_color=Theme.ACCENT,
            hover_color=Theme.ACCENT_HOVER,
            text_color=Theme.BG,
            command=self._open_folder,
        ).pack()

    def _make_row(self, book):
        """创建一条书籍条目，返回 (行容器, 选中标记)。"""
        row = ctk.CTkFrame(
            self.list_frame,
            fg_color=Theme.SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=Theme.BORDER,
            height=62,
        )
        row.pack(fill="x", padx=10, pady=5)
        row.pack_propagate(False)

        dot = ctk.CTkLabel(
            row,
            text="●",
            width=16,
            font=(Theme.FONT_UI, 10),
            text_color=Theme.BORDER_HOVER,
        )
        dot.pack(side="left", padx=(16, 6))

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=9)

        title = book.title
        if len(title) > 54:
            title = title[:26] + "…" + title[-24:]

        ctk.CTkLabel(
            info,
            text=title,
            font=(Theme.FONT_UI, 14, "bold"),
            text_color=Theme.FG,
            anchor="w",
        ).pack(anchor="w")

        meta = f"{book.size_kb} KB · 上次进度 第 {book.progress} 句"
        if not book.progress:
            meta = f"{book.size_kb} KB · 尚未开始"
        ctk.CTkLabel(
            info,
            text=meta,
            font=(Theme.FONT_UI, 11),
            text_color=Theme.MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        def enter():
            if book.path != self.selected_path:
                row.configure(
                    fg_color=Theme.SURFACE_HOVER, border_color=Theme.BORDER_HOVER
                )

        def leave():
            if book.path != self.selected_path:
                row.configure(fg_color=Theme.SURFACE, border_color=Theme.BORDER)

        bind_hover(row, enter, leave)
        bind_click(row, lambda _event, path=book.path: self._select(path))
        bind_double_click(row, lambda _event, path=book.path: self._start_path(path))

        return row, dot

    def _select(self, path):
        """更新选中状态与「开始练习」按钮。"""
        self.selected_path = path
        for row_path, (row, dot) in self._rows.items():
            if row_path == path:
                row.configure(fg_color=Theme.SURFACE_HOVER, border_color=Theme.ACCENT)
                dot.configure(text_color=Theme.ACCENT)
            else:
                row.configure(fg_color=Theme.SURFACE, border_color=Theme.BORDER)
                dot.configure(text_color=Theme.BORDER_HOVER)

        if path:
            self.btn_start.configure(
                state="normal",
                fg_color=Theme.ACCENT,
                text_color=Theme.BG,
            )
        else:
            self.btn_start.configure(
                state="disabled",
                fg_color=Theme.BORDER,
                text_color=Theme.MUTED,
            )

    # ── 操作 ──────────────────────────────────────────────────────

    def _open_folder(self):
        """用资源管理器打开 books 文件夹。"""
        try:
            BOOKS_DIR.mkdir(parents=True, exist_ok=True)
            os.startfile(BOOKS_DIR)
        except OSError as exc:
            messagebox.showerror("无法打开文件夹", str(exc), parent=self)

    def _start(self):
        """开始练习当前选中的书。"""
        self._start_path(self.selected_path)

    def _start_path(self, path):
        """校验并启动指定书籍；成功后关闭书目窗口。"""
        if not path or not Path(path).is_file():
            self.refresh()
            return
        save_last_book(path)
        if self.on_start(path):
            self._close()

    def _close(self):
        """关闭书目窗口。"""
        self.destroy()
