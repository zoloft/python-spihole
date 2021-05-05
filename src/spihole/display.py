import queue
import threading

from PIL import Image

from . import lcd

LCD_SIZE = lcd.LCD_WIDTH, lcd.LCD_HEIGHT


class Display(threading.Thread):
    def __init__(self) -> None:
        super().__init__()
        self._data_queue = queue.Queue()
        self._stop_evt = threading.Event()
        self._lcd = lcd.LCD()
        self._lcd.LCD_Init(lcd.SCAN_DIR_DFT)
        self._lcd.LCD_Clear()
        self._lcd.LCD_Off()

    def on_data(self, data: bytes):
        self._data_queue.put(data)

    def run(self):
        self._lcd.LCD_On()
        while not self._stop_evt.is_set():
            try:
                data = self._data_queue.wait(5)
                self._display(data)
            except queue.Empty:
                pass

    def stop(self):
        self._stop_evt.set()

    def _display(self, data: bytes):
        image = Image.open(data)
        image.thumbnail(LCD_SIZE)
        self._lcd.LCD_ShowImage(image, 0, 0)
