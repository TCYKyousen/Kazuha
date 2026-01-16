from PySide6.QtCore import QObject, QTimer, Signal, Slot

class TimerManager(QObject):
    updated = Signal(int)  # remaining seconds
    finished = Signal()
    state_changed = Signal(bool) # is_running

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TimerManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        self.remaining_seconds = 0
        self.is_running = False
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._tick)

    @Slot(int)
    def start(self, seconds):
        self.remaining_seconds = float(seconds)
        self.is_running = True
        self.timer.start()
        self.state_changed.emit(True)
        self.updated.emit(int(self.remaining_seconds))

    @Slot()
    def pause(self):
        self.is_running = False
        self.timer.stop()
        self.state_changed.emit(False)

    @Slot()
    def resume(self):
        if self.remaining_seconds > 0:
            self.is_running = True
            self.timer.start()
            self.state_changed.emit(True)

    @Slot()
    def stop(self):
        self.remaining_seconds = 0
        self.is_running = False
        self.timer.stop()
        self.state_changed.emit(False)
        self.updated.emit(0)

    @Slot()
    def finish(self):
        should_emit = self.is_running or self.remaining_seconds > 0
        self.stop()
        if should_emit:
            self.finished.emit()

    def _tick(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 0.1
            if self.remaining_seconds <= 0:
                self.remaining_seconds = 0
                self.stop()
                self.finished.emit()
            else:
                self.updated.emit(int(self.remaining_seconds))
        else:
            self.stop()

    def get_remaining_time_str(self):
        val = int(self.remaining_seconds)
        hours = val // 3600
        minutes = (val % 3600) // 60
        seconds = val % 60
        if hours > 0:
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return f"{minutes:02}:{seconds:02}"
