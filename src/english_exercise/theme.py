"""统一配色、字体与窗口小工具，供所有界面模块复用。"""


class Theme:
    """Tokyo Night 风格配色与字体常量。"""

    BG = "#16161e"  # 窗口底色
    SURFACE = "#1a1b26"  # 卡片底色
    SURFACE_HOVER = "#1f2335"  # 卡片悬停
    BORDER = "#262b40"  # 分隔线与描边
    BORDER_HOVER = "#3b4261"  # 悬停描边
    FG = "#c0caf5"  # 主文字
    TRANSLATION = "#6b7394"  # 译文
    MUTED = "#565f89"  # 次要信息
    ACCENT = "#7aa2f7"  # 强调色
    ACCENT_HOVER = "#5f87d8"  # 强调色悬停
    SUCCESS = "#9ece6a"  # 已输入
    GHOST = "#2f3550"  # 尚未输入的文字
    FLASH_BG = "#2a1a24"  # 打错时的背景闪色
    FONT_UI = "Microsoft YaHei UI"
    FONT_MONO = "Cascadia Mono"


def disable_ime_for_thread():
    """关闭当前线程的输入法，避免中文 IME 吞掉打字按键。

    必须在创建窗口之前调用，Windows 才会对整个线程生效。
    """
    try:
        import ctypes

        ctypes.windll.imm32.ImmDisableIME(0)
    except Exception:
        pass


def apply_dark_titlebar(window):
    """让 Windows 标题栏跟随深色主题，失败时静默忽略。"""
    try:
        import ctypes

        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        enabled = ctypes.c_int(1)
        for attribute in (20, 19):  # DWMWA_USE_IMMERSIVE_DARK_MODE 及其旧编号
            result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, attribute, ctypes.byref(enabled), ctypes.sizeof(enabled)
            )
            if result == 0:
                break
    except Exception:
        pass


def center_window(window, width, height, y_offset=0):
    """按给定尺寸把窗口摆到屏幕正中。"""
    window.update_idletasks()
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    x = max(0, (screen_w - width) // 2)
    y = max(0, (screen_h - height) // 2 + y_offset)
    window.geometry(f"{width}x{height}+{x}+{y}")


def _descendant_of(widget, container):
    """判断控件是否位于容器内部（用于过滤 Enter/Leave 的抖动）。"""
    while widget is not None:
        if widget is container:
            return True
        widget = getattr(widget, "master", None)
    return False


def bind_hover(container, on_enter, on_leave, cursor="hand2"):
    """让容器及其子控件整体响应鼠标悬停，避免子控件触发 Leave。"""

    def enter(_event):
        on_enter()
        try:
            container.configure(cursor=cursor)
        except Exception:
            pass

    def leave(event):
        try:
            under = container.winfo_containing(event.x_root, event.y_root)
        except Exception:
            under = None
        if _descendant_of(under, container):
            return
        on_leave()

    def walk(widget):
        widget.bind("<Enter>", enter, add="+")
        widget.bind("<Leave>", leave, add="+")
        try:
            widget.configure(cursor=cursor)
        except Exception:
            pass
        for child in widget.winfo_children():
            walk(child)

    walk(container)


def bind_click(container, handler):
    """让容器及其全部子控件响应鼠标左键点击。"""

    def walk(widget):
        widget.bind("<Button-1>", handler, add="+")
        for child in widget.winfo_children():
            walk(child)

    walk(container)


def bind_double_click(container, handler):
    """让容器及其全部子控件响应鼠标左键双击。"""

    def walk(widget):
        widget.bind("<Double-Button-1>", handler, add="+")
        for child in widget.winfo_children():
            walk(child)

    walk(container)
