"""包结构与入口：模块可导入，界面类就位（不创建窗口）。"""

import customtkinter as ctk

import english_exercise
from english_exercise import main as entry


def test_package_exposes_version():
    assert english_exercise.__version__


def test_entry_point_is_callable():
    assert callable(entry.main)


def test_ui_windows_are_defined():
    from english_exercise.ui.book_picker import BookPicker
    from english_exercise.ui.home import HomeWindow
    from english_exercise.ui.typing import TypingWindow

    assert issubclass(HomeWindow, ctk.CTk)
    assert issubclass(BookPicker, ctk.CTkToplevel)
    assert issubclass(TypingWindow, ctk.CTkToplevel)
