import multiprocessing
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from .ppt_core import ppt_worker_process, PPTState

class PPTWorker(QObject):
    state_updated = pyqtSignal(object) # PPTState
    
    def __init__(self):
        super().__init__()
        self.cmd_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.process = None
        self.running = False
        
        # Timer to poll results from the queue
        self.poll_timer = QTimer()
        self.poll_timer.setInterval(50) # Poll every 50ms
        self.poll_timer.timeout.connect(self.check_results)

    def start(self):
        if self.running:
            return
            
        self.running = True
        self.process = multiprocessing.Process(
            target=ppt_worker_process, 
            args=(self.cmd_queue, self.result_queue),
            daemon=True
        )
        self.process.start()
        self.poll_timer.start()
        
    def check_results(self):
        if not self.running:
            return
            
        try:
            latest_state = None
            # Drain the queue of all pending updates to process ONLY the latest
            while not self.result_queue.empty():
                try:
                    msg_type, data = self.result_queue.get_nowait()
                    if msg_type == 'state_update':
                        latest_state = data
                except:
                    break
            
            if latest_state:
                state = PPTState(**latest_state)
                self.state_updated.emit(state)
        except:
            pass
                
    def request_state(self):
        self.cmd_queue.put({'type': 'check_state'})
        
    def next_slide(self):
        self.cmd_queue.put({'type': 'next'})
        self.request_state()
        
    def prev_slide(self):
        self.cmd_queue.put({'type': 'prev'})
        self.request_state()
        
    def goto_slide(self, index):
        self.cmd_queue.put({'type': 'goto', 'args': {'index': index}})
        self.request_state()
        
    def set_pointer_type(self, mode):
        self.cmd_queue.put({'type': 'set_pointer', 'args': {'mode': mode}})
        self.request_state()
        
    def set_pen_color(self, color):
        self.cmd_queue.put({'type': 'set_pen_color', 'args': {'color': color}})
        
    def erase_ink(self):
        self.cmd_queue.put({'type': 'erase_ink'})
        self.request_state()
        
    def exit_show(self, keep_ink=None):
        self.cmd_queue.put({'type': 'exit_show', 'args': {'keep_ink': keep_ink}})
        self.request_state()
        
    def stop(self):
        self.running = False
        self.poll_timer.stop()
        self.cmd_queue.put(None)
        if self.process:
            self.process.join(timeout=1)
            if self.process.is_alive():
                self.process.terminate()
