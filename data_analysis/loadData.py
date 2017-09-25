#!/usr/bin/python
'''
KORUZA experiment v2 - batch measurement download
Copyright (C) 2017  Institute IRNAS Rače <info@irnas.eu>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import urllib
import json
import os
import csv

# GLOBAL VARIABLES======================================================================================================
# Test name
test_name = 'test2'
# Create new file
if not os.path.exists(test_name):
    os.makedirs(test_name)

# Define data granularity
granularity = 'minutes'
# Define data limits
limit = '100000'
# Start timestamp
start = '<START>'
# End timestamp
end = '<STOP>'

# Number of used sensors
n_sensor = 18
# Define unit sensor names
ID_name = ['accel_x_range1_maximum',
           'accel_x_range2_maximum',
           'accel_x_range3_maximum',
           'accel_x_range4_maximum',
           'accel_y_range1_maximum',
           'accel_y_range2_maximum',
           'accel_y_range3_maximum',
           'accel_y_range4_maximum',
           'accel_z_range1_maximum',
           'accel_z_range2_maximum',
           'accel_z_range3_maximum',
           'accel_z_range4_maximum',
           'rx_power_dbm',
           'rx_power_dbm_minimum',
           'rx_power_dbm_maximum',
           'rx_power_variance',
           'temperature',
           'value']

# Number of Koruza units
n_unit = 2
# Define Koruza units ID
unit_ID = ['<UNIT 1 ID>',
           '<UNIT 2 ID>'
           ]

# Define unit names
unit_name = ['<UNIT 1 NAME>',
             '<UNIT 2 NAME>',
             ]

# Define weather station ID
weather_id = '<WS ID>'

# Number of weather station used sensors
n_weather = 6
# define weather station sensor id names
weather_name = ['weather_indoor_humidity',
                'weather_outdoor_humidity',
                'weather_wind_speed',
                'weather_outdoor_temperature',
                'weather_indoor_temperature',
                'weather_uv'
                ]

#CLASSES================================================================================================================
# Koruza Unit
class KoruzaUnit:
    def __init__(self, ID, name):
        self.name = name
        self.ID = ID
        self.sensor_ID = get_id(self.ID)
        self.ctn = False
        if self.sensor_ID:
            self.ctn = True

    def run(self):
        if self.ctn:
            # Open new JSON file
            ful_path = test_name + '/' + self.name
            if not os.path.exists(ful_path):
                os.makedirs(ful_path)
            # Print data to files
            for i in range(0,n_sensor,1):
                # Define sensor URL
                url = "https://kw.koruza.net/api/v1/stream/%s/?granularity=%s&limit=%s&value_downsamplers=min&value_downsamplers=mean&value_downsamplers=max&time_downsamplers=mean&start=%s&end=%s&format=json" %(self.sensor_ID[i], granularity, limit, start, end)
                # Filenames for json and csv files
                filename_json = ful_path + '/' + self.name + ID_name[i] + '.json'
                filename_csv = ful_path + '/' + self.name + ID_name[i] + '.csv'
                # Save Json to file
                if urllib.urlretrieve(url, filename_json):
                    print ("Saved %s for unit %s " % (ID_name[i], self.name))
                    # Open json file and convert it to csv
                    json_data = open(filename_json)
                    json_parsed = json.load(json_data)
                    json_parsed_datapoints = json_parsed["datapoints"]

                    with open(filename_csv, 'wb+') as f:
                        dict_writer = csv.DictWriter(f, fieldnames=['t', 'v'])
                        dict_writer.writeheader()
                        dict_writer.writerows(json_parsed_datapoints)

                    del json_data, json_parsed, json_parsed_datapoints
                else:
                    print ("ERROR saving %s for unit %s !" % (ID_name[i], self.name))

# Weather station
class WeatherUnit:
    def __init__(self, ID):
        self.name = 'WeatherStation'
        self.ID = ID
        self.ctn = False
        self.sensor_ID = get_weather_id(self.ID)
        if self.sensor_ID:
            self.ctn = True

    def run(self):
        if self.ctn:
            # Open new file
            ful_path = test_name + '/' + self.name
            if not os.path.exists(ful_path):
                os.makedirs(ful_path)
            # Print data
            for i in range(0,n_weather,1):
                url = "https://kw.koruza.net/api/v1/stream/%s/?granularity=%s&limit=%s&value_downsamplers=min&value_downsamplers=mean&value_downsamplers=max&time_downsamplers=mean&start=%s&end=%s&format=json" %(self.sensor_ID[i], granularity, limit, start, end)
                filename_json = ful_path + '/' + self.name + weather_name[i] + '.json'
                filename_csv = ful_path + '/' + self.name + weather_name[i] + '.csv'
                # Save Json to file
                if urllib.urlretrieve(url, filename_json):
                    print ("Saved %s for weather station" % (weather_name[i]))
                    # Open json file and convert it to csv
                    json_data = open(filename_json)
                    json_parsed = json.load(json_data)
                    json_parsed_datapoints = json_parsed["datapoints"]

                    with open(filename_csv, 'wb+') as f:
                        dict_writer = csv.DictWriter(f, fieldnames=['t', 'v'])
                        dict_writer.writeheader()
                        dict_writer.writerows(json_parsed_datapoints)

                    del json_data, json_parsed, json_parsed_datapoints
                else:
                    print ("ERROR saving %s for weather station" % (weather_name[i]))

# Function for obtaining koruza sensor IDs
def get_id(node_id):
    #Create id list
    sensor_id = []
    # Define node url
    url = 'https://kw.koruza.net/api/v1/stream/?tags__node=%s&limit=500&format=json' %(node_id)
    # Open url
    response = urllib.urlopen(url)
    # Load JSON data
    data = json.loads(response.read())
    if data:
        # Loop over desired sensors
        for i in range(0,n_sensor-1,1):
            tmp_ID = [item["id"] for item in data["objects"]
                    if item["tags"]["name"] == ID_name[i]]
            if tmp_ID:
                sensor_id.append(tmp_ID[0])
                print ("ID for %s: %s" % (ID_name[i], tmp_ID[0]))
            else:
                sensor_id.append('')
                print ("ID for %s: ERROR!" % (ID_name[i]))

        # Add variance ID
        tmp_ID = [item["id"] for item in data["objects"]
                if (item["tags"]["name"] ==  ID_name[n_sensor-1] and item["tags"]["unit"] == "%")]
        sensor_id.append(tmp_ID[0])
        print ("ID for %s: %s" % (ID_name[n_sensor-1], tmp_ID[0]))
    else:
        print ("ERROR obtaining sensor IDs!")

    return sensor_id

# Function for obtaining sensor IDs from the weather station
def get_weather_id(node_id):
    # Create id list
    sensor_id = []
    # Define node url
    url = 'https://kw.koruza.net/api/v1/stream/?tags__node=%s&limit=500&format=json' %(node_id)
    # Open url
    response = urllib.urlopen(url)
    # Load JSON data
    data = json.loads(response.read())
    if data:
        # Loop over desired sensors
        for i in range(0,n_weather,1):
            tmp_ID = [item["id"] for item in data["objects"]
                    if ("sensor_id" in item["tags"] and item["tags"]["sensor_id"] == weather_name[i])]
            if tmp_ID:
                sensor_id.append(tmp_ID[0])
                print ("ID for %s: %s" % (weather_name[i], tmp_ID[0]))
            else:
                sensor_id.append('')
                print ("ID for %s: ERROR!" % (weather_name[i]))
    else:
        print ("ERROR obtaining sensor IDs!")

    return sensor_id

# RUN===================================================================================================================
# Loop over Koruza units and get data
for i in range(0,n_unit,1):
       print ("Load koruza nr: %s\n" % unit_name[i])
       Koruza = KoruzaUnit(unit_ID[i], unit_name[i])
       print("\n")
       Koruza.run()
       del Koruza
       print("\n")

# Get data from the weather station
print ("Load weather station\n" )
WStation = WeatherUnit(weather_id)
print("\n")
WStation.run()
