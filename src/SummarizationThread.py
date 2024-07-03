from PyQt6.QtCore import QThread, pyqtSignal

from utils import summarize_with_ollama


class SummarizationThread(QThread):
    summary_ready = pyqtSignal(int, str)  # item_id, summary

    def __init__(self, item_id, content, model):
        super().__init__()
        self.item_id = item_id
        self.content = content
        self.model = model

    def run(self):
        try:
            summary = summarize_with_ollama(self.content, self.model)
            print(
                f"Summarization result for item {self.item_id}: {summary[:100]}...")  # Print truncated summary for debugging
            self.summary_ready.emit(self.item_id, summary)
        except Exception as e:
            error_message = f"Error in summarization: {str(e)}"
            print(error_message)
            self.summary_ready.emit(self.item_id, error_message)
