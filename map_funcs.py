import requests
import sys
import pygame
import os


API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'


def geocode(address):
    """Возвращает топоним с информацией об объекте"""
    geocoder_server = 'http://geocode-maps.yandex.ru/1.x/'
    geocoder_params = {
        'apikey': API_KEY,
        'geocode': address,
        'format': 'json'
    }
    response = requests.get(geocoder_server,
                            params=geocoder_params)
    if response:
        json_response = response.json()
    else:
        raise RuntimeError(f'Ошибка выполнения запроса: {geocoder_server}\n'
                           f'HTTP статус: {response.status_code} {response.reason}')
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return toponym[0]["GeoObject"] if toponym else None


def get_ll_spn(address):
    """Возвращает долготу и широту объекта и размеры обзора"""
    toponym = geocode(address)
    if not toponym:
        return None, None

    ll = ",".join(toponym["Point"]["pos"].split())

    envelop = toponym["boundedBy"]["Envelope"]
    min_x, min_y = envelop["lowerCorner"].split()
    max_x, max_y = envelop["upperCorner"].split()

    dx = float(max_x) - float(min_x)
    dy = float(max_y) - float(min_y)
    return ll, f"{dx},{dy}"


def get_coordinates(address):
    """Возвращает широту и долготу объекта"""
    toponym = geocode(address)
    if not toponym:
        return None, None
    else:
        longitude, latitude = toponym["Point"]["pos"].split()
        return float(longitude), float(latitude)


def get_address_component(name_location, index=0):
    """Возвращает адрес объекта"""
    toponym = geocode(name_location)
    if not toponym:
        return None

    components = toponym['metaDataProperty']['GeocoderMetaData']['Address']['Components']
    return components[index]['name']


