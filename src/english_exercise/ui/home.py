"""主菜单窗口：提供 Spoken 与 Type Type 两个练习入口。"""

import tkinter as tk
import tkinter.messagebox as messagebox
import traceback
from pathlib import Path

import customtkinter as ctk

from ..audio import AudioPlayer
from ..progress import load_progress
from ..settings import DEEPL, ensure_config, get_api_key, get_voice
from ..text import load_book, split_sentences
from ..theme import Theme, apply_dark_titlebar, bind_click, bind_hover, center_window
from ..translation import DeepLTranslator
from .book_picker import BookPicker
from .typing import TypingWindow


class HomeWindow(ctk.CTk):
    """英语学习软件的主界面。"""

    WIDTH, HEIGHT = 900, 520

    def __init__(self):
        """创建主界面窗口。"""
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("English Exercise")
        self.configure(fg_color=Theme.BG)
        self.resizable(False, False)
        center_window(self, self.WIDTH, self.HEIGHT)

        self._toast_after = None
        self._picker = None
        self._typing = None

        self._build()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(120, lambda: apply_dark_titlebar(self))

    # ── 布局 ──────────────────────────────────────────────────────

    def _build(self):
        """搭建品牌栏、标题、两张模式卡片和底部提示。"""
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=64, pady=(36, 30))

        # ── 顶部品牌栏 ──
        header = ctk.CTkFrame(root, fg_color="transparent")
        header.pack(fill="x")

        mark = ctk.CTkFrame(
            header, width=10, height=10, corner_radius=3, fg_color=Theme.ACCENT
        )
        mark.pack(side="left", pady=(3, 0))
        ctk.CTkLabel(
            header,
            text="ENGLISH EXERCISE",
            font=(Theme.FONT_UI, 12, "bold"),
            text_color=Theme.ACCENT,
        ).pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            header,
            text="选择练习方式",
            font=(Theme.FONT_UI, 11),
            text_color=Theme.MUTED,
        ).pack(side="right")

        # ── 标题 ──
        ctk.CTkLabel(
            root,
            text="今天想练哪一种？",
            font=(Theme.FONT_UI, 30, "bold"),
            text_color=Theme.FG,
            anchor="w",
        ).pack(anchor="w", pady=(34, 0))

        ctk.CTkLabel(
            root,
            text="选一个模式，开始今天的英语练习。",
            font=(Theme.FONT_UI, 13),
            text_color=Theme.MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(8, 0))

        # ── 模式卡片 ──
        cards = ctk.CTkFrame(root, fg_color="transparent")
        cards.pack(fill="x", pady=(30, 0))
        cards.grid_columnconfigure(0, weight=1, uniform="mode")
        cards.grid_columnconfigure(1, weight=1, uniform="mode")

        self._make_card(
            cards,
            column=0,
            glyph="🔊",
            title="Spoken",
            desc="跟读、听写与口语练习",
            status="即将推出",
            command=self._on_spoken,
            disabled=True,
        )
        self._make_card(
            cards,
            column=1,
            glyph="⌨",
            title="Type Type",
            desc="照着原文打字，边打边听",
            status="开始练习  →",
            command=self._open_picker,
        )

        # ── 轻提示（默认隐藏）──
        self._toast = ctk.CTkLabel(
            self,
            text="",
            font=(Theme.FONT_UI, 12),
            text_color=Theme.FG,
            fg_color=Theme.SURFACE,
            corner_radius=12,
            padx=18,
            pady=8,
        )

    def _make_card(
        self,
        parent,
        column,
        glyph,
        title,
        desc,
        status,
        command,
        disabled=False,
    ):
        """创建一张可点击的模式卡片。"""
        padx = (0, 11) if column == 0 else (11, 0)
        card = ctk.CTkFrame(
            parent,
            fg_color=Theme.SURFACE,
            corner_radius=18,
            border_width=1,
            border_color=Theme.BORDER,
            height=262,
        )
        card.grid(row=0, column=column, sticky="nsew", padx=padx)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)

        badge = ctk.CTkFrame(
            card, width=60, height=60, corner_radius=18, fg_color="#232840"
        )
        badge.grid(row=0, column=0, pady=(32, 0))
        badge.grid_propagate(False)
        ctk.CTkLabel(
            badge,
            text=glyph,
            font=("Segoe UI Emoji", 24),
            text_color=Theme.ACCENT if not disabled else Theme.MUTED,
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            card,
            text=title,
            font=(Theme.FONT_UI, 23, "bold"),
            text_color=Theme.FG if not disabled else Theme.MUTED,
        ).grid(row=1, column=0, pady=(18, 0))

        ctk.CTkLabel(
            card,
            text=desc,
            font=(Theme.FONT_UI, 12),
            text_color=Theme.MUTED,
        ).grid(row=2, column=0, pady=(8, 0))

        if disabled:
            pill = ctk.CTkLabel(
                card,
                text=status,
                font=(Theme.FONT_UI, 11),
                text_color=Theme.MUTED,
                fg_color="#232840",
                corner_radius=10,
                padx=14,
                height=30,
            )
        else:
            pill = ctk.CTkLabel(
                card,
                text=status,
                font=(Theme.FONT_UI, 12, "bold"),
                text_color=Theme.BG,
                fg_color=Theme.ACCENT,
                corner_radius=10,
                padx=16,
                height=32,
            )
        pill.grid(row=3, column=0, pady=(24, 24))

        def enter():
            card.configure(
                fg_color=Theme.SURFACE_HOVER,
                border_color=Theme.BORDER_HOVER if disabled else Theme.ACCENT,
            )
            badge.configure(fg_color="#2a3153")

        def leave():
            card.configure(fg_color=Theme.SURFACE, border_color=Theme.BORDER)
            badge.configure(fg_color="#232840")

        def click(_event):
            command()

        bind_hover(card, enter, leave, cursor="arrow" if disabled else "hand2")
        bind_click(card, click)

    # ── 交互 ──────────────────────────────────────────────────────

    def _show_toast(self, text):
        """在窗口底部短暂显示一条提示。"""
        if self._toast_after is not None:
            self.after_cancel(self._toast_after)
        self._toast.configure(text=text)
        self._toast.place(relx=0.5, rely=1.0, anchor="s", y=-26)
        self._toast.lift()
        self._toast_after = self.after(2400, self._hide_toast)

    def _hide_toast(self):
        """收起底部提示。"""
        self._toast.place_forget()
        self._toast_after = None

    def _on_spoken(self):
        """Spoken 模式暂未实现，仅给出提示。"""
        self._show_toast("Spoken 模式正在开发中，敬请期待")

    def _open_picker(self):
        """打开书目选择窗口。"""
        if self._picker is not None and self._picker.winfo_exists():
            self._picker.lift()
            self._picker.focus_force()
            return

        self._picker = BookPicker(self, on_start=self._start_book)

    def _start_book(self, book_path):
        """载入所选书籍并打开打字练习窗口；成功返回 True。"""
        cfg = ensure_config()
        api_key = get_api_key(DEEPL)
        if not api_key:
            proceed = messagebox.askyesno(
                "未找到 DeepL API Key",
                "练习时不会显示中文翻译。\n\n"
                "请把 Key 填入项目根目录的 keys.ini：\n"
                "    [deepl]\n"
                "    api_key = 你的密钥\n\n"
                "仍要继续吗？",
                parent=self,
            )
            if not proceed:
                return False

        self.configure(cursor="watch")
        self.update_idletasks()
        try:
            text = load_book(book_path)
            sentences = split_sentences(text)
        except Exception as exc:
            messagebox.showerror(
                "无法打开这本书", f"{Path(book_path).name}\n\n{exc}", parent=self
            )
            return False
        finally:
            self.configure(cursor="")

        if not sentences:
            messagebox.showerror(
                "没有可练习的句子", "这本书里没有找到英文句子。", parent=self
            )
            return False

        start_index = min(load_progress(book_path), len(sentences) - 1)
        try:
            translator = DeepLTranslator(api_key)
            player = AudioPlayer(voice=get_voice(cfg))
            self.withdraw()
            self._typing = TypingWindow(
                sentences=sentences,
                book_path=book_path,
                start_index=start_index,
                translator=translator,
                audio_player=player,
                master=self,
                on_exit=self._on_typing_closed,
            )
        except Exception as exc:
            self.deiconify()
            messagebox.showerror("启动练习失败", str(exc), parent=self)
            return False
        return True

    def _on_typing_closed(self):
        """练习窗口关闭后回到主界面。"""
        self._typing = None
        self.deiconify()
        self.lift()
        self.focus_force()
        apply_dark_titlebar(self)

    def _on_close(self):
        """关闭主界面。"""
        self.destroy()

    def report_callback_exception(self, exc, val, tb):
        """忽略窗口销毁后残留回调产生的 TclError，其余异常照常输出。"""
        if isinstance(val, tk.TclError):
            return
        traceback.print_exception(exc, val, tb)
