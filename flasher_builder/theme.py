"""Light/dark theme support. The light stylesheet in gui.py stays the source of truth;
dark mode is the same layout with every colour swapped through DARK."""
from __future__ import annotations

import re
import sys

from PySide6.QtGui import QColor as _QColor

_state = {'dark': False}

# Light colour -> dark colour. Colours that are already dark (sidebar text, console,
# tooltip) are left out on purpose and stay as they are.
DARK = {
    # surfaces
    '#f4f6f9': '#0b101b', '#101c30': '#070b13', '#ffffff': '#121a2b', '#f8fafd': '#0f1625',
    '#f3f5f8': '#0d1320', '#f2f4f8': '#0d1320', '#f7f9fc': '#1a2336', '#f0f4fa': '#1c2438',
    '#f3f6fc': '#1c2438', '#edf2f8': '#1c2438', '#f5f7fb': '#121a2b', '#f1f5fc': '#1c2740',
    '#e4ecfa': '#223052', '#eef3ff': '#1c2f55', '#eaf0ff': '#1c2f55', '#dce5f3': '#2a3f6b',
    '#dce7ff': '#2c4a85', '#edf2fc': '#1c2740', '#fff0f0': '#3a1f26',
    # borders and lines
    '#eef1f6': '#1e2739', '#edf0f5': '#222c42', '#e3e9f3': '#252f45', '#e1e6ef': '#263248',
    '#dce3ee': '#2a3550', '#e6eaf1': '#222c42', '#e5eaf1': '#222c42', '#b9c9e5': '#3b4d75',
    '#b8c9e4': '#3b4d75', '#a8bddf': '#4a6db5', '#c4cddc': '#39455f', '#9db7ec': '#4a6db5',
    '#a0b8e8': '#2d4472', '#f0f4ff': '#8fa6d4',
    # accent
    '#3268d9': '#5b8def', '#245ac9': '#7aa2f7', '#3b66c8': '#8fb4ff', '#285bc0': '#a9c6ff',
    '#2c5fba': '#a9c6ff', '#5c83d7': '#6b91df', '#4277dd': '#5b8def',
    # text
    '#1b273b': '#e4e9f4', '#18283f': '#f1f4fa', '#20324b': '#e8edf7', '#263851': '#dbe3f1',
    '#40536e': '#b9c4d8', '#485871': '#9aa6bd', '#3c4f6b': '#aab6cc', '#536b92': '#9aa6bd',
    '#7b889a': '#8b97ad', '#7d8b9e': '#8b97ad', '#7f8b9c': '#8b97ad', '#76859b': '#9aa6bd',
    '#8290a4': '#8b97ad', '#94a0b1': '#7e8aa3', '#a5afbf': '#5b6880', '#a3adbc': '#5b6880',
    '#8b9bb2': '#7e8aa3', '#617188': '#9aa6bd',
    # status
    '#b35454': '#e07a7a', '#9b3434': '#f09595', '#c68181': '#b05a5a', '#347856': '#4ca77a',
}
CARD = '#161e30'
_HEX = re.compile(r'#[0-9a-fA-F]{6}\b')


def is_dark():
    return _state['dark']


def set_dark(value):
    _state['dark'] = bool(value)


def themed(color):
    """Map a '#rrggbb' string to its dark twin while dark mode is on."""
    if _state['dark'] and isinstance(color, str) and color.startswith('#'):
        return DARK.get(color.lower(), color)
    return color


class QColor(_QColor):
    """QColor that swaps '#rrggbb' strings for their dark twin while dark mode is on."""
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], str):
            args = (themed(args[0]),)
        super().__init__(*args)


def build_style(style, dark):
    if not dark:
        return style
    # Cards sit one step above the fields and the page; handle them before the generic map.
    style = style.replace('QFrame#card { background: #ffffff;', 'QFrame#card { background: ' + CARD + ';')
    style = style.replace('alternate-background-color: #f8fafd', 'alternate-background-color: #1a2236')
    style = style.replace('background: white', 'background: ' + CARD)
    return _HEX.sub(lambda m: DARK.get(m.group(0).lower(), m.group(0)), style)


def system_prefers_dark(hints):
    """Whether the OS is in dark mode. `hints` is QGuiApplication.styleHints()."""
    from PySide6.QtCore import Qt
    scheme = hints.colorScheme()
    if scheme != Qt.ColorScheme.Unknown:
        return scheme == Qt.ColorScheme.Dark
    if sys.platform == 'win32':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize') as key:
                return winreg.QueryValueEx(key, 'AppsUseLightTheme')[0] == 0
        except OSError:
            pass
    return False
