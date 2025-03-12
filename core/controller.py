"""
Controller module for Orange Intelligence.
Handles the interaction between model and view components.
"""

import logging
import os
import sys
import time
from typing import Dict, Any, List, Optional

from PyQt6.QtCore import QObject, pyqtSlot, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMenu
from pynput import keyboard

# Import the new config module
from config import CONFIG
from core.config_manager import load_config
from core.model import Model

from core.views.floating_window import FloatingWindow
from core.views.settings_page import SettingsWindow
from core.views.system_tray import SystemTray

LOG = logging.getLogger(__name__)


class Controller(QObject):
    """Controller class for the application."""

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app

        # Load the latest configuration
        self._config = load_config()

        # Initialize the model with extensions
        self.model = Model()

        # Define the tab sections based on enabled tabs in config and available extensions
        tab_sections = self._get_tab_sections()

        # Initialize the main UI components
        self.main_window = FloatingWindow(tab_sections)
        self.settings_window = None  # This will be created on-demand

        # Set up system tray
        self.system_tray = SystemTray()
        self.system_tray.open_settings_signal.connect(self.open_settings)
        self.system_tray.quit_signal.connect(self.app.quit)

        # Make sure system tray is visible
        self.system_tray.show()

        # Connect signals and slots
        self._connect_signals()

        # Initialize the main window but don't show it
        # It will be shown when triggered by keyboard shortcut

        # Set up keyboard listener for global shortcuts
        self._setup_keyboard_listener()

    def _connect_signals(self):
        """Connect signals and slots for the UI components."""
        # Disconnect any existing connections first
        try:
            self.main_window.process_text_event.disconnect()
            LOG.debug("Disconnected all process_text_event connections")
        except:
            LOG.debug("No existing process_text_event connections to disconnect")
            
        try:
            self.main_window.custom_prompt_event.disconnect()
            LOG.debug("Disconnected all custom_prompt_event connections")
        except:
            LOG.debug("No existing custom_prompt_event connections to disconnect")
        
        # Connect signals with explicit naming to avoid confusion
        LOG.debug("Setting up clean signal connections")
        self.main_window.process_text_event.connect(self._handle_process_text)
        LOG.debug("Connected process_text_event to _handle_process_text")
        
        # Create a brand new connection for custom prompts
        self.main_window.custom_prompt_event.connect(self._handle_process_text)
        LOG.debug("Connected custom_prompt_event to _handle_process_text")

    def _handle_process_text(self, section: str, function_name: str, text: str):
        """Handle the process_text_event signal from the main window."""
        import time
        from utils import get_focused_text, cmd_v, put_app_in_focus, return_app_in_focus, put_this_app_in_focus

        LOG.debug(f"SIGNAL DEBUG: _handle_process_text called with ({section}, {function_name}, {text[:20] if text else 'empty'})")
        
        try:
            # Store the current app that has focus
            focused_app = return_app_in_focus()

            # If no text is provided, get it from clipboard
            if not text:
                text = get_focused_text()
                
            LOG.debug(f"Processing text for {section}.{function_name}")

            if function_name == "custom_prompt":
                # Handle custom prompt
                prompt_text = text
                text = get_focused_text()
                result = self.model.process_text(section.lower(), function_name, text, prompt_text=prompt_text)
            else:
                # Process the text using the model
                result = self.model.process_text(section.lower(), function_name, text)

            # Put result in clipboard
            import pyperclip

            pyperclip.copy(result)

            # Return to the app that had focus and paste the result
            time.sleep(0.2)  # Give time for the clipboard to update
            put_app_in_focus(focused_app)
            time.sleep(0.2)  # Give time for the app to gain focus
            cmd_v()
            time.sleep(0.2)  # Wait before returning to this app

            # Return focus to our app
            put_this_app_in_focus()

            LOG.debug(f"Processed text with {section}.{function_name}")
        except Exception as e:
            LOG.error(f"Error processing text: {e}")

    def _handle_custom_prompt(self, section: str, function_name: str, prompt_text: str):
        """Handle the custom_prompt_event signal from the main window."""
        import time
        from utils import get_focused_text, cmd_v, put_app_in_focus, return_app_in_focus, put_this_app_in_focus

        LOG.debug(f"SIGNAL DEBUG: _handle_custom_prompt called with ({section}, {function_name}, {prompt_text[:20] if prompt_text else 'empty'})")
        
        try:
            input_text = ""

            # Store the current app that has focus
            focused_app = return_app_in_focus()

            # If no text is provided, get it from clipboard
            if not input_text:
                input_text = get_focused_text()
                
            LOG.debug(f"Processing custom prompt for {section}.{function_name}")
            
            # Process the custom prompt using the model
            # We pass the prompt_text directly since it was entered by the user
            result = self.model.process_text(section.lower(), "custom_prompt", input_text, prompt_text=prompt_text)

            # Put result in clipboard
            import pyperclip
            pyperclip.copy(result)

            # Return to the app that had focus and paste the result
            time.sleep(0.2)  # Give time for the clipboard to update
            put_app_in_focus(focused_app)
            time.sleep(0.2)  # Give time for the app to gain focus
            cmd_v()
            time.sleep(0.2)  # Wait before returning to this app

            # Return focus to our app
            put_this_app_in_focus()

            LOG.debug(f"Processed custom prompt with {section}.{function_name}")
        except Exception as e:
            LOG.error(f"Error processing custom prompt: {e}")

    def _setup_keyboard_listener(self):
        """Set up global keyboard shortcuts."""
        # Variables to track Alt/Option key double-tap
        self._last_alt_press_time = 0
        self._alt_press_count = 0

        # Start keyboard listener in a separate thread
        self._keyboard_listener = keyboard.Listener(on_press=self._on_key_press, on_release=self._on_key_release)
        self._keyboard_listener.daemon = True
        self._keyboard_listener.start()

    def _on_key_press(self, key):
        """Handle key press events for global shortcuts."""
        try:
            # Check if Alt/Option key is pressed
            if key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                current_time = time.time()
                # Check if this is a second press within 0.5 seconds
                if current_time - self._last_alt_press_time < 0.5:
                    self._alt_press_count += 1
                    # If double-tapped, toggle window visibility
                    if self._alt_press_count == 2:
                        # Use invokeMethod to safely call from another thread
                        QTimer.singleShot(0, self._toggle_window_visibility)
                        self._alt_press_count = 0
                else:
                    # First press or too much time elapsed
                    self._alt_press_count = 1

                self._last_alt_press_time = current_time
        except Exception as e:
            LOG.error(f"Error in keyboard listener: {e}")

    def _on_key_release(self, key):
        """Handle key release events."""
        pass

    @pyqtSlot()
    def _toggle_window_visibility(self):
        """Toggle the visibility of the main window."""
        if self.main_window.isVisible():
            self.main_window.hide()
            LOG.debug("Window hidden via keyboard shortcut")
        else:
            # Position the window at the bottom center of the screen before showing
            self.main_window.position_at_bottom_center()
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            LOG.debug("Window shown via keyboard shortcut")

    def _get_tab_sections(self) -> Dict[str, List[str]]:
        """Get the tab sections based on enabled tabs in config and available extensions."""
        # Get available sections from the model (this represents all loaded extensions)
        dynamic_sections = self.model.get_sections()

        # Map section keys to display names (title case)
        section_names = {
            "basics": "Basics",
            "openai": "OpenAI",
            "google_gemini": "Google Gemini",
            "ollama": "Ollama",
            "variables": "Variables",
        }

        # Get enabled tabs from config
        enabled_tabs = self._config.get("ui", {}).get("enabled_tabs", {})

        # If no configuration exists, return all dynamic sections (backwards compatibility)
        if not enabled_tabs:
            formatted_sections = {}
            for section_key, functions in dynamic_sections.items():
                display_name = section_names.get(section_key, section_key.replace("_", " ").title())
                formatted_sections[display_name] = [func_name.replace("_", " ").title() for func_name in functions]
            return formatted_sections

        # Filter sections based on enabled_tabs configuration
        filtered_sections = {}
        for section_key, functions in dynamic_sections.items():
            # Check if this section is enabled in configuration
            if section_key in enabled_tabs and enabled_tabs[section_key]:
                # Use prettier display name for the section
                display_name = section_names.get(section_key, section_key.replace("_", " ").title())
                # Format function names to title case with spaces
                formatted_functions = [func_name.replace("_", " ").title() for func_name in functions if func_name != "custom_prompt"]
                filtered_sections[display_name] = formatted_functions

        return filtered_sections

    @pyqtSlot()
    def open_settings(self):
        """Open the settings window."""
        if not self.settings_window:
            # Create the settings window if it doesn't exist
            self.settings_window = SettingsWindow(parent=self.main_window)  # Set parent to main window
            self.settings_window.settings_changed.connect(self.reload_config)

        # Show the settings window and bring it to the front
        self.settings_window.show()
        self.settings_window.raise_()  # Bring window to the front
        self.settings_window.activateWindow()  # Give it keyboard focus

    @pyqtSlot()
    def reload_config(self):
        """Reload the configuration after settings have been changed."""
        # Reload the configuration from disk
        self._config = load_config()
        
        LOG.debug("Reloading configuration after settings change")

        # Update the UI components with the new configuration
        self._update_ui_from_config()
        
        # If we need to recreate tab sections based on new config
        # Get the updated tab sections
        tab_sections = self._get_tab_sections()
        
        # Clear and recreate tabs if necessary (may be needed for newly enabled tabs)
        if hasattr(self.main_window, 'tab_widget'):
            # Only if there are changes to the tab structure
            if self.main_window.tab_widget.count() != len(tab_sections):
                LOG.debug("Rebuilding tabs with new sections")
                # Store current tab
                current_tab = self.main_window.tab_widget.currentIndex()
                
                # Clear existing tabs
                while self.main_window.tab_widget.count() > 0:
                    self.main_window.tab_widget.removeTab(0)
                
                # Set up tabs with new sections
                self.main_window.set_up_tab_widget(tab_sections)
                
                # Restore tab selection if possible
                if current_tab < self.main_window.tab_widget.count():
                    self.main_window.tab_widget.setCurrentIndex(current_tab)

        LOG.debug("Configuration reloaded and UI updated")

    def _update_ui_from_config(self):
        """Update UI components based on the current configuration."""
        # Get enabled tabs from config
        enabled_tabs = self._config.get("ui", {}).get("enabled_tabs", {})
        
        LOG.debug(f"Updating UI with enabled tabs: {enabled_tabs}")
        
        # Update the main window's tab visibility
        for tab_name, is_enabled in enabled_tabs.items():
            LOG.debug(f"Setting tab visibility: {tab_name} -> {is_enabled}")
            self.main_window.set_tab_visible(tab_name, is_enabled)
        
        # Update other UI components as needed

    def _get_icon(self) -> Optional[QIcon]:
        """Get the application icon from the config."""
        icon_path = self._config.get("app", {}).get("icon")
        if icon_path and os.path.exists(icon_path):
            return QIcon(icon_path)
        return None
