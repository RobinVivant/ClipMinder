# ClipMinder

ClipMinder is a macOS application that monitors your clipboard for file paths and processes them automatically. It's designed to streamline your workflow by making it easy to copy the contents of multiple files or directories with a single clipboard operation.

## Features

- Monitors clipboard for file and directory paths
- Automatically processes text files when paths are copied
- Configurable file type support and size limits
- Optional content summarization using Ollama
- System tray integration for easy access and control
- Copy history with quick access to previous clipboard contents

## Requirements

- macOS (tested on macOS Monterey and later)
- Python 3.11 or later
- PyQt6
- py2app (for building the standalone application)
- Ollama (optional, for content summarization)

## Build the application
```
./build.sh
```
The built application will be available in the `dist` directory.

## Usage

1. Launch the ClipMinder application.
2. The app will run in the background with an icon in the system tray.
3. Copy a file or directory path to your clipboard.
4. ClipMinder will automatically process the contents of the file(s) and update your clipboard with the text content.
5. Access the app's features through the system tray icon:
   - Toggle monitoring on/off
   - View and access copy history
   - Open settings
   - Quit the application

## Configuration

Access the settings through the system tray icon to configure:

- File types to process (or process all file types)
- Maximum file size to process
- Enable/disable Ollama summarization
- Select Ollama model for summarization

## Development

The project structure is as follows:

- `src/`: Contains the source code for the application
  - `main.py`: Entry point of the application
  - `ClipboardMonitorApp.py`: Main application class
  - `ClipboardMonitorThread.py`: Thread for monitoring clipboard
  - `DatabaseManager.py`: Manages SQLite database operations
  - `Settings.py`: Handles application settings
  - `SettingsDialog.py`: UI for settings configuration
  - `SummarizationThread.py`: Thread for Ollama summarization
  - `utils.py`: Utility functions
- `setup.py`: Configuration for building the application with py2app
- `build.sh`: Shell script to build the application

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
