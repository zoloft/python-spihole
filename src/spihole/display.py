import io
import logging
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
        self._background = Image.new('RGBA', LCD_SIZE, (0, 0, 0, 0))
        self._displaying = False

    def on_data(self, data: bytes):
        if self._displaying:
            logging.debug('Previous image is still being rendered, skipping data')
            return
        self._data_queue.put(data)

    def run(self):
        self._lcd.LCD_On()
        while not self._stop_evt.is_set():
            try:
                data = self._data_queue.get(30)
                self._displaying = True
                self._display(data)
            except queue.Empty:
                pass
            finally:
                self._displaying = False

    def stop(self):
        self._stop_evt.set()

    def _display(self, data: bytes):
        image = Image.open(io.BytesIO(data))
        image.thumbnail(LCD_SIZE)
        position = (int((LCD_SIZE[0] - image.size[0]) / 2), int((LCD_SIZE[1] - image.size[1]) / 2))
        self._background.paste(image, position)
        self._lcd.LCD_ShowImage(self._background, 0, 0)
        logging.debug('Image Rendered')
