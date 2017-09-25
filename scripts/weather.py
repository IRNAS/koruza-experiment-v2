from __future__ import print_function

import re
import time

import requests

import common


class WeatherStationAPI(object):
    """Weather station API."""
    INPUT_REGEX = re.compile(r'<input.*?name="(.+?)".*?value="(.+?)".*?>')

    def __init__(self, host, port=80, path='/livedata.htm'):
        """Construct API instance."""
        self.host = host
        self.port = port
        self.path = path

    def _parse(self, value):
        try:
            return float(value)
        except ValueError:
            return None

    def update(self):
        """Update from remote feed."""
        response = requests.get('http://{}:{}{}'.format(self.host, self.port, self.path))
        data = dict(self.INPUT_REGEX.findall(response.text))
        return {
            'timestamp': data.get('CurrTime', None),
            'outdoor': {
                'humidity': self._parse(data.get('outHumi', None)),
                'temperature': self._parse(data.get('outTemp', None)),
            },
            'indoor': {
                'humidity': self._parse(data.get('inHumi', None)),
                'temperature': self._parse(data.get('inTemp', None)),
            },
            'wind': {
                'direction': self._parse(data.get('windir', None)),
                'speed': self._parse(data.get('avgwind', None)),
                'gust': self._parse(data.get('gustspeed', None)),
            },
            'uv': self._parse(data.get('uv', None)),
            'uvi': self._parse(data.get('uvi', None)),
            'rain': self._parse(data.get('rainofhourly', None)),
        }


def push(data):
    """Submit data to nodewatcher instance."""
    body = {
        'sensors.generic': {
            '_meta': {'version': 1},
            'weather_indoor_humidity': {
                'name': 'Indoor Humidity',
                'unit': '%',
                'value': data['indoor']['humidity'],
                'group': 'weather_humidity',
            },
            'weather_indoor_temperature': {
                'name': 'Indoor Temperature',
                'unit': 'C',
                'value': data['indoor']['temperature'],
                'group': 'weather_temperature',
            },
            'weather_outdoor_humidity': {
                'name': 'Outdoor Humidity',
                'unit': '%',
                'value': data['outdoor']['humidity'],
                'group': 'weather_humidity',
            },
            'weather_outdoor_temperature': {
                'name': 'Outdoor Temperature',
                'unit': 'C',
                'value': data['outdoor']['temperature'],
                'group': 'weather_temperature',
            },
            'weather_wind_direction': {
                'name': 'Wind Direction',
                'unit': 'deg',
                'value': data['wind']['direction'],
            },
            'weather_wind_speed': {
                'name': 'Wind Speed',
                'unit': 'km/h',
                'value': data['wind']['speed'],
                'group': 'weather_wind_speed',
            },
            'weather_wind_gust': {
                'name': 'Wind Gust',
                'unit': 'km/h',
                'value': data['wind']['gust'],
                'group': 'weather_wind_speed',
            },
            'weather_uv': {
                'name': 'UV',
                'unit': '',
                'value': data['uv'],
            },
            'weather_uv_index': {
                'name': 'UV Index',
                'unit': '',
                'value': data['uvi'],
            },
            'weather_rain': {
                'name': 'Rain',
                'unit': '',
                'value': data['rain'],
            },
        }
    }

    for sensor_id, value in list(body['sensors.generic'].items()):
        if 'value' not in value:
            continue

        if value['value'] is None:
            del body['sensors.generic'][sensor_id]

    common.nodewatcher_push(common.get_config('weather.uuid'), body)

if __name__ == '__main__':
    print('KORUZA Experiment: Weather reporting script.')
    print('Configured host: {}'.format(common.get_config('weather.host')))
    print('Configured UUID: {}'.format(common.get_config('weather.uuid')))

    api = WeatherStationAPI(common.get_config('weather.host'))

    while True:
        try:
            data = api.update()
            push(data)
        except:
            pass

        time.sleep(60)
