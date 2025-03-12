import logging.config
import sys

from core.config_manager import get_logging_config
from PyQt6.QtWidgets import QApplication
from utils import avoid_dock_macos_icon

from core.controller import Controller


def main():
    # Configure logging using the config manager
    logging.config.dictConfig(get_logging_config())

    app = QApplication(sys.argv)

    avoid_dock_macos_icon()

    # Create the controller with the new signature
    controller = Controller(app=app)

    # Run the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
