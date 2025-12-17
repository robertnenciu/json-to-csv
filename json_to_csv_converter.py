#!/usr/bin/env python3
"""
JSON to CSV Converter with PySide UI
Handles nested JSON structures and properly escapes commas in CSV output.
"""

import sys
import json
import csv
from pathlib import Path
from typing import Any, Dict, List, Union, Tuple

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QMessageBox, QProgressBar,
    QTabWidget, QPlainTextEdit, QCheckBox, QSpinBox, QGroupBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont


class JsonToCsvConverter:
    """Converts JSON data to CSV format with proper comma handling."""
    
    @staticmethod
    def flatten_json(data: Any, parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """
        Flatten nested JSON structure into a flat dictionary.
        
        Args:
            data: JSON data (dict, list, or primitive)
            parent_key: Parent key for nested structures
            sep: Separator for nested keys
            
        Returns:
            Flattened dictionary
        """
        items = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{parent_key}{sep}{key}" if parent_key else key
                if isinstance(value, (dict, list)):
                    items.extend(JsonToCsvConverter.flatten_json(value, new_key, sep=sep).items())
                else:
                    items.append((new_key, value))
        elif isinstance(data, list):
            for i, value in enumerate(data):
                new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
                if isinstance(value, (dict, list)):
                    items.extend(JsonToCsvConverter.flatten_json(value, new_key, sep=sep).items())
                else:
                    items.append((new_key, value))
        else:
            return {parent_key: data} if parent_key else {}
        
        return dict(items)
    
    @staticmethod
    def json_to_csv(json_data: Union[List[Dict], Dict], output_path: Path, max_rows_per_file: int = None) -> Tuple[bool, int, str]:
        """
        Convert JSON data to CSV file(s) with proper comma handling.
        
        Args:
            json_data: JSON data (list of dicts or single dict)
            output_path: Path to save CSV file(s)
            max_rows_per_file: Maximum rows per file. If None, creates a single file.
            
        Returns:
            Tuple of (success: bool, num_files: int, message: str)
        """
        try:
            # Normalize input to list of dicts
            if isinstance(json_data, dict):
                json_data = [json_data]
            elif not isinstance(json_data, list):
                raise ValueError("JSON data must be a dict or list of dicts")
            
            if not json_data:
                raise ValueError("JSON data is empty")
            
            # Flatten all records while preserving key order as encountered
            flattened_records = []
            ordered_keys: List[str] = []
            
            for record in json_data:
                flattened = JsonToCsvConverter.flatten_json(record)
                flattened_records.append(flattened)
                
                for key in flattened.keys():
                    if key not in ordered_keys:
                        ordered_keys.append(key)
            
            total_records = len(flattened_records)
            
            # If max_rows_per_file is set and we have more records, split into multiple files
            if max_rows_per_file and max_rows_per_file > 0 and total_records > max_rows_per_file:
                return JsonToCsvConverter._write_split_csv(
                    flattened_records, ordered_keys, output_path, max_rows_per_file
                )
            else:
                # Write single CSV file
                with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(
                        csvfile,
                        fieldnames=ordered_keys,
                        delimiter=',',
                        quotechar='"',
                        quoting=csv.QUOTE_ALL,
                    )
                    writer.writeheader()
                    
                    for record in flattened_records:
                        complete_record = {key: record.get(key, '') for key in ordered_keys}
                        writer.writerow(complete_record)
                
                return True, 1, f"Created 1 CSV file with {total_records} rows"
            
        except Exception as e:
            print(f"Error converting JSON to CSV: {e}")
            return False, 0, str(e)
    
    @staticmethod
    def _write_split_csv(flattened_records: List[Dict], ordered_keys: List[str], 
                        output_path: Path, max_rows_per_file: int) -> Tuple[bool, int, str]:
        """
        Write CSV data split across multiple files.
        
        Args:
            flattened_records: List of flattened record dictionaries
            ordered_keys: Ordered list of column keys
            output_path: Base path for output files
            max_rows_per_file: Maximum rows per file
            
        Returns:
            Tuple of (success: bool, num_files: int, message: str)
        """
        try:
            total_records = len(flattened_records)
            num_files = (total_records + max_rows_per_file - 1) // max_rows_per_file  # Ceiling division
            
            # Get base path components
            base_dir = output_path.parent
            base_name = output_path.stem
            base_ext = output_path.suffix
            
            created_files = []
            
            for file_num in range(1, num_files + 1):
                start_idx = (file_num - 1) * max_rows_per_file
                end_idx = min(start_idx + max_rows_per_file, total_records)
                
                # Generate filename: base_1.csv, base_2.csv, etc.
                if num_files > 1:
                    file_path = base_dir / f"{base_name}_{file_num}{base_ext}"
                else:
                    file_path = output_path
                
                # Write this chunk to a file
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(
                        csvfile,
                        fieldnames=ordered_keys,
                        delimiter=',',
                        quotechar='"',
                        quoting=csv.QUOTE_ALL,
                    )
                    writer.writeheader()
                    
                    for i in range(start_idx, end_idx):
                        record = flattened_records[i]
                        complete_record = {key: record.get(key, '') for key in ordered_keys}
                        writer.writerow(complete_record)
                
                created_files.append(file_path.name)
            
            file_list = ", ".join(created_files)
            return True, num_files, f"Created {num_files} CSV file(s) with {total_records} total rows: {file_list}"
            
        except Exception as e:
            print(f"Error writing split CSV files: {e}")
            return False, 0, str(e)


class ConversionThread(QThread):
    """Thread for performing JSON to CSV conversion without blocking UI."""
    
    finished = Signal(bool, str)  # success, message
    
    def __init__(self, json_data: Any, csv_path: Path, source_name: str = "JSON", max_rows_per_file: int = None):
        super().__init__()
        self.json_data = json_data
        self.csv_path = csv_path
        self.source_name = source_name
        self.max_rows_per_file = max_rows_per_file
    
    def run(self):
        """Perform the conversion in a separate thread."""
        try:
            # Convert to CSV
            success, num_files, message = JsonToCsvConverter.json_to_csv(
                self.json_data, self.csv_path, self.max_rows_per_file
            )
            
            if success:
                self.finished.emit(True, message)
            else:
                self.finished.emit(False, f"Conversion failed: {message}")
                
        except json.JSONDecodeError as e:
            self.finished.emit(False, f"Invalid JSON: {e}")
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class JsonToCsvWindow(QMainWindow):
    """Main window for JSON to CSV converter application."""
    
    def __init__(self):
        super().__init__()
        self.json_file_path = None
        self.json_text_content = None
        self.conversion_thread = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("JSON to CSV Converter")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Title
        title = QLabel("JSON to CSV Converter")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Description
        description = QLabel(
            "Select a JSON file or paste JSON content to convert to CSV format.\n"
            "Commas in values are automatically handled with proper CSV quoting."
        )
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Tab widget for file selection and paste options
        self.input_tabs = QTabWidget()
        
        # Tab 1: File Selection
        file_tab = QWidget()
        file_tab_layout = QVBoxLayout()
        file_tab.setLayout(file_tab_layout)
        
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 3px;")
        file_layout.addWidget(self.file_label, stretch=1)
        
        browse_btn = QPushButton("Browse JSON File")
        browse_btn.clicked.connect(self.browse_json_file)
        file_layout.addWidget(browse_btn)
        
        file_tab_layout.addLayout(file_layout)
        file_tab_layout.addStretch()
        
        # Tab 2: Paste JSON
        paste_tab = QWidget()
        paste_tab_layout = QVBoxLayout()
        paste_tab.setLayout(paste_tab_layout)
        
        paste_label = QLabel("Paste your JSON content below:")
        paste_tab_layout.addWidget(paste_label)
        
        # Use QPlainTextEdit for better performance with large content
        self.json_text_edit = QPlainTextEdit()
        self.json_text_edit.setPlaceholderText("Paste JSON content here...\n\nExample:\n{\n  \"name\": \"John\",\n  \"age\": 30\n}")
        self.json_text_edit.textChanged.connect(self.on_json_text_changed)
        # Set monospace font for better readability
        font = QFont("Courier", 10)
        self.json_text_edit.setFont(font)
        paste_tab_layout.addWidget(self.json_text_edit)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_json_text)
        paste_tab_layout.addWidget(clear_btn)
        
        # Add tabs
        self.input_tabs.addTab(file_tab, "Select File")
        self.input_tabs.addTab(paste_tab, "Paste JSON")
        self.input_tabs.currentChanged.connect(self.on_tab_changed)
        
        layout.addWidget(self.input_tabs)
        
        # Split options group
        split_group = QGroupBox("Split Options (for large files)")
        split_layout = QVBoxLayout()
        split_group.setLayout(split_layout)
        
        # Enable split checkbox
        self.split_checkbox = QCheckBox("Split into multiple CSV files")
        self.split_checkbox.setToolTip("Enable this to split large JSON files into multiple CSV files")
        split_layout.addWidget(self.split_checkbox)
        
        # Max rows per file
        rows_layout = QHBoxLayout()
        rows_label = QLabel("Max rows per file:")
        self.max_rows_spinbox = QSpinBox()
        self.max_rows_spinbox.setMinimum(1)
        self.max_rows_spinbox.setMaximum(10000000)  # 10 million max
        self.max_rows_spinbox.setValue(100000)  # Default: 100k rows
        self.max_rows_spinbox.setEnabled(False)
        self.max_rows_spinbox.setToolTip("Maximum number of rows per CSV file (excluding header)")
        
        # Connect checkbox to enable/disable spinbox
        self.split_checkbox.toggled.connect(self.max_rows_spinbox.setEnabled)
        
        rows_layout.addWidget(rows_label)
        rows_layout.addWidget(self.max_rows_spinbox)
        rows_layout.addStretch()
        split_layout.addLayout(rows_layout)
        
        layout.addWidget(split_group)
        
        # Convert button
        self.convert_btn = QPushButton("Convert to CSV")
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self.convert_to_csv)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(self.convert_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status text area
        status_label = QLabel("Status:")
        layout.addWidget(status_label)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        self.status_text.setPlaceholderText("Status messages will appear here...")
        layout.addWidget(self.status_text)
        
        # Add some spacing
        layout.addStretch()
    
    def browse_json_file(self):
        """Open file dialog to select JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select JSON File",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.json_file_path = Path(file_path)
            self.file_label.setText(f"Selected: {self.json_file_path.name}")
            self.update_convert_button_state()
            self.add_status(f"Selected file: {self.json_file_path}")
    
    def on_json_text_changed(self):
        """Handle JSON text content changes."""
        text = self.json_text_edit.toPlainText().strip()
        self.json_text_content = text if text else None
        self.update_convert_button_state()
    
    def clear_json_text(self):
        """Clear the JSON text editor."""
        self.json_text_edit.clear()
        self.json_text_content = None
        self.update_convert_button_state()
    
    def on_tab_changed(self, index: int):
        """Handle tab changes."""
        self.update_convert_button_state()
    
    def update_convert_button_state(self):
        """Update the convert button enabled state based on input availability."""
        has_file = self.json_file_path is not None and self.json_file_path.exists()
        has_text = self.json_text_content is not None and len(self.json_text_content.strip()) > 0
        
        # Enable if current tab has valid input
        current_tab = self.input_tabs.currentIndex()
        if current_tab == 0:  # File tab
            self.convert_btn.setEnabled(has_file)
        else:  # Paste tab
            self.convert_btn.setEnabled(has_text)
    
    def convert_to_csv(self):
        """Convert JSON (from file or paste) to CSV."""
        current_tab = self.input_tabs.currentIndex()
        json_data = None
        source_name = "JSON"
        
        # Get JSON data based on current tab
        if current_tab == 0:  # File tab
            if not self.json_file_path or not self.json_file_path.exists():
                QMessageBox.warning(self, "Error", "Please select a valid JSON file first.")
                return
            
            try:
                with open(self.json_file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                source_name = self.json_file_path.name
            except json.JSONDecodeError as e:
                QMessageBox.critical(self, "Error", f"Invalid JSON file: {e}")
                return
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error reading file: {str(e)}")
                return
        else:  # Paste tab
            if not self.json_text_content or not self.json_text_content.strip():
                QMessageBox.warning(self, "Error", "Please paste JSON content first.")
                return
            
            try:
                json_data = json.loads(self.json_text_content)
                source_name = "pasted JSON"
            except json.JSONDecodeError as e:
                QMessageBox.critical(self, "Error", f"Invalid JSON content: {e}")
                return
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error parsing JSON: {str(e)}")
                return
        
        # Get split options
        enable_split = self.split_checkbox.isChecked()
        max_rows = self.max_rows_spinbox.value() if enable_split else None
        
        # Get output file path
        if current_tab == 0 and self.json_file_path:
            default_name = self.json_file_path.stem + ".csv"
            default_dir = str(self.json_file_path.parent)
        else:
            default_name = "output.csv"
            default_dir = ""
        
        dialog_title = "Save CSV File(s)" if enable_split else "Save CSV File"
        
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            dialog_title,
            default_dir + "/" + default_name if default_dir else default_name,
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not output_path:
            return
        
        output_path = Path(output_path)
        
        # Disable convert button and show progress
        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        if enable_split and max_rows:
            self.add_status(f"Converting {source_name} to CSV (splitting at {max_rows:,} rows per file)...")
        else:
            self.add_status(f"Converting {source_name} to CSV...")
        
        # Start conversion in separate thread
        self.conversion_thread = ConversionThread(json_data, output_path, source_name, max_rows)
        self.conversion_thread.finished.connect(self.on_conversion_finished)
        self.conversion_thread.start()
    
    def on_conversion_finished(self, success: bool, message: str):
        """Handle conversion completion."""
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        
        if success:
            self.add_status(message)
            QMessageBox.information(self, "Success", message)
        else:
            self.add_status(f"Error: {message}")
            QMessageBox.critical(self, "Error", message)
    
    def add_status(self, message: str):
        """Add a status message to the status text area."""
        self.status_text.append(message)
        # Auto-scroll to bottom
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = JsonToCsvWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

