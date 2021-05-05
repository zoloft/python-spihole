try:
    import picamera
except ImportError:
    import fake_rpi.picamera as picamera

import io
import queue
import threading
import time


class Capture(threading.Thread):
    def __init__(self, data_queue: queue.Queue) -> None:
        super().__init__()
        self.daemon = True
        self.camera = picamera.PiCamera()
        self._stop_evt = threading.Event()
        self._data_queue = data_queue

    def run(self) -> None:
        self.camera.resolution = (1920, 1080)
        self.camera.framerate = 30
        time.sleep(2)  # camera initialization
        stream = io.BytesIO()
        for _ in self.camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            try:
                stream.seek(0)
                self._data_queue.put_nowait(stream.read())
                print("==== TELL: %d", stream.tell())
            except Exception:
                pass
            finally:
                stream.seek(0)
                stream.truncate()
            if self._stop_evt.is_set():
                break
        self.camera.close()

    def stop(self) -> None:
        self._stop_evt.set()
