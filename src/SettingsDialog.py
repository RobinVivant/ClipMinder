from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QCheckBox, QLabel, QPushButton, QSpinBox, QTextEdit, QComboBox
                             )

from utils import get_installed_ollama_models


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Process all files checkbox
        self.process_all_files_cb = QCheckBox("Process all file types")
        self.process_all_files_cb.setChecked(self.settings.process_all_files)
        self.process_all_files_cb.stateChanged.connect(self.toggle_supported_extensions)
        layout.addWidget(self.process_all_files_cb)

        # Supported extensions
        self.supported_extensions_label = QLabel("Supported file extensions (comma-separated):")
        layout.addWidget(self.supported_extensions_label)
        self.supported_extensions_edit = QTextEdit()
        self.supported_extensions_edit.setPlainText(", ".join(self.settings.supported_extensions))
        layout.addWidget(self.supported_extensions_edit)

        # Max file size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Max file size (MB):"))
        self.max_file_size_spin = QSpinBox()
        self.max_file_size_spin.setRange(1, 1000)  # 1 MB to 1000 MB
        self.max_file_size_spin.setValue(self.settings.max_file_size)
        size_layout.addWidget(self.max_file_size_spin)
        layout.addLayout(size_layout)

        # Ollama settings
        self.use_ollama_cb = QCheckBox("Use Ollama for summarization")
        self.use_ollama_cb.setChecked(self.settings.use_ollama)
        layout.addWidget(self.use_ollama_cb)

        ollama_model_layout = QHBoxLayout()
        ollama_model_layout.addWidget(QLabel("Ollama Model:"))
        self.ollama_model_combo = QComboBox()
        self.ollama_model_combo.addItems(self.settings.installed_models)
        if self.settings.ollama_model in self.settings.installed_models:
            self.ollama_model_combo.setCurrentText(self.settings.ollama_model)
        elif self.settings.installed_models:
            self.ollama_model_combo.setCurrentIndex(0)
        ollama_model_layout.addWidget(self.ollama_model_combo)
        layout.addLayout(ollama_model_layout)

        # Refresh models button
        refresh_button = QPushButton("Refresh Ollama Models")
        refresh_button.clicked.connect(self.refresh_ollama_models)
        layout.addWidget(refresh_button)

        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet("background-color: blue; color: white;")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.setWindowTitle("Clipboard Monitor Settings")
        self.toggle_supported_extensions()

    def toggle_supported_extensions(self):
        enabled = not self.process_all_files_cb.isChecked()
        self.supported_extensions_label.setEnabled(enabled)
        self.supported_extensions_edit.setEnabled(enabled)

    def refresh_ollama_models(self):
        self.settings.installed_models = get_installed_ollama_models()
        current_model = self.ollama_model_combo.currentText()
        self.ollama_model_combo.clear()
        self.ollama_model_combo.addItems(self.settings.installed_models)
        if current_model in self.settings.installed_models:
            self.ollama_model_combo.setCurrentText(current_model)
        elif self.settings.installed_models:
            self.ollama_model_combo.setCurrentIndex(0)

    def save_settings(self):
        self.settings.process_all_files = self.process_all_files_cb.isChecked()
        self.settings.max_file_size = self.max_file_size_spin.value()
        if not self.settings.process_all_files:
            extensions = [ext.strip() for ext in self.supported_extensions_edit.toPlainText().split(',')]
            self.settings.supported_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
        self.settings.use_ollama = self.use_ollama_cb.isChecked()
        self.settings.ollama_model = self.ollama_model_combo.currentText()
        self.settings.save()
        self.accept()
