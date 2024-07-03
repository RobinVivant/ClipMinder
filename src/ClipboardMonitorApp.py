from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (QWidget, QSystemTrayIcon, QMenu, QDialog, QApplication)
from ClipboardMonitorThread import ClipboardMonitorThread
from DatabaseManager import DatabaseManager
from Settings import Settings
from SettingsDialog import SettingsDialog
from SummarizationThread import SummarizationThread
from utils import set_clipboard_content


class ClipboardMonitorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.settings = Settings(self.db_manager)
        self.init_ui()
        self.monitor_thread = None
        self.summarization_threads = []
        self.start_monitoring()  # Start monitoring on app launch

    def init_ui(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.set_icon(is_active=False)  # Set initial icon to inactive state

        self.menu = QMenu()
        self.toggle_action = QAction("Stop Monitoring", self)
        self.toggle_action.triggered.connect(self.toggle_monitoring)
        self.menu.addAction(self.toggle_action)

        self.menu.addSeparator()

        self.history_menu = self.menu.addMenu("Copy History")
        self.update_history_menu()

        self.menu.addSeparator()

        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.show_settings)
        self.menu.addAction(self.settings_action)

        self.menu.addSeparator()

        self.quit_action = QAction("Quit", self)
        self.quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()

    def set_icon(self, is_active):
        if is_active:
            icon = QIcon.fromTheme("media-record", QIcon.fromTheme("media-playback-start"))
        else:
            icon = QIcon.fromTheme("media-playback-stop", QIcon.fromTheme("process-stop"))
        self.tray_icon.setIcon(icon)

    def toggle_monitoring(self):
        if self.monitor_thread is None or not self.monitor_thread.isRunning():
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        if self.monitor_thread is None or not self.monitor_thread.isRunning():
            self.monitor_thread = ClipboardMonitorThread(self.settings, self.db_manager)
            self.monitor_thread.update_status.connect(self.update_status)
            self.monitor_thread.copy_completed.connect(self.add_to_history)
            self.monitor_thread.start()
            self.toggle_action.setText("Stop Monitoring")
            self.tray_icon.setToolTip("Clipboard Monitor: Running")
            self.set_icon(is_active=True)

    def stop_monitoring(self):
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.monitor_thread.stop()
            self.monitor_thread.wait()
            self.monitor_thread = None
        self.toggle_action.setText("Start Monitoring")
        self.tray_icon.setToolTip("Clipboard Monitor: Stopped")
        self.set_icon(is_active=False)

    def update_status(self, message):
        self.tray_icon.showMessage("Clipboard Monitor", message, QSystemTrayIcon.MessageIcon.Information, 3000)

    def add_to_history(self, files, lines, item_id, content, file_paths):
        self.update_history_menu()
        if self.settings.use_ollama:
            self.start_summarization(item_id, content)
        else:
            self.update_summary(item_id, "Summarization disabled")

    def update_summary(self, item_id, summary):
        if summary.startswith("Error:"):
            print(f"Summarization error for item {item_id}: {summary}")
        self.db_manager.update_copy_history_summary(item_id, summary)
        self.update_history_menu()

    def update_history_menu(self):
        self.history_menu.clear()
        history = self.db_manager.get_copy_history()
        if not history:
            self.history_menu.addAction("No recent copies").setEnabled(False)
        else:
            for item in history:
                item_id, files_count, lines_count, content, summary = item
                action_text = f"{files_count} file(s), {lines_count} line(s)"
                if summary and not summary.startswith("Error:"):
                    action_text += f" - {summary}"
                action = QAction(action_text, self)
                action.triggered.connect(lambda checked, item_id=item_id: self.copy_history_item(item_id))
                self.history_menu.addAction(action)

    def start_summarization(self, item_id, content):
        summary_thread = SummarizationThread(item_id, content, self.settings.ollama_model)
        summary_thread.summary_ready.connect(self.update_summary)
        summary_thread.finished.connect(lambda: self.cleanup_thread(summary_thread))
        self.summarization_threads.append(summary_thread)
        summary_thread.start()

    def cleanup_thread(self, thread):
        if thread in self.summarization_threads:
            self.summarization_threads.remove(thread)
        thread.deleteLater()

    def copy_history_item(self, item_id):
        content = self.db_manager.get_history_item_content(item_id)
        if content:
            set_clipboard_content(content)
            self.update_status("Copied historical content to clipboard")

    def show_settings(self):
        dialog = SettingsDialog(self.settings, self)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            if self.monitor_thread:
                self.stop_monitoring()
                self.start_monitoring()

    def quit_app(self):
        self.stop_monitoring()
        for thread in self.summarization_threads:
            thread.wait()
        self.db_manager.close()
        QApplication.instance().quit()

    def closeEvent(self, event):
        self.quit_app()
        event.accept()
