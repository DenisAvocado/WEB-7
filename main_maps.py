import os
import sys
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic


class YandexMaps(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('maps.ui', self)
        self.server = 'http://static-maps.yandex.ru/1.x/'
        self.request_params = {
            'll': '37.530887,55.703118',
            'z': '0',
            'l': 'map'
        }
        self.image_update()

    def image_update(self):
        response = requests.get(self.server, params=self.request_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(self.map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.pixmap = QPixmap(self.map_file)
        self.pixmap = self.pixmap.scaled(650, 450)
        self.map.setPixmap(self.pixmap)

    def scale_update(self, action):
        if ((0 < int(self.request_params['z']) and action == '-') or
                (21 > int(self.request_params['z']) and action == '+')):
            scaling = 1 if action == '+' else -1
            self.request_params['z'] = str(int(self.request_params['z']) + scaling)
            self.image_update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            self.scale_update('-')
        elif event.key() == Qt.Key_PageUp:
            self.scale_update('+')

    def closeEvent(self, event):
        os.remove(self.map_file)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YandexMaps()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
