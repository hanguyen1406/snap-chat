import sys
import time
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QThread, pyqtSignal, QWaitCondition, QMutex

class Worker(QThread):
    update_label = pyqtSignal(int)

    wait_condition = QWaitCondition()
    mutex = QMutex()
    current_thread_id = 0

    def __init__(self, thread_id, total_threads):
        super().__init__()
        self.thread_id = thread_id
        self.total_threads = total_threads
        self.counter = thread_id

    def run(self):
        while True:
            Worker.mutex.lock()
            while Worker.current_thread_id != self.thread_id:
                Worker.wait_condition.wait(Worker.mutex)
            self.update_label.emit(self.counter)
            self.counter += self.total_threads
            Worker.current_thread_id = (Worker.current_thread_id + 1) % self.total_threads
            Worker.mutex.unlock()
            Worker.wait_condition.wakeAll()
            time.sleep(2)  # Sleep for 2 seconds before allowing the next thread to proceed

class AppDemo(QWidget):
    def __init__(self, num_threads):
        super().__init__()
        self.num_threads = num_threads

        self.setWindowTitle('Thread Display')
        self.setGeometry(100, 100, 400, 200)
        
        layout = QVBoxLayout()
        self.labels = []

        for i in range(num_threads):
            label = QLabel(f'Thread {i + 1}: Waiting...', self)
            layout.addWidget(label)
            self.labels.append(label)

        self.setLayout(layout)

        self.threads = []
        for i in range(num_threads):
            thread = Worker(i, num_threads)
            thread.update_label.connect(self.update_label)
            thread.start()
            self.threads.append(thread)
            

    def update_label(self, value):
        thread_id = value % self.num_threads
        self.labels[thread_id].setText(f'Thread {thread_id + 1}: {value}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = AppDemo(4)
    demo.show()
    sys.exit(app.exec())
