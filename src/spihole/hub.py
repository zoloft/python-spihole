import queue
import threading
from abc import ABCMeta


class HubSubscriber(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return hasattr(subclass, 'on_data') and callable(subclass.on_data) or NotImplemented


class Hub(threading.Thread):
    def __init__(self) -> None:
        super().__init__()
        self._subscribers = set()
        self._bus = queue.Queue()
        self._stop_evt = threading.Event()

    def add_subscriber(self, subscriber: HubSubscriber):
        if not isinstance(subscriber, HubSubscriber):
            raise ValueError('Bad interface')
        self._subscribers.add(subscriber)

    def run(self) -> None:
        while not self._stop_evt.is_set():
            try:
                data = self._bus.get(5)
                self._distribute(data)
            except queue.Empty:
                pass

    def stop(self) -> None:
        self._stop_evt.set()

    def _distribute(self, data: bytes) -> None:
        subscriber: HubSubscriber
        for subscriber in self._subscribers:
            subscriber.on_data(data)

    @property
    def bus(self):
        return self._bus
