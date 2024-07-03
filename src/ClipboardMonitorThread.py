import time
from PyQt6.QtCore import QThread, pyqtSignal
from utils import get_clipboard_files, process_path, set_clipboard_content


class ClipboardMonitorThread(QThread):
    update_status = pyqtSignal(str)
    copy_completed = pyqtSignal(int, int, int, str, list)  # files_count, lines_count, item_id, content, file_paths

    def __init__(self, settings, db_manager):
        super().__init__()
        self.running = True
        self.settings = settings
        self.db_manager = db_manager

    def run(self):
        last_processed_paths = []
        while self.running:
            try:
                file_paths = get_clipboard_files()

                if file_paths and file_paths != last_processed_paths:
                    self.update_status.emit(f"Processing {len(file_paths)} file(s)/folder(s)...")
                    combined_content = ""
                    total_processed_files = 0
                    total_processed_lines = 0
                    for path in file_paths:
                        path_content, files_count, lines_count, _ = process_path(path, self.settings)
                        if path_content:
                            combined_content += path_content
                            total_processed_files += files_count
                            total_processed_lines += lines_count

                    if combined_content:
                        set_clipboard_content(combined_content)
                        item_id = self.db_manager.add_copy_history(total_processed_files, total_processed_lines,
                                                                   combined_content)
                        self.update_status.emit(
                            f"Processed {total_processed_files} file(s), {total_processed_lines} line(s)")
                        self.copy_completed.emit(total_processed_files, total_processed_lines, item_id,
                                                 combined_content, file_paths)
                        last_processed_paths = file_paths
                    else:
                        self.update_status.emit(f"No supported files found in the copied path(s)")
                        last_processed_paths = file_paths
            except Exception as e:
                self.update_status.emit(f"Error: {str(e)}")

            time.sleep(1)

    def stop(self):
        self.running = False
