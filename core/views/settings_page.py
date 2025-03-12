"""
Settings page component for the Orange Intelligence application.
Allows users to configure visible tabs and other UI settings.
"""

import logging
import json
import os
from typing import Dict, Any, Callable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QFrame, QScrollArea, QWidget, QFormLayout,
    QLineEdit, QMessageBox, QGridLayout, QGroupBox, QSizePolicy
)
from PyQt6.QtGui import QIcon

from config import CONFIG
from core.config_manager import save_config, set_api_key

LOG = logging.getLogger(__name__)

class SettingsWindow(QMainWindow):
    """Window for configuring application settings."""
    
    # Signal to notify that settings have been changed
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set window properties
        self.setWindowTitle("Orange Intelligence Settings")
        self.setMinimumWidth(700)
        self.setMinimumHeight(800)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Initialize UI
        self.init_ui()
        
    def closeEvent(self, event):
        """Override close event to hide the window instead of closing it."""
        event.ignore()  # Prevent the window from actually closing
        self.hide()  # Instead just hide it
        
    def init_ui(self):
        """Initialize the settings page UI."""
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        
        # Add a Settings title
        title_label = QLabel("Settings")
        title_label.setStyleSheet("""
            font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 28px;
            font-weight: 500;
            color: #ffffff;
            margin-bottom: 8px;
        """)
        main_layout.addWidget(title_label)
        
        # Add the tab settings section
        tab_section = self.create_tab_settings()
        main_layout.addWidget(tab_section)
        
        # Give fixed size to tab section to leave more room for the API section
        tab_section.setMaximumHeight(120)
        
        # Add the API configuration section with stretching
        api_section = self.create_api_settings()
        main_layout.addWidget(api_section, 1)  # Add stretch factor of 1
        
        # Add buttons at the bottom
        button_layout = QHBoxLayout()
        
        # Create Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.close)
        
        # Create Save button
        save_button = QPushButton("Save")
        save_button.setObjectName("saveButton")
        save_button.clicked.connect(self.save_settings)
        
        # Add buttons to layout
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        main_layout.addLayout(button_layout)
        
        # Apply styling
        self.central_widget.setStyleSheet("""
            QWidget#centralWidget {
                background-color: #202124;
                color: #ffffff;
            }
            
            QLabel {
                color: #ffffff;
                font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            
            QLineEdit {
                background-color: #303134;
                color: #e8eaed;
                height: 32px;
                min-height: 32px;
                min-width: 300px;
                border: 1px solid #5f6368;
                selection-background-color: #1a73e8;
                font-family: 'Menlo', monospace;
                font-size: 13px;
                padding: 4px 8px;
                border-radius: 4px;
            }
            
            QLineEdit:focus {
                border: 1px solid #8ab4f8;
            }
            
            QCheckBox {
                color: #ffffff;
                font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            
            QCheckBox::indicator:unchecked {
                width: 18px;
                height: 18px;
                background-color: #303134;
                ##border: 1px solid #5f6368;
            }
            
            QCheckBox::indicator:checked {
                width: 18px;
                height: 18px;
                background-color: #1a73e8;
                image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'></polyline></svg>");
            }
            
            QPushButton#saveButton {
                background-color: #1a73e8;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
                font-weight: 500;
            }
            
            QPushButton#saveButton:hover {
                background-color: #1765c9;
            }
            
            QPushButton#cancelButton {
                background-color: #f1f3f4;
                color: #3c4043;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
                font-weight: 500;
            }
            
            QPushButton#cancelButton:hover {
                background-color: #494c50;
            }
        """)
        
        # Ensure API settings visibility is initialized after UI is created
        self.update_api_settings_visibility()
        
    def create_tab_settings(self) -> QWidget:
        """Create the section for configuring visible tabs."""
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #303134;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Add section title without any box
        title = QLabel("Visible Tabs")
        title.setStyleSheet("""
            font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 16px;
            font-weight: 500;
            color: #ffffff;
            background-color: transparent;
            border: none;
            padding: 0;
            margin: 0;
        """)
        layout.addWidget(title)
        
        # Get enabled tabs from config
        enabled_tabs = CONFIG.get("ui", {}).get("enabled_tabs", {})
        
        # Define the valid/available tabs
        valid_tabs = ["basics", "openai", "google_gemini", "ollama"]
        
        # Create a checkbox for each valid tab
        self.tab_checkboxes = {}
        
        for tab_name in valid_tabs:
            is_enabled = enabled_tabs.get(tab_name, True)  # Default to enabled if not found
            
            display_name = tab_name.replace("_", " ").title()
            checkbox = QCheckBox(display_name)
            checkbox.setChecked(is_enabled)
            
            # Store the checkbox with its original config key
            self.tab_checkboxes[tab_name] = checkbox
            
            # Connect the stateChanged signal to update API settings visibility
            checkbox.stateChanged.connect(self.update_api_settings_visibility)
            
            layout.addWidget(checkbox)
        
        return container
    
    def create_api_settings(self) -> QWidget:
        """Create the section for configuring API settings."""
        # Create outer container
        outer_container = QWidget()
        outer_container.setStyleSheet("""
            QWidget {
                background-color: #303134;
                border-radius: 8px;
            }
        """)
        
        # Make the outer container expand to fill available space
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        outer_container.setSizePolicy(size_policy)
        
        outer_layout = QVBoxLayout(outer_container)
        outer_layout.setContentsMargins(16, 16, 16, 16)
        outer_layout.setSpacing(8)
        
        # Add section title without any box
        title = QLabel("API Configuration")
        title.setStyleSheet("""
            font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 16px;
            font-weight: 500;
            color: #ffffff;
            background-color: transparent;
            border: none;
            padding: 0;
            margin: 0;
        """)
        outer_layout.addWidget(title)
        
        # Create scroll area for API settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Set a fixed height first to ensure minimum size
        scroll_area.setMinimumHeight(400)
        
        # Configure the scroll area to fill available space
        scroll_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll_policy.setVerticalStretch(1)
        scroll_area.setSizePolicy(scroll_policy)
        
        # Re-add scrollbar styling
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2c2c2c;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #5f6368;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #8ab4f8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background-color: #2c2c2c;
            }
        """)
        
        # Create the inner container for API settings
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)  # Reduced margins
        layout.setSpacing(0)  # Reduced spacing to minimum
        
        # Helper function to create section labels
        def create_section_label(text):
            label = QLabel(text)
            label.setStyleSheet("""
                font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 14px;
                font-weight: 500;
                color: #8ab4f8;
                background-color: transparent;
                padding: 4px 0;
                margin: 0;
            """)
            return label
            
        # Create containers for each API provider with headers
        self.openai_container = QWidget()
        openai_layout = QVBoxLayout(self.openai_container)
        openai_layout.setContentsMargins(0, 4, 0, 0)
        openai_layout.setSpacing(2)
        
        openai_label = create_section_label("OpenAI")
        openai_layout.addWidget(openai_label)
        
        openai_form = QFormLayout()
        openai_form.setContentsMargins(8, 0, 0, 0)
        openai_form.setSpacing(12)
        openai_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        openai_form.setHorizontalSpacing(24)
        openai_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        openai_layout.addLayout(openai_form)
        
        self.gemini_container = QWidget()
        gemini_layout = QVBoxLayout(self.gemini_container)
        gemini_layout.setContentsMargins(0, 4, 0, 4)  # Fixed inconsistent margins
        gemini_layout.setSpacing(2)
        
        gemini_label = create_section_label("Google Gemini")
        gemini_layout.addWidget(gemini_label)
        
        gemini_form = QFormLayout()
        gemini_form.setContentsMargins(8, 0, 0, 0)
        gemini_form.setSpacing(12)
        gemini_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        gemini_form.setHorizontalSpacing(24)
        gemini_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        gemini_layout.addLayout(gemini_form)
        
        self.ollama_container = QWidget()
        ollama_layout = QVBoxLayout(self.ollama_container)
        ollama_layout.setContentsMargins(0, 4, 0, 0)
        ollama_layout.setSpacing(2)
        
        ollama_label = create_section_label("Ollama")
        ollama_layout.addWidget(ollama_label)
        
        ollama_form = QFormLayout()
        ollama_form.setContentsMargins(8, 0, 0, 0)
        ollama_form.setSpacing(12)
        ollama_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        ollama_form.setHorizontalSpacing(24)
        ollama_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        ollama_layout.addLayout(ollama_form)
        
        # Add horizontal separator function
        def create_separator():
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            separator.setStyleSheet("background-color: #5f6368; margin: 0;")
            separator.setFixedHeight(1)
            return separator
        
        # OpenAI settings
        openai_key = CONFIG.get("openai", {}).get("api_key", "")
        openai_model = CONFIG.get("openai", {}).get("default_model", "")
        
        # Create input fields
        self.openai_key_input = QLineEdit(openai_key if openai_key else "")
        self.openai_key_input.setPlaceholderText("Enter OpenAI API Key")
        self.openai_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.openai_model_input = QLineEdit(openai_model)
        self.openai_model_input.setPlaceholderText("e.g., gpt-3.5-turbo")
        
        # Add to OpenAI form layout
        openai_form.addRow("API Key:", self.openai_key_input)
        openai_form.addRow("Model:", self.openai_model_input)
        
        # Google Gemini settings
        gemini_key = CONFIG.get("google_gemini", {}).get("api_key", "")
        gemini_model = CONFIG.get("google_gemini", {}).get("default_model", "")
        
        # Create input fields
        self.gemini_key_input = QLineEdit(gemini_key if gemini_key else "")
        self.gemini_key_input.setPlaceholderText("Enter Google Gemini API Key")
        self.gemini_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.gemini_model_input = QLineEdit(gemini_model)
        self.gemini_model_input.setPlaceholderText("e.g., gemini-2.0-flash")
        
        # Add to Google Gemini form layout
        gemini_form.addRow("API Key:", self.gemini_key_input)
        gemini_form.addRow("Model:", self.gemini_model_input)
        
        # Ollama settings
        ollama_url = CONFIG.get("ollama", {}).get("url", "")
        ollama_model = CONFIG.get("ollama", {}).get("default_model", "")
        
        # Create input fields
        self.ollama_url_input = QLineEdit(ollama_url)
        self.ollama_url_input.setPlaceholderText("e.g., https://ollama.com")
        
        self.ollama_model_input = QLineEdit(ollama_model)
        self.ollama_model_input.setPlaceholderText("e.g., llama3.1")
        
        # Add to Ollama form layout
        ollama_form.addRow("URL:", self.ollama_url_input)
        ollama_form.addRow("Model:", self.ollama_model_input)
        
        # Add all API containers to the main layout with separators
        layout.addWidget(self.openai_container)
        layout.addWidget(create_separator())
        layout.addWidget(self.gemini_container)
        layout.addWidget(create_separator())
        layout.addWidget(self.ollama_container)
        
        # Add a spacer to ensure content is packed at the top
        layout.addStretch(1)
        
        # Set fixed height to ensure consistent scrollbar behavior
        container.setFixedHeight(400)
        
        # Set initial visibility based on current tab settings
        self.update_api_settings_visibility()
        
        # Set the inner container as the scroll area's widget
        scroll_area.setWidget(container)
        
        # Add the scroll area to the outer layout
        outer_layout.addWidget(scroll_area)
        
        return outer_container
    
    def update_api_settings_visibility(self):
        """Update the visibility of API settings based on the tab checkboxes."""
        # Get the current state of the tab checkboxes
        try:
            openai_enabled = self.tab_checkboxes.get("openai", None)
            gemini_enabled = self.tab_checkboxes.get("google_gemini", None)
            ollama_enabled = self.tab_checkboxes.get("ollama", None)
            
            # Show/hide API settings based on checkbox states
            if hasattr(self, "openai_container") and openai_enabled:
                self.openai_container.setVisible(openai_enabled.isChecked())
                
            if hasattr(self, "gemini_container") and gemini_enabled:
                self.gemini_container.setVisible(gemini_enabled.isChecked())
                
            if hasattr(self, "ollama_container") and ollama_enabled:
                self.ollama_container.setVisible(ollama_enabled.isChecked())
                
        except Exception as e:
            print(f"Error updating API settings visibility: {e}")
    
    def save_settings(self):
        """Save the current settings using the config manager."""
        try:
            # Get current config as a base
            updated_config = CONFIG.copy()
            
            # Update enabled_tabs configuration
            if "ui" not in updated_config:
                updated_config["ui"] = {}
            if "enabled_tabs" not in updated_config["ui"]:
                updated_config["ui"]["enabled_tabs"] = {}
                
            # Update tab visibility settings
            for tab_name, checkbox in self.tab_checkboxes.items():
                updated_config["ui"]["enabled_tabs"][tab_name] = checkbox.isChecked()
                
            # Update API keys
            # OpenAI
            if "openai" not in updated_config:
                updated_config["openai"] = {}
            
            openai_key = self.openai_key_input.text().strip()
            if openai_key:
                updated_config["openai"]["api_key"] = openai_key
                
            openai_model = self.openai_model_input.text().strip()
            if openai_model:
                updated_config["openai"]["default_model"] = openai_model
            
            # Google Gemini
            if "google_gemini" not in updated_config:
                updated_config["google_gemini"] = {}
            
            gemini_key = self.gemini_key_input.text().strip()
            if gemini_key:
                updated_config["google_gemini"]["api_key"] = gemini_key
                
            gemini_model = self.gemini_model_input.text().strip()
            if gemini_model:
                updated_config["google_gemini"]["default_model"] = gemini_model
            
            # Ollama
            if "ollama" not in updated_config:
                updated_config["ollama"] = {}
                
            ollama_url = self.ollama_url_input.text().strip()
            if ollama_url:
                updated_config["ollama"]["url"] = ollama_url
                
            ollama_model = self.ollama_model_input.text().strip()
            if ollama_model:
                updated_config["ollama"]["default_model"] = ollama_model
            
            # Save the config
            save_config(updated_config)
            
            # Notify that settings have changed
            self.settings_changed.emit()
            
            # Show success message
            QMessageBox.information(
                self,
                "Settings Saved",
                "Your settings have been saved successfully."
            )
            
            # Log the updated tab settings for debugging
            LOG.debug(f"Updated tab settings: {updated_config['ui']['enabled_tabs']}")
            
            # Hide the window instead of accepting/closing it
            self.hide()
            
        except Exception as e:
            LOG.error(f"Error saving settings: {e}")
            QMessageBox.critical(
                self,
                "Error Saving Settings",
                f"An error occurred while saving settings: {str(e)}"
            )
