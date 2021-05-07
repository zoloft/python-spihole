try:
    import picamera
except ImportError:
    import fake_rpi.picamera as picamera

import io
import threading
import time

from .hub import Hub
from .hub import HubMessage
from .hub import HubMessageType


class Capture(threading.Thread):
    def __init__(self, hub: Hub) -> None:
        super().__init__()
        self.daemon = True
        self.camera: picamera.PiCamera
        self._stop_evt = threading.Event()
        self._data_queue = hub.bus
        hub.add_subscriber(self)
        self._message = HubMessage(HubMessageType.DATA, bytes())

    def run(self) -> None:
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1920, 1080)
        self.camera.framerate = 30
        self.camera.rotation = 90
        time.sleep(2)  # camera initialization
        stream = io.BytesIO()
        for _ in self.camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            try:
                stream.seek(0)
                self._message.content = stream.read()
                self._data_queue.put_nowait(self._message)
            except Exception:
                pass
            finally:
                stream.seek(0)
                stream.truncate()
            if self._stop_evt.is_set():
                break
        self.camera.close()
        self._stop_evt.clear()

    def stop(self) -> None:
        self._stop_evt.set()
        self.join()

    def on_message(self, message: HubMessage):
        if message.type == HubMessageType.EVENT:
            pass
