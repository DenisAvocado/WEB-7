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
            'spn': '0.005,0.005',
            'l': 'map'
        }
        self.image_update()
        self.map_btn.clicked.connect(self.map_format)
        self.sat_btn.clicked.connect(self.map_format)
        self.skl_btn.clicked.connect(self.map_format)
        self.map_btn.setEnabled(False)
        self.sat_btn.setEnabled(False)
        self.skl_btn.setEnabled(False)
        self.count = 0

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
        self.map.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            self.scale_update('/')
        elif event.key() == Qt.Key_PageUp:
            self.scale_update('*')
        else:
            self.next_view(event)

    def mousePressEvent(self, event):
        if self.count % 2 == 0:
            self.map_btn.setEnabled(True)
            self.sat_btn.setEnabled(True)
            self.skl_btn.setEnabled(True)
        else:
            self.map_btn.setEnabled(False)
            self.sat_btn.setEnabled(False)
            self.skl_btn.setEnabled(False)
        self.count += 1

    def scale_update(self, action):
        new_scale = eval(f"{float(self.request_params['spn'].split(',')[0])}{action}2")
        if 0.0001562 < new_scale < 90:
            self.request_params['spn'] = f'{new_scale},{new_scale}'
            self.image_update()

    def next_view(self, event):
        l1, l2 = [float(l) for l in self.request_params['ll'].split(',')]
        spn = float(self.request_params['spn'].split(',')[0])
        if event.key() == Qt.Key_Up:
            l2 += spn * 1.1
        if event.key() == Qt.Key_Down:
            l2 -= spn * 1.1
        if event.key() == Qt.Key_Left:
            l1 -= spn * 2.6
        if event.key() == Qt.Key_Right:
            l1 += spn * 2.6
        self.request_params['ll'] = f'{str(l1)},{str(l2)}'
        self.image_update()

    def map_format(self):
        if self.sender().objectName() == 'map_btn':
            self.request_params['l'] = 'map'
        elif self.sender().objectName() == 'sat_btn':
            self.request_params['l'] = 'sat'
        elif self.sender().objectName() == 'skl_btn':
            self.request_params['l'] = 'sat,skl'
        self.image_update()

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
