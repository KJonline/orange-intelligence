class FloatingWindowStyleOptions:
    geometry = "200, 200, 400, 300"

    title = "Orange GUI"

    base = """
        QWidget {
            background-color: #202124; 
            ##border: 1px solid #5f6368;
            ##border-radius: 6px;
            padding: 0;
            color: #ffffff;
        }
        
        QMainWindow, QDialog {
            background-color: #202124;
            ##border-radius: 6px;
            color: #ffffff;
        }
        
        /* Title bar styling to mimic modern macOS/Google Cloud console */
        #titleBar {
            background-color: #202124;
            color: #ffffff;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            height: 36px;
            min-height: 36px;
            max-height: 36px;
        }
        
        /* Traffic light buttons (close, minimize, maximize) */
        #closeButton {
            background-color: #ff5f57;
            border-radius: 6px;
            min-width: 12px;
            min-height: 12px;
            max-width: 12px;
            max-height: 12px;
            margin: 12px 4px 12px 8px;
            border: none;
        }
        
        #minimizeButton {
            background-color: #ffbd2e;
            border-radius: 6px;
            min-width: 12px;
            min-height: 12px;
            max-width: 12px;
            max-height: 12px;
            margin: 12px 4px;
            border: none;
        }
        
        #maximizeButton {
            background-color: #28c941;
            border-radius: 6px;
            min-width: 12px;
            min-height: 12px;
            max-width: 12px;
            max-height: 12px;
            margin: 12px 4px;
            border: none;
        }
        
        #closeButton:hover, #minimizeButton:hover, #maximizeButton:hover {
            opacity: 0.8;
        }
        
        #windowTitle {
            color: #ffffff;
            font-weight: 500;
            font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            font-size: 13px;
        }
    """

    tab_widget = """
        QTabWidget::pane { 
            border: none; 
            background: #202124; 
        }
        QTabBar {
            background: #202124;
            border-bottom: 1px solid #5f6368;
        }
        QTabBar::tab { 
            background: #303134; 
            border: none; 
            padding: 10px 16px; 
            margin: 0; 
            color: #e8eaed;
            font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            font-size: 13px;
        }
        QTabBar::tab:selected { 
            color: #8ab4f8;
            border-bottom: 2px solid #8ab4f8;
            font-weight: 500; 
        }
        QTabBar::tab:hover:!selected { 
            background: #3c4043; 
        }
    """

    search_bar = """
        QLineEdit { 
            background-color: #303134; 
            border: 1px solid #5f6368; 
            border-radius: 4px; 
            padding: 8px 12px; 
            margin: 8px 10px; 
            font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            font-size: 13px;
            color: #e8eaed;
        }
        
        QLineEdit:focus {
            border: 1px solid #8ab4f8;
            background-color: #303134;
        }
        
        QLineEdit::placeholder {
            color: #9aa0a6;
        }
    """

    list_widget = """
        QListWidget { 
            background-color: #202124; 
            ##border: 1px solid #5f6368; 
            ##border-radius: 4px; 
            margin: 10px; 
            font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }
        QListWidget::item { 
            padding: 10px 12px; 
            font-size: 13px; 
            color: #e8eaed;
            border-bottom: 1px solid #5f6368;
        }
        QListWidget::item:selected { 
            background-color: #3c4043; 
            color: #8ab4f8; 
            font-weight: 500; 
            border-left: 3px solid #8ab4f8;
        }
        QListWidget::item:hover:!selected { 
            background-color: #3c4043; 
        }
        
        /* Modern scrollbar */
        QScrollBar:vertical {
            border: none;
            background: #303134;
            width: 8px;
            margin: 0px 0px 0px 0px;
        }
        
        QScrollBar::handle:vertical {
            background: #5f6368;
            border-radius: 4px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #7d8084;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            border: none;
            background: #303134;
            height: 8px;
            margin: 0px 0px 0px 0px;
        }
        
        QScrollBar::handle:horizontal {
            background: #5f6368;
            border-radius: 4px;
            min-width: 30px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background: #7d8084;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        QPushButton {
            background-color: #1a73e8;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            font-size: 13px;
            font-weight: 500;
        }
        
        QPushButton:hover {
            background-color: #1765c9;
        }
        
        QPushButton:pressed {
            background-color: #185abc;
        }
    """
