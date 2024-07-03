from PyQt6.QtWidgets import QApplication
from ClipboardMonitorApp import ClipboardMonitorApp
import sys
import warnings

# Suppress DeprecationWarning for pkg_resources
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    clipboard_monitor = ClipboardMonitorApp()
    app.setQuitOnLastWindowClosed(False)
    sys.exit(app.exec())
