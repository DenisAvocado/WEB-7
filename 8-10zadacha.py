import os
import sys
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic


API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"


def geocode(address):
    request = f'http://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={address}&format=json'
    response = requests.get(request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        return toponym_coodrinates


def full_adr(address):
    request = f'http://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={address}&format=json'
    response = requests.get(request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        try:
            post = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]['postal_code']
        except Exception:
            post = "Невозможно определить почтовый индекс"
        return toponym_address, post


def coords_to_address(coords):
    request = f'http://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={coords}&format=json'
    response = requests.get(request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        try:
            post = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]['postal_code']
        except Exception:
            post = "Невозможно определить почтовый индекс"
        return toponym_address, post


class YandexMaps(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('maps_2.ui', self)
        self.server = 'http://static-maps.yandex.ru/1.x/'
        self.request_params = {
            'll': '37.530887,55.703118',
            'spn': '0.005,0.005',
            'l': 'map',
            'size': '650,450'
        }
        self.image_update()
        self.map_btn.clicked.connect(self.map_format)
        self.sat_btn.clicked.connect(self.map_format)
        self.skl_btn.clicked.connect(self.map_format)
        self.search_btn.clicked.connect(self.search_request)
        self.delete_btn.clicked.connect(self.delete_marker)
        self.post_index.clicked.connect(self.post_index_state)
        self.map_btn.setFocusPolicy(Qt.NoFocus)
        self.sat_btn.setFocusPolicy(Qt.NoFocus)
        self.skl_btn.setFocusPolicy(Qt.NoFocus)
        self.search_btn.setFocusPolicy(Qt.NoFocus)
        self.delete_btn.setFocusPolicy(Qt.NoFocus)
        self.full_address.setFocusPolicy(Qt.NoFocus)
        self.post_index.setFocusPolicy(Qt.NoFocus)
        self.count = 0
        self.cur_post_state = 0

    def search_request(self, address):
        try:
            coords = geocode(address)
            address_out = full_adr(address)[0]
            if self.cur_post_state == 1:
                address += f"\n{full_adr(address)[1]}"
            self.full_address.setText(str(address))
            self.request_params["ll"] = ",".join(coords.split())
            self.request_params["pt"] = f"{','.join(coords.split())},vkbkm"
            self.image_update()
        except Exception:
            self.statusBar().showMessage("Некорректный запрос. Попробуйте еще раз.", 1000)

    def delete_marker(self):
        if "pt" in self.request_params:
            self.request_params.pop("pt")
        self.search_line.setText("")
        self.full_address.setText("")
        self.image_update()

    def image_update(self):
        response = requests.get(self.server, params=self.request_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(response.url)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.pixmap = QPixmap(self.map_file)
        self.map.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.scale_update('/')
        elif event.key() == Qt.Key_PageDown:
            self.scale_update('*')
        else:
            self.next_view(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if 651 > event.x() > 0 and 451 > event.y() > 0:
                x_spn = float(self.request_params['spn'].split(',')[0]) * 2.8 / 650 * event.x()
                y_spn = float(self.request_params['spn'].split(',')[1]) * 1.1 / 450 * (450 - event.y())
                x = float(self.request_params['ll'].split(',')[0]) - \
                    float(self.request_params['spn'].split(',')[0]) * 2.8 / 2
                y = float(self.request_params['ll'].split(',')[1]) - \
                    float(self.request_params['spn'].split(',')[1]) * 1.1 / 2
                self.request_params["pt"] = \
                    f"{x_spn + x},{y_spn + y},vkbkm"
                self.image_update()
                address = coords_to_address(f"{x_spn + x},{y_spn + y}")[0]
                if self.cur_post_state == 1:
                    address += f"\n{coords_to_address(f'{x_spn + x},{y_spn + y}')[1]}"
                self.full_address.setText(str(address))

        self.search_line.setEnabled(not self.search_line.isEnabled())

    def scale_update(self, action):
        new_scale = eval(f"{float(self.request_params['spn'].split(',')[0])}{action}2")
        if 0.0001562 < new_scale < 50:
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
            l1 -= spn * 2.8
        if event.key() == Qt.Key_Right:
            l1 += spn * 2.8
        if l2 >= 90 or l2 <= -90 or l1 >= 180 or l1 <= -180:
            l1, l2 = 37.617563, 55.755841
            self.request_params['ll'] = f'{str(l1)},{str(l2)}'
            self.image_update()
        else:
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

    def post_index_state(self):
        self.cur_post_state = (self.cur_post_state + 1) % 2
        if self.cur_post_state == 1:
            self.post_index.setStyleSheet("background-color: green")
        else:
            self.post_index.setStyleSheet("background-color: white")
        if self.full_address.toPlainText() != "":
            if self.search_line.text():
                self.search_request(self.search_line.text())
            elif self.full_address.toPlainText():
                self.search_request(self.full_address.toPlainText())

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
