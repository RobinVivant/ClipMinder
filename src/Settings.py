from utils import get_installed_ollama_models


class Settings:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.process_all_files = self.db_manager.get_setting("process_all_files", "True") == "True"
        self.max_file_size = int(self.db_manager.get_setting("max_file_size", "1"))
        self.supported_extensions = self.db_manager.get_setting("supported_extensions",
                                                                ".txt,.md,.py,.js,.html,.css,.json,.xml,.csv,.yml,.yaml,.sh,.bash,.zsh,.ts").split(
            ',')
        self.use_ollama = self.db_manager.get_setting("use_ollama", "False") == "True"
        self.ollama_model = self.db_manager.get_setting("ollama_model", "")
        self.installed_models = get_installed_ollama_models()

    def save(self):
        self.db_manager.set_setting("process_all_files", str(self.process_all_files))
        self.db_manager.set_setting("max_file_size", str(self.max_file_size))
        self.db_manager.set_setting("supported_extensions", ",".join(self.supported_extensions))
        self.db_manager.set_setting("use_ollama", str(self.use_ollama))
        self.db_manager.set_setting("ollama_model", self.ollama_model)
