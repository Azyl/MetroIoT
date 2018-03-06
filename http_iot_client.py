import base64
import datetime
import json
import time
from google.api_core import retry
import jwt
import requests


class HTTP_iot_client(object):
   
    @property
    def BASE_URL(self):
        return self._BASE_URL

    @BASE_URL.setter
    def BASE_URL(self,value=None):
        if value is None:
            self._BASE_URL = 'https://cloudiotdevice.googleapis.com/v1'
        else:
            self._BASE_URL = value

    @BASE_URL.getter
    def BASE_URL(self):
        return self._BASE_URL

    @property
    def BACKOFF_DURATION(self):
        return self._BACKOFF_DURATION

    @BACKOFF_DURATION.setter
    def BACKOFF_DURATION(self,value=None):
        if value is None:
            self._BACKOFF_DURATION = 60
        else:
            self._BACKOFF_DURATION = value

    @BACKOFF_DURATION.getter
    def BACKOFF_DURATION(self):
        return self._BACKOFF_DURATION

    @property
    def project_id(self):
        return self._project_id

    @project_id.setter
    def project_id(self,value=None):
        if value is None:
            self._project_id = 'animated-bonsai-195009'
        else:
            self._project_id = value

    @project_id.getter   
    def project_id(self):
        return self._project_id

    @property
    def registry_id(self):
        return self._registry_id

    @registry_id.setter
    def registry_id(self,value=None):
        if value is None:
            self._registry_id = 'metro-iot-reg1'
        else:
            self._registry_id = value

    @project_id.getter
    def registry_id(self):
        return self._project_id

    @property
    def device_id(self):
         return self._device_id

    @device_id.setter
    def device_id(self,value=None):
        if value is None:
            self._device_id = 'raspi_node_1'
        else:
            self._device_id = value

    @device_id.getter
    def device_id(self):
        return self._device_id

    @property
    def algorithm(self):
         return self._algorithm

    @algorithm.setter
    def algorithm(self,value=None):
        if value is None:
            self._algorithm = 'RS256'
        else:
            self._algorithm = value

    @algorithm.getter
    def algorithm(self):
        return self._algorithm

    @property
    def cloud_region(self):
         return self._cloud_region

    @cloud_region.setter
    def cloud_region(self,value=None):
        if value is None:
            self._cloud_region = 'europe-west1'
        else:
            self._cloud_region = value

    @cloud_region.getter
    def cloud_region(self):
        return self._cloud_region

    @property
    def ca_certs(self):
         return self._ca_certs

    @ca_certs.setter
    def ca_certs(self,value=None):
        if value is None:
            self._ca_certs = 'roots.pem'
        else:
            self._ca_certs = value

    @ca_certs.getter
    def ca_certs(self):
        return self._ca_certs

    @property
    def num_messages(self):
         return self._num_messages

    @num_messages.setter
    def num_messages(self,value=None):
         if value is None:
            self._num_messages = 100
         else:
             self._num_messages = value

    @num_messages.getter
    def num_messages(self):
        return self._num_messages

    @property
    def message_type(self):
         return self._message_type

    @message_type.setter
    def message_type(self,value=None):
         if value is None:
             self._message_type = 'event'
         else:
             self._message_type = value

    @message_type.getter
    def message_type(self):
        return self._message_type



    @property
    def private_key_file(self):
         return self._private_key_file

    @private_key_file.setter
    def private_key_file(self,value=None):
         if value is None:
             self._private_key_file = 'rsa_private.pem'
         else:
             self._private_key_file = value

    @private_key_file.getter
    def private_key_file(self):
         return self._private_key_file

    @property
    def jwt_token(self):
         return self._jwt_token

    @jwt_token.setter
    def jwt_token(self,value=None):
         if value is None:
             self._jwt_token = self.create_jwt(self.project_id, self.private_key_file, self.algorithm)
         else:
             self._jwt_token = value

    @jwt_token.getter
    def jwt_token(self):
        return self._jwt_token


    @property
    def jwt_iat(self):
        return self._jwt_iat

    @jwt_iat.setter
    def jwt_iat(self,value=None):
        if value is None:
            self._jwt_iat = datetime.datetime.utcnow()
        else:
            self._jwt_token = value

    @jwt_iat.getter
    def jwt_iat(self):
       return self._jwt_iat


    @property
    def jwt_expires_minutes(self):
       return self._jwt_expires_minutes

    @jwt_expires_minutes.setter
    def jwt_expires_minutes(self,value=None):
       if value is None:
           self._jwt_expires_minutes = 20
       else:
           self._jwt_expires_minutes = value

    @jwt_expires_minutes.getter
    def jwt_expires_minutes(self):
       return self._jwt_expires_minutes

    def __init__(self, BASE_URL=None, BACKOFF_DURATION=None, project_id=None, registry_id=None, device_id=None, algorithm=None, cloud_region=None, ca_certs=None, num_messages=None, message_type=None, private_key_file=None, jwt_token=None, jwt_iat=None, jwt_expires_minutes=None):
        self._BASE_URL = BASE_URL
        self._BACKOFF_DURATION = BACKOFF_DURATION
        self._project_id = project_id
        self._registry_id = registry_id
        self._device_id = device_id
        self._algorithm = algorithm
        self._cloud_region = cloud_region
        self._ca_certs = ca_certs
        self._num_messages = num_messages
        self._message_type = message_type
        self._private_key_file = private_key_file
        self._jwt_token = jwt_token
        self._jwt_iat = jwt_iat
        self._jwt_expires_minutes = jwt_expires_minutes


    def create_jwt(project_id, private_key_file, algorithm):
        token = {
                # The time the token was issued.
                'iat': datetime.datetime.utcnow(),
                # Token expiration time.
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                # The audience field should always be set to the GCP project id.
                'aud': project_id
        }

        # Read the private key file.
        with open(private_key_file, 'r') as f:
            private_key = f.read()

        print('Creating JWT using {} from private key file {}'.format(
                algorithm, private_key_file))

        return jwt.encode(token, private_key, algorithm=algorithm).decode('ascii')


    @retry.Retry(
    predicate=retry.if_exception_type(AssertionError),
    deadline=BACKOFF_DURATION)
    def publish_message(
            message, message_type, base_url, project_id, cloud_region, registry_id,
            device_id, jwt_token):
        headers = {
                'authorization': 'Bearer {}'.format(jwt_token),
                'content-type': 'application/json',
                'cache-control': 'no-cache'
        }

        # Publish to the events or state topic based on the flag.
        url_suffix = 'publishEvent' if message_type == 'event' else 'setState'

        publish_url = (
            '{}/projects/{}/locations/{}/registries/{}/devices/{}:{}').format(
                base_url, project_id, cloud_region, registry_id, device_id,
                url_suffix)

        body = None
        msg_bytes = base64.urlsafe_b64encode(message.encode('utf-8'))
        if message_type == 'event':
            body = {'binary_data': msg_bytes.decode('ascii')}
        else:
            body = {
            'state': {'binary_data': msg_bytes.decode('ascii')}
            }

        resp = requests.post(
                publish_url, data=json.dumps(body), headers=headers)

        if (resp.status_code != 200):
            print('Response came back {}, retrying'.format(resp.status_code))
            raise AssertionError('Not OK response: {}'.format(resp.status_code))

        return resp




    @retry.Retry(
    predicate=retry.if_exception_type(AssertionError),
    deadline=BACKOFF_DURATION)
    # [START iot_http_getconfig]
    def get_config(
            version, message_type, base_url, project_id, cloud_region, registry_id,
            device_id, jwt_token):
        headers = {
                'authorization': 'Bearer {}'.format(jwt_token),
                'content-type': 'application/json',
                'cache-control': 'no-cache'
        }

        basepath = '{}/projects/{}/locations/{}/registries/{}/devices/{}/'
        template = basepath + 'config?local_version={}'
        config_url = template.format(
            base_url, project_id, cloud_region, registry_id, device_id, version)

        resp = requests.get(config_url, headers=headers)

        if (resp.status_code != 200):
            print('Error getting config: {}, retrying'.format(resp.status_code))
            raise AssertionError('Not OK response: {}'.format(resp.status_code))

        return resp
        # [END iot_http_getconfig]      




