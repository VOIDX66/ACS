import threading


class ReadWriteLock:
    def __init__(self):
        self._cond = threading.Condition()
        self._readers = 0
        self._writers_waiting = 0
        self._writing = False

    def acquire_read(self):
        with self._cond:
            while self._writing or self._writers_waiting > 0:
                self._cond.wait()
            self._readers += 1

    def release_read(self):
        with self._cond:
            self._readers -= 1
            if self._readers == 0:
                self._cond.notify_all()

    def acquire_write(self):
        with self._cond:
            self._writers_waiting += 1
            while self._writing or self._readers > 0:
                self._cond.wait()
            self._writers_waiting -= 1
            self._writing = True

    def release_write(self):
        with self._cond:
            self._writing = False
            self._cond.notify_all()
