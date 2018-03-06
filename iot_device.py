from http_iot_client import HTTP_iot_client
from adc_read import ADC_reader


class IOT_device(object):
    
    
    
    
    
    def __init__(self):
        self.sesors = ADC_reader()
        self.iot_client = HTTP_iot_client()


if __name__ == '__main__':
    device = IOT_device()
    print(device.iot_client.BASE_URL)
    device.iot_client.jwt_token(None)
    device.iot_client.jwt_iat(None)

    for i in range(1, device.iot_client.num_messages+1):
        print(device.iot_client.jwt_token)

