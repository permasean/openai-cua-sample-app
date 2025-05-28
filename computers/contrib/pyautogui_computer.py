import pyautogui
import base64
import time
from typing import List, Dict
from PIL import Image
import io

class PyAutoGUIComputer:
    """
    A computer implementation that uses PyAutoGUI to control the local machine.
    This allows the model to interact with your desktop environment directly.
    """

    def get_environment(self):
        return "mac"  # PyAutoGUI will work on any OS, but we'll return the current OS

    def get_dimensions(self):
        return pyautogui.size()

    def __init__(self):
        # Set up PyAutoGUI safety features
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.1  # Add small delay between actions

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def screenshot(self) -> str:
        """Capture the screen and return as base64 encoded PNG."""
        screenshot = pyautogui.screenshot()
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return base64.b64encode(img_byte_arr).decode('utf-8')

    def click(self, x: int, y: int, button: str = "left") -> None:
        """Click at the specified coordinates."""
        button_map = {
            "left": "left",
            "right": "right",
            "middle": "middle"
        }
        pyautogui.click(x=x, y=y, button=button_map.get(button, "left"))

    def double_click(self, x: int, y: int) -> None:
        """Double click at the specified coordinates."""
        pyautogui.doubleClick(x=x, y=y)

    def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        """Scroll at the specified coordinates."""
        pyautogui.moveTo(x, y)
        pyautogui.scroll(scroll_y)  # PyAutoGUI only supports vertical scrolling

    def type(self, text: str) -> None:
        """Type the specified text."""
        pyautogui.write(text)

    def wait(self, ms: int = 1000) -> None:
        """Wait for the specified number of milliseconds."""
        time.sleep(ms / 1000)

    def move(self, x: int, y: int) -> None:
        """Move the mouse to the specified coordinates."""
        pyautogui.moveTo(x, y)

    def keypress(self, keys: List[str]) -> None:
        """Press the specified keys."""
        # PyAutoGUI uses different key names, so we'll map them
        key_map = {
            "ctrl": "ctrl",
            "alt": "alt",
            "shift": "shift",
            "cmd": "command",
            "win": "win",
            "enter": "enter",
            "esc": "esc",
            "tab": "tab",
            "space": "space",
            "backspace": "backspace",
            "delete": "delete",
            "up": "up",
            "down": "down",
            "left": "left",
            "right": "right"
        }
        mapped_keys = [key_map.get(key.lower(), key) for key in keys]
        pyautogui.hotkey(*mapped_keys)

    def drag(self, path: List[Dict[str, int]]) -> None:
        """Drag the mouse along the specified path."""
        if not path:
            return
        start_x = path[0]["x"]
        start_y = path[0]["y"]
        pyautogui.moveTo(start_x, start_y)
        pyautogui.mouseDown()
        for point in path[1:]:
            pyautogui.moveTo(point["x"], point["y"])
        pyautogui.mouseUp()

    def get_current_url(self) -> str:
        """Not applicable for desktop environment."""
        return None 