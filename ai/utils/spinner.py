"""
Spinner animation for terminal feedback during operations
"""

import sys
import time
import threading
from .colors import Colors
from ..constants import SPINNER_FRAMES, SPINNER_MESSAGES

class Spinner:
    """An enhanced spinner class with a smooth animation"""
    def __init__(self):
        self.spinning = False
        self.frames = SPINNER_FRAMES
        self.loading_messages = SPINNER_MESSAGES
        self.spinner_idx = 0
        self.message_idx = 0
        self.dots = 0
        self.message_update_counter = 0
        self.thread = None

    def spin(self):
        """Main animation function for the spinner thread"""
        while self.spinning:
            if self.message_update_counter % 20 == 0:
                self.message_idx = (self.message_idx + 1) % len(self.loading_messages)
                self.dots = 0

            if self.message_update_counter % 5 == 0:
                self.dots = (self.dots + 1) % 4

            message = self.loading_messages[self.message_idx]
            dots = "." * self.dots
            spaces = " " * (3 - self.dots)

            spinner = self.frames[self.spinner_idx]
            line = f"\r{Colors.ORANGE}{spinner} {message}{dots}{spaces}{Colors.RESET}"

            sys.stdout.write(line)
            sys.stdout.flush()

            self.spinner_idx = (self.spinner_idx + 1) % len(self.frames)
            self.message_update_counter += 1
            time.sleep(0.1)

        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()

    def start(self):
        """Start the spinner animation in a separate thread"""
        self.spinning = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()

    def stop(self):
        """Stop the spinner animation"""
        self.spinning = False
        if hasattr(self, 'thread') and self.thread is not None:
            self.thread.join()
