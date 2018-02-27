# Copyright 2017 Google Inc. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""Sample device that consumes configuration from Google Cloud IoT.
This example represents a simple device with a temperature sensor and a fan
(simulated with software). When the device's fan is turned on, its temperature
decreases by one degree per second, and when the device's fan is turned off,
its temperature increases by one degree per second.

Every second, the device publishes its temperature reading to Google Cloud IoT
Core. The server meanwhile receives these temperature readings, and decides
whether to re-configure the device to turn its fan on or off. The server will
instruct the device to turn the fan on when the device's temperature exceeds 10
degrees, and to turn it off when the device's temperature is less than 0
degrees. In a real system, one could use the cloud to compute the optimal
thresholds for turning on and off the fan, but for illustrative purposes we use
a simple threshold model.

To connect the device you must have downloaded Google's CA root certificates,
and a copy of your private key file. See cloud.google.com/iot for instructions
on how to do this. Run this script with the corresponding algorithm flag.

  $ python cloudiot_pubsub_example_mqtt_device.py \
      --project_id=my-project-id \
      --registry_id=example-my-registry-id \
      --device_id=my-device-id \
      --private_key_file=rsa_private.pem \
      --algorithm=RS256

With a single server, you can run multiple instances of the device with
different device ids, and the server will distinguish them. Try creating a few
devices and running them all at the same time.
"""

import argparse
import datetime
import json
import os
import time

import jwt
import paho.mqtt.client as mqtt

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO

def create_jwt(project_id, private_key_file, algorithm):
    """Create a JWT (https://jwt.io) to establish an MQTT connection."""
    token = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'aud': project_id
    }
    with open(private_key_file, 'r') as f:
        private_key = f.read()
    print('Creating JWT using {} from private key file {}'.format(
        algorithm, private_key_file))
    return jwt.encode(token, private_key, algorithm=algorithm)


def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


class Device(object):
    """Represents the state of a single device."""

    def __init__(self):

        # Software SPI configuration:
        #CLK  = 18
        #MISO = 23
        #MOSI = 24
        #CS   = 25
        #mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

        # Hardware SPI configuration:
        self.SPI_PORT   = 0
        self.SPI_DEVICE = 0
        self.mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(self.SPI_PORT, self.SPI_DEVICE))
        self.WaterPumpGPIOpin = 21
        GPIO.setup(self.WaterPumpGPIOpin, GPIO.OUT)
        GPIO.output(self.WaterPumpGPIOpin,0)

        lcd_rs        = 25  # Note this might need to be changed to 21 for older revision Pi's.
        lcd_en        = 24
        lcd_d4        = 23
        lcd_d5        = 17
        lcd_d6        = 18
        lcd_d7        = 22
        lcd_backlight = 4
        lcd_columns = 16
        lcd_rows    = 2

        self.lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,lcd_columns, lcd_rows, lcd_backlight)

        self.ADC_moisture = 7
        self.ADC_temperature = 1
        self.ADC_humidity = 0
        self.ADC_ligth = 2
        self.Reference_mV = 3.3

        self.temperature = 0
        self.water_on = False
        self.connected = False


        self.temp     = 13    #sensor reading here
        self.humidity = 13    #sensor reading here
        self.ligth    = 13    #sensor reading here
        self.moisture = 13    #sensor reading here

    def update_sensor_data(self):
        """Pretend to read the device's sensor data.
        If the fan is on, assume the temperature decreased one degree,
        otherwise assume that it increased one degree.
        """
        
        read_values_moisture=[]
        read_values_humidity=[]
        read_values_temp=[]
        read_values_ligth=[]

        read_humidity=0
        read_temp=0
        read_ligth=0
        read_moisture=0

        for i in range(1,11):
            read_moisture = self.mcp.read_adc(self.ADC_moisture)
            if read_moisture > 0:
                read_moisture = (((read_moisture * self.Reference_mV) / 1024.0) -0.5) * 100
                read_values_moisture += [read_moisture]
            read_humidity = self.mcp.read_adc(self.ADC_humidity)
            if read_humidity > 0:
                read_humidity = (((read_humidity * self.Reference_mV) / 1024.0) -0.5) * 100
                read_values_humidity  += [read_humidity]
            read_temp = self.mcp.read_adc(self.ADC_temperature)
            if read_temp > 0:
                read_temp     = (((read_temp * self.Reference_mV) / 1024.0) -0.5) * 100
                read_values_temp     += [read_temp]
            read_ligth    = self.mcp.read_adc(self.ADC_ligth)
            if read_ligth > 0:
                read_ligth     = (((read_ligth * self.Reference_mV) / 1024.0) -0.5) * 100
                read_values_ligth    += [read_ligth]

            print "Debug - senzor moisture reading on ADC %d is %d" % (self.ADC_moisture,read_moisture)
            print "Debug - senzor humidity reading on ADC %d is %d" % (self.ADC_humidity,read_humidity)
            print "Debug - senzor temperature reading on ADC %d is %d" % (self.ADC_temperature,read_temp)
            print "Debug - senzor ligth reading on ADC %d is %d" % (self.ADC_ligth,read_ligth)


            time.sleep(0.5)

        self.moisture = sum(read_values_moisture) / float(len(read_values_moisture))
        self.humidity = sum(read_values_humidity) / float(len(read_values_humidity))
        self.temp     = sum(read_values_temp) /     float(len(read_values_temp))
        self.ligth    = sum(read_values_ligth)    / float(len(read_values_ligth))


    def wait_for_connection(self, timeout):
        """Wait for the device to become connected."""
        total_time = 0
        while not self.connected and total_time < timeout:
            time.sleep(1)
            total_time += 1

        if not self.connected:
            raise RuntimeError('Could not connect to MQTT bridge.')

    def on_connect(self, unused_client, unused_userdata, unused_flags, rc):
        """Callback for when a device connects."""
        print('Connection Result:', error_str(rc))
        self.connected = True
        self.lcd.clear()
        self.lcd.message('Connected to\nGOOGEL IoT MQTT Bridge')

    def on_disconnect(self, unused_client, unused_userdata, rc):
        """Callback for when a device disconnects."""
        print('Disconnected:', error_str(rc))
        self.connected = False
        self.lcd.clear()
        self.lcd.message('Disconnected from\nGOOGEL IoT MQTT Bridge')

    def on_publish(self, unused_client, unused_userdata, unused_mid):
        """Callback when the device receives a PUBACK from the MQTT bridge."""
        print('Published message acked.')
        self.lcd.clear()
        self.lcd.message('MSG ACK from\nGOOGEL IoT MQTT Bridge')

    def on_subscribe(self, unused_client, unused_userdata, unused_mid,
                     granted_qos):
        """Callback when the device receives a SUBACK from the MQTT bridge."""
        print('Subscribed: ', granted_qos)
        if granted_qos[0] == 128:
            print('Subscription failed.')

    def on_message(self, unused_client, unused_userdata, message):
        """Callback when the device receives a message on a subscription."""
        payload = str(message.payload)
        print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))

        # The device will receive its latest config when it subscribes to the
        # config topic. If there is no configuration for the device, the device
        # will receive a config with an empty payload.
        if not payload:
            return

        # The config is passed in the payload of the message. In this example,
        # the server sends a serialized JSON string.
        data = json.loads(payload)
        if data['water_on'] != self.water_on:
            # If changing the state of the water_pump, print a message and
            # update the internal state.
            self.water_on = data['water_on']
            if self.water_on:
                print('Water turned on.')
                GPIO.output(self.WaterPumpGPIOpin,1)
            else:
                print('Water turned off.')
                GPIO.output(self.WaterPumpGPIOpin,0)


def parse_command_line_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Example Google Cloud IoT MQTT device connection code.')
    parser.add_argument(
        '--project_id',
        default=os.environ.get("GOOGLE_CLOUD_PROJECT"),
        required=True,
        help='GCP cloud project name.')
    parser.add_argument(
        '--registry_id', required=True, help='Cloud IoT registry id')
    parser.add_argument(
        '--device_id',
        required=True,
        help='Cloud IoT device id')
    parser.add_argument(
        '--private_key_file', required=True, help='Path to private key file.')
    parser.add_argument(
        '--algorithm',
        choices=('RS256', 'ES256'),
        required=True,
        help='Which encryption algorithm to use to generate the JWT.')
    parser.add_argument(
        '--cloud_region', default='us-central1', help='GCP cloud region')
    parser.add_argument(
        '--ca_certs',
        default='roots.pem',
        help='CA root certificate. Get from https://pki.google.com/roots.pem')
    parser.add_argument(
        '--num_messages',
        type=int,
        default=100,
        help='Number of messages to publish.')
    parser.add_argument(
        '--mqtt_bridge_hostname',
        default='mqtt.googleapis.com',
        help='MQTT bridge hostname.')
    parser.add_argument(
        '--mqtt_bridge_port', default=8883, help='MQTT bridge port.')
    parser.add_argument(
        '--message_type', choices=('event', 'state'),
        default='event',
        help=('Indicates whether the message to be published is a '
              'telemetry event or a device state message.'))

    return parser.parse_args()


def main():
    args = parse_command_line_args()

    # Create the MQTT client and connect to Cloud IoT.
    client = mqtt.Client(
        client_id='projects/{}/locations/{}/registries/{}/devices/{}'.format(
            args.project_id,
            args.cloud_region,
            args.registry_id,
            args.device_id))
    client.username_pw_set(
        username='unused',
        password=create_jwt(
            args.project_id,
            args.private_key_file,
            args.algorithm))
    client.tls_set(ca_certs=args.ca_certs)

    device = Device()

    client.on_connect = device.on_connect
    client.on_publish = device.on_publish
    client.on_disconnect = device.on_disconnect
    client.on_subscribe = device.on_subscribe
    client.on_message = device.on_message

    client.connect(args.mqtt_bridge_hostname, args.mqtt_bridge_port)

    client.loop_start()

    # This is the topic that the device will publish telemetry events
    # (temperature data) to.
    mqtt_telemetry_topic = '/devices/{}/events'.format(args.device_id)

    # This is the topic that the device will receive configuration updates on.
    mqtt_config_topic = '/devices/{}/config'.format(args.device_id)

    # Wait up to 5 seconds for the device to connect.
    device.wait_for_connection(5)

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)

    # Update and publish temperature readings at a rate of one per second.
    for _ in range(args.num_messages):
        # In an actual device, this would read the device's sensors. Here,
        # you update the temperature based on whether the fan is on.
        device.update_sensor_data()

        # Report the device's temperature to the server by serializing it
        # as a JSON string.
        payload = json.dumps({'deviceId':'rb1','timestamp': datetime.datetime.now().isoformat(), 'temp': device.temp, 'humidity':device.humidity, 'ligth':device.ligth, 'moisture':device.moisture, 'water_on': device.water_on})
        print('Publishing payload', payload)
        client.publish(mqtt_telemetry_topic, payload, qos=1)
        
        device.lcd.clear()
        device.lcd.message('T='+str(int(device.temp))+' H='+str(int(device.humidity)))
        # Send events every second.
        time.sleep(1)

    client.disconnect()
    client.loop_stop()
    print('Finished loop successfully. Goodbye!')
    device.lcd.clear()
    device.lcd.message('Comunication END\nGoing to SLEEP')
    device.lcd.set_backlight(1)


if __name__ == '__main__':
    main()
