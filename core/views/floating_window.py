import logging

from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QCloseEvent, QHideEvent, QKeyEvent, QShowEvent, QMouseEvent, QIcon, QCursor, QColor
from PyQt6.QtWidgets import (
    QListWidget, QListWidgetItem, QTabWidget, QVBoxLayout, QWidget,
    QHBoxLayout, QLabel, QPushButton, QFrame, QLineEdit, QSizePolicy, QApplication,
    QGraphicsDropShadowEffect
)
from core.views.styling.floating_window_style import FloatingWindowStyleOptions

LOG = logging.getLogger(__name__)


class FloatingWindow(QWidget):
    """Main floating window that contains the tabbed interface."""
    
    custom_signal = pyqtSignal(str, str) 
    windows_event = pyqtSignal(bool)
    process_text_event = pyqtSignal(str, str, str)
    custom_prompt_event = pyqtSignal(str, str, str)  # section, function, prompt_text
    event_put_app_focus = pyqtSignal()
    
    def __init__(self, tab_sections=None, parent=None):
        super().__init__(parent)
        
        # Set window title
        self.setWindowTitle("Orange Intelligence")
        
        # Initialize drag variables
        self.dragging = False
        self.drag_start_position = None
        
        # Flag to help differentiate between regular functions and custom prompts
        self.is_custom_prompt_mode = False
        
        # Create the main container (this is the 'self' since we're a QWidget)
        self.setObjectName("centralWidget")
        
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create content container
        self.content_container = QWidget()
        self.content_container.setObjectName("contentContainer")
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        content_layout.addWidget(self.tab_widget)
        
        # Add prompt field at the bottom
        self.prompt_container = self.create_prompt_field()
        content_layout.addWidget(self.prompt_container)
        
        # Add content container to main layout
        self.main_layout.addWidget(self.content_container)
        
        # Initialize tab scroll positions
        self.tab_scroll_positions = {}
        
        # Set up tab widget with sections if provided
        if tab_sections:
            self.set_up_tab_widget(tab_sections)
        
        # Apply styling
        self.apply_styling()
        
        # Connect tab change signal to update prompt field state
        self.tab_widget.currentChanged.connect(self.update_prompt_field_state)

    def apply_styling(self):
        """Apply consistent styling to match the settings page"""
        # Central widget styling
        self.setStyleSheet("""
            QWidget#centralWidget {
                background-color: #202124;
                color: #ffffff;
                border-radius: 8px;
            }
        """)
        
        # Tab widget styling
        self.tab_widget.setStyleSheet("""
            QTabWidget {
                background-color: #202124;
            }
            
            QTabWidget::pane {
                border: none;
                background-color: #202124;
            }
            
            QTabWidget::tab-bar {
                alignment: left;
                background-color: #303134;
                left: 0px;
                right: 0px;
            }
            
            QTabBar {
                background-color: #303134;
            }
            
            QTabBar::scroller {
                background-color: #303134;
            }
            
            QTabBar QToolButton {
                background-color: #303134;
                border: none;
            }
            
            QTabBar QToolButton::right-arrow {
                background-color: #303134;
            }
            
            QTabBar QToolButton::left-arrow {
                background-color: #303134;
            }
            
            QTabBar::tab {
                background-color: #303134;
                color: #e8eaed;
                font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 14px;
                font-weight: 500;
                padding: 12px 16px;
                border: none;
                min-width: 120px;
            }
            
            QTabBar::tab:hover {
                background-color: #3c4043;
                color: #ffffff;
            }
            
            QTabBar::tab:selected {
                background-color: #202124;
                color: #8ab4f8;
                border-bottom: 2px solid #8ab4f8;
            }
            
            QListWidget {
                background-color: #202124;
                border: none;
                outline: none;
                color: #e8eaed;
                font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 14px;
            }
            
            QListWidget::item {
                padding: 12px 16px;
                border-bottom: 1px solid #3c4043;
            }
            
            QListWidget::item:hover {
                background-color: #3c4043;
            }
            
            QListWidget::item:selected {
                background-color: #202124;
                color: #8ab4f8;
            }
        """)
        
        # Content container styling
        self.content_container.setStyleSheet("""
            QWidget#contentContainer {
                background-color: #202124;
            }
        """)
        
        # Prompt container
        self.prompt_container.setStyleSheet("""
            #promptContainer {
                background-color: #202124;
                border-top: 1px solid #5f6368;
                padding: 10px;
            }
        """)
        
        # Prompt field
        self.prompt_field.setStyleSheet("""
            #promptField {
                background-color: #303134;
                color: #e8eaed;
                border: 1px solid #5f6368;
                border-radius: 4px;
                padding: 8px 12px;
                font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 14px;
                height: 20px;
                min-height: 20px;
            }
            
            #promptField:focus {
                border: 1px solid #8ab4f8;
            }
            
            #promptField:disabled {
                background-color: #3c4043;
                color: #9aa0a6;
            }
        """)
    
    def set_up_tab_widget(self, tab_sections: dict):
        """Set up the tab widget with sections and sub-items."""
        self.tab_widget.setObjectName("contentTabs")
        
        # Add tabs for each section in the tab_sections dictionary
        for section_name, items in tab_sections.items():
            tab_content = QWidget()
            tab_content.setStyleSheet("""
                background-color: #202124;
                color: #ffffff;
            """)
            tab_layout = QVBoxLayout(tab_content)
            tab_layout.setContentsMargins(0, 0, 0, 0)
            tab_layout.setSpacing(0)
            
            # Create a list widget for the section items
            list_widget = QListWidget()
            list_widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
            list_widget.setObjectName(f"{section_name.lower()}List")
            list_widget.setStyleSheet("""
                QListWidget {
                    background-color: #202124;
                    border: none;
                    outline: none;
                }
                
                QListWidget::item {
                    padding: 16px;
                    border-bottom: 1px solid #5f6368;
                }
                
                QListWidget::item:hover {
                    background-color: #3c4043;
                }
                
                QListWidget::item:selected {
                    background-color: #202124;
                    color: #8ab4f8;
                }
            """)
            
            # Connect the list widget to the item click handler
            section_key = section_name
            list_widget.itemClicked.connect(lambda item, s=section_key: self.handle_item_click(s, item.text()))
            
            # Add each item to the list
            for item in items:
                list_item = QListWidgetItem(item)
                list_widget.addItem(list_item)
            
            # Store the list widget's scroll position
            self.tab_scroll_positions[section_name] = 0
            list_widget.verticalScrollBar().valueChanged.connect(
                lambda value, name=section_name: self.save_scroll_position(name, value)
            )
            
            # Add the list widget to the tab
            tab_layout.addWidget(list_widget)
            
            # Add the tab to the tab widget
            self.tab_widget.addTab(tab_content, section_name)
            
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.restore_scroll_position)

    def create_prompt_field(self):
        """Create a custom prompt text field at the bottom of the window."""
        prompt_container = QFrame()
        prompt_container.setObjectName("promptContainer")
        
        prompt_layout = QHBoxLayout(prompt_container)
        prompt_layout.setContentsMargins(10, 5, 10, 5)
        
        # Create text input field
        self.prompt_field = QLineEdit()
        self.prompt_field.setObjectName("promptField")
        self.prompt_field.setPlaceholderText("Enter your custom prompt...")
        self.prompt_field.returnPressed.connect(self.submit_custom_prompt)
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        if current_tab not in ["OpenAI", "Google Gemini"]:  # Disable for non-LLM tabs
            self.prompt_field.setEnabled(False)
        
        prompt_layout.addWidget(self.prompt_field)
        
        return prompt_container
        
    def update_prompt_field_state(self):
        """Enable or disable the prompt field based on the current tab."""
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        
        # Enable for LLM tabs, disable for others
        llm_tabs = ["OpenAI", "Google Gemini"]
        if current_tab in llm_tabs:
            self.prompt_field.setEnabled(True)
            self.prompt_field.setPlaceholderText(f"Enter your custom {current_tab} prompt...")
        else:
            self.prompt_field.setEnabled(False)
            self.prompt_field.setPlaceholderText("Custom prompts not available for this tab")
    
    def submit_custom_prompt(self):
        """Submit the custom prompt text."""
        prompt_text = self.prompt_field.text().strip()
        if not prompt_text:
            return
            
        current_index = self.tab_widget.currentIndex()
        current_tab = self.tab_widget.tabText(current_index)
        
        # Only process for enabled tabs
        if self.prompt_field.isEnabled() and prompt_text:
            # Convert tab name to section name (lowercase with underscores)
            section_name = current_tab.lower().replace(" ", "_")
            
            # Set the custom prompt flag
            self.is_custom_prompt_mode = True
            
            LOG.debug(f"CUSTOM_PROMPT_MODE: Activated for {section_name}")
            
            # Direct custom prompt handling
            self.handle_custom_prompt_directly(section_name, prompt_text)
            
            # Clear the prompt field
            self.prompt_field.clear()
            
            # Close the window after submitting
            self.close()
            
    def handle_custom_prompt_directly(self, section_name, prompt_text):
        """Directly emit the custom prompt signal with the correct parameters to prevent cross-wiring."""
        if not self.is_custom_prompt_mode:
            LOG.debug("CUSTOM_PROMPT_MODE: Not active, skipping custom prompt handling")
            return
            
        LOG.debug(f"CUSTOM_PROMPT_MODE: Emitting custom prompt for {section_name}")
        
        try:
            # Explicitly bypass any process_text_event signals
            self.custom_prompt_event.emit(section_name, "custom_prompt", prompt_text)
            LOG.debug("CUSTOM_PROMPT_MODE: Successfully emitted custom_prompt_event")
        finally:
            # Reset the flag regardless of outcome
            self.is_custom_prompt_mode = False
            
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events for window dragging"""
        # With standard title bar, this is handled by the system
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move events for window dragging"""
        # With standard title bar, this is handled by the system
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release events for window dragging"""
        # With standard title bar, this is handled by the system
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        current_index = self.tab_widget.currentIndex()
        current_widget = self.tab_widget.currentWidget()

        if event.key() == Qt.Key.Key_Escape:
            self.close()

        # Retrieve the QListWidget inside the current tab
        if current_widget:
            list_widget = current_widget.findChild(QListWidget)
            if list_widget and isinstance(list_widget, QListWidget):
                # If the current tab contains a QListWidget
                if event.key() == Qt.Key.Key_Up:
                    current_row = list_widget.currentRow()
                    new_row = max(0, current_row - 1)
                    list_widget.setCurrentRow(new_row)
                elif event.key() == Qt.Key.Key_Down:
                    current_row = list_widget.currentRow()
                    new_row = min(list_widget.count() - 1, current_row + 1)
                    list_widget.setCurrentRow(new_row)

                if event.key() == Qt.Key.Key_Return:
                    # Handle Enter key
                    current_item = list_widget.currentItem()  # Get the currently selected item
                    if current_item:
                        tab_name = self.tab_widget.tabText(current_index)
                        row_text = current_item.text()
                        self.handle_enter_key(tab_name, row_text, current_index)

                    else:
                        LOG.debug("No item selected in the current list.")
            else:
                LOG.debug("Current tab does not contain a QListWidget.")
        else:
            LOG.debug("No current widget in the tab.")

        # Handle Left and Right arrow keys to switch tabs
        if event.key() == Qt.Key.Key_Right:
            next_index = (current_index + 1) % self.tab_widget.count()
            self.tab_widget.setCurrentIndex(next_index)
        elif event.key() == Qt.Key.Key_Left:
            previous_index = (current_index - 1) % self.tab_widget.count()
            self.tab_widget.setCurrentIndex(previous_index)
        else:
            # Pass other key events to the parent class
            super().keyPressEvent(event)

    def handle_item_click(self, section_name: str, item_text: str):
        """Handle item click event."""
        LOG.debug(f"Item '{item_text}' clicked in section '{section_name}'")
        # Convert the display text (Title Case) back to function name (snake_case)
        function_name = item_text.lower().replace(" ", "_")
        section_name = section_name.lower().replace(" ", "_")
        # Emit the signal to process the text, passing an empty string for text
        # This will trigger the controller to handle the function execution
        self.process_text_event.emit(section_name, function_name, "")
        self.close()  # Close/hide the window after processing

    def handle_enter_key(self, tab_name: str, text_item: str, tab_index: int) -> None:
        """Close the window and trigger the processText function."""
        # Convert the display text (Title Case) back to
        #  function name (snake_case)
        function_name = text_item.lower().replace(" ", "_")
        tab_name = tab_name.lower().replace(" ", "_")
        # Emit the signal to process the text, passing an empty string for text
        # This will trigger the controller to handle the function execution
        self.process_text_event.emit(tab_name, function_name, "")
        self.close()  # Close the window

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event - hide instead of close to keep app running in system tray."""
        # Hide the window instead of closing it to prevent application shutdown
        event.ignore()
        self.hide()
        # Signal that the floating window is no longer visible
        self.windows_event.emit(False)

    def set_tab_visible(self, tab_name: str, visible: bool) -> None:
        """Set the visibility of a tab in the tab widget.
        
        Args:
            tab_name: The name of the tab to show/hide (config key format)
            visible: Whether to show or hide the tab
        """
        tab_name_to_index = {}
        
        # Build a mapping of tab names to indexes
        for i in range(self.tab_widget.count()):
            tab_title = self.tab_widget.tabText(i)
            
            # Convert UI tab title to config key format (lowercase with underscores)
            config_key = tab_title.lower().replace(" ", "_")
            tab_name_to_index[config_key] = i
            
            # Also add the raw tab title as a key for direct comparison
            tab_name_to_index[tab_title.lower()] = i
        
        # Debug logging to help diagnose the issue
        LOG.debug(f"Tab visibility request: '{tab_name}' -> {visible}")
        LOG.debug(f"Available tabs: {tab_name_to_index}")
        
        # If the tab exists, set its visibility
        if tab_name in tab_name_to_index:
            index = tab_name_to_index[tab_name]
            self.tab_widget.setTabVisible(index, visible)
            LOG.debug(f"Tab '{tab_name}' visibility set to {visible}")
        else:
            LOG.debug(f"Tab '{tab_name}' not found in tab widget")

    def hideEvent(self, event: QHideEvent) -> None:
        # Ensure the key listener flag is updated when the window is hidden
        self.windows_event.emit(False)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        # Ensure the window is focused when shown
        self.raise_()  # Raise the window to the top
        self.activateWindow()  # Make the window active (focused)

        self.windows_event.emit(True)

        self.event_put_app_focus.emit()

    def position_at_bottom_center(self) -> None:
        """Position the window at the bottom center of the current screen."""
        # Get the current cursor position to determine active screen
        cursor_pos = QCursor.pos()
        
        # Get all screens
        screens = QApplication.screens()
        active_screen = QApplication.primaryScreen()  # Default to primary screen
        
        # Find which screen contains the cursor
        for screen in screens:
            screen_geometry = screen.geometry()
            if screen_geometry.contains(cursor_pos):
                active_screen = screen
                break
        
        # Use available geometry to respect taskbars/docks
        screen_geometry = active_screen.availableGeometry()
        
        # Calculate the position for bottom center
        window_width = self.width()
        window_height = self.height()
        
        x = (screen_geometry.width() - window_width) // 2 + screen_geometry.x()
        # Position at bottom with some margin
        y = screen_geometry.height() - window_height - 50 + screen_geometry.y()
        
        # Set the window position
        self.setGeometry(x, y, window_width, window_height)
        LOG.debug(f"Window positioned at bottom center on active screen: ({x}, {y})")

    def save_scroll_position(self, section_name: str, scroll_position: int) -> None:
        """Save the scroll position of a section."""
        self.tab_scroll_positions[section_name] = scroll_position

    def restore_scroll_position(self) -> None:
        """Restore the scroll position of the current tab."""
        current_index = self.tab_widget.currentIndex()
        current_widget = self.tab_widget.currentWidget()
        
        if current_widget:
            list_widget = current_widget.findChild(QListWidget)
            if list_widget and isinstance(list_widget, QListWidget):
                tab_name = self.tab_widget.tabText(current_index)
                scroll_position = self.tab_scroll_positions.get(tab_name, 0)
                list_widget.verticalScrollBar().setValue(scroll_position)

    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
