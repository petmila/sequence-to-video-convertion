import sys

from PyQt5.QtWidgets import QApplication, QVBoxLayout, QMainWindow, QFileDialog, QLabel, \
    QMessageBox, QWidget, QPushButton, QHBoxLayout

import ffmpeg
import os


class MainWindow(QMainWindow):
    """
    Window with GUI
    """
    def __init__(self):
        super().__init__()
        self.sequences = {}
        self.save_dir_path = None
        self.source_dir_path = None

        self.button_open = QPushButton("Выбрать путь к директории секвенций", self)
        self.button_open.clicked.connect(self.get_source_dir_path)
        self.label_open = QLabel("")
        h_open_layout = QHBoxLayout()
        h_open_layout.addWidget(self.button_open)
        h_open_layout.addWidget(self.label_open)

        self.button_save = QPushButton("Выбрать путь для сохранения видео", self)
        self.button_save.clicked.connect(self.get_save_dir_path)
        self.label_save = QLabel("")
        h_save_layout = QHBoxLayout()
        h_save_layout.addWidget(self.button_save)
        h_save_layout.addWidget(self.label_save)

        self.button_convert = QPushButton("Конвертировать", self)
        self.button_convert.clicked.connect(self.convert_selected_sequences)
        self.label_convert = QLabel("")
        h_convert_layout = QHBoxLayout()
        h_convert_layout.addWidget(self.button_convert)
        h_convert_layout.addWidget(self.label_convert)

        vlayout = QVBoxLayout()
        vlayout.addLayout(h_open_layout)
        vlayout.addLayout(h_save_layout)
        vlayout.addLayout(h_convert_layout)

        self.widget = QWidget()
        self.widget.setLayout(vlayout)
        self.setCentralWidget(self.widget)

        self.setWindowTitle('Конвертация секвенций в видео')
        self.show()

    def convert_selected_sequences(self) -> None:
        """
        Going through all sets of sequences and calling self.convert_sequence method
        Changing self.label_convert.text if converted successfully
        :return: None
        """
        if self.save_dir_path is None or self.source_dir_path is None:
            msg = QMessageBox()
            msg.setWindowTitle("Ошибка")
            msg.setText("Выберите директории, пожалуйста")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        else:
            self.get_sequence_names(self.source_dir_path)
            for sequence_name in self.sequences.keys():
                self.convert_sequence(sequence_name)

            self.label_convert.setText("Конвертация успешно завершена")

    def get_source_dir_path(self) -> None:
        """
        Get path to the directory there sequences are stored
        Using QFileDialog
        :return: None
        """
        self.label_convert.setText("")
        self.source_dir_path = QFileDialog.getExistingDirectory(options=QFileDialog.ShowDirsOnly)
        self.label_open.setText(self.source_dir_path)

    def get_save_dir_path(self) -> None:
        """
        Get path to the directory for saving output
        Using QFileDialog
        :return: None
        """
        self.label_convert.setText("")
        self.save_dir_path = QFileDialog.getExistingDirectory(options=QFileDialog.ShowDirsOnly)
        self.label_save.setText(self.save_dir_path)

    def get_sequence_names(self, path: str) -> None:
        """
        Recursively searches through and defines sequences in a given path
        :param path: path to directory, where we currently look for sequenced
        :return: None
        """
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                self.get_sequence_names(full_path)
            else:
                fname, fextention = os.path.splitext(item)
                if fextention == '.jpg':
                    padding_length = len([d for d in fname[::-1] if d.isdigit()])
                    if (common_name := fname[:len(fname) - padding_length]) not in self.sequences:
                        self.sequences[common_name] = os.path.join(path, f"{common_name}%{padding_length}d.jpg")

    def convert_sequence(self, sequence_name: str) -> None:
        """
        Convert one set of sequences into one video
        :param sequence_name: common part of filename that defines sequences of one video
        :return: None
        """
        output_path = os.path.join(self.save_dir_path, f'{sequence_name}.mov')
        ffmpeg.input(self.sequences[sequence_name], framerate=24).output(output_path, vcodec='mjpeg')\
            .run(overwrite_output=True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    main = MainWindow()
    sys.exit(app.exec_())
