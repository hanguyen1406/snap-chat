import sys
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget


class Worker(QThread):
    finished = pyqtSignal()  # Signal emitted when the task is finished
    progress = pyqtSignal(int)  # Signal emitted to report progress


    def run(self):
        """Long-running task"""
        for i in range(7):
            self.msleep(1000)  # Sleep for 1000 milliseconds (1 second)
            self.progress.emit(i + 1)  # Emit progress signal
        self.finished.emit()  # Emit finished signal when done


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('QThread Example with msleep')

        self.layout = QVBoxLayout()

        self.label = QLabel('Press the button to start the task', self)
        self.layout.addWidget(self.label)

        self.button = QPushButton('Start Task', self)
        self.button.clicked.connect(self.start_task)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def start_task(self):
        self.worker = Worker()
        self.worker.progress.connect(self.report_progress)
        self.worker.finished.connect(self.task_finished)
        self.worker.start()

    def report_progress(self, n):
        self.label.setText(f'Task progress: {n}')

    def task_finished(self):
        self.label.setText('Task finished')


def main():
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
