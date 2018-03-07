from http_iot_client import HTTP_iot_client
from adc_read import ADC_reader
import datetime
import time


class IotDevice(object):

    def __init__(self):
        self.sesors = ADC_reader()
        self.iot_client = HTTP_iot_client()


if __name__ == '__main__':
    device = IotDevice()
    print(device.iot_client.BASE_URL)
    device.iot_client.jwt_token = device.iot_client.create_jwt(device.iot_client.private_key_file,device.iot_client.algorithm)
    device.iot_client.jwt_iat = datetime.datetime.utcnow()
    device.iot_client.jwt_expires_minutes = None

    # Update device configuration
    print('Latest configuration: {}'.format(device.iot_client.get_config(
        '0', device.iot_client.message_type, device.iot_client.BASE_URL, device.iot_client.project_id,
        device.iot_client.cloud_region, device.iot_client.registry_id, device.iot_client.device_id, device.iot_client.jwt_token).text))

    for i in range(1, device.iot_client.num_messages+1):
        print(device.iot_client.jwt_token)
        seconds_since_issue = (datetime.datetime.utcnow() - device.iot_client.jwt_iat).seconds
        if seconds_since_issue > 60 * device.iot_client.jwt_expires_minutes:
            print('Refreshing token after {}s').format(seconds_since_issue)
            device.iot_client.jwt_token = device.iot_client.create_jwt(device.iot_client.private_key_file,device.iot_client.algorithm)
            device.iot_client.jwt_iat = datetime.datetime.utcnow()

        payload = '{}/{}-payload-{}'.format(device.iot_client.registry_id, device.iot_client.device_id, i)

        print('Publishing message {}/{}: \'{}\''.format(i, device.iot_client.num_messages, payload))

        resp = device.iot_client.publish_message(
                payload, device.iot_client.message_type, device.iot_client.BASE_URL, device.iot_client.project_id,
                device.iot_client.cloud_region, device.iot_client.registry_id, device.iot_client.device_id, device.iot_client.jwt_token)

        print('HTTP response: ', resp)

        # Send events every second. State should not be updated as often
        time.sleep(1 if device.iot_client.message_type == 'event' else 5)
    print('Finished.')
