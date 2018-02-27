import requests
from string import Template
import simplejson

def call_cld_func(device_data):

    subject = Template('Plant status update from device $deviceId Plant watering requested.').safe_substitute(device_data)
    body = Template('The plant monitored by the device has been found to have the following soil moisture ''$moisture'' reading and will require watering. Action Water_pump_on requested from the device').safe_substitute(device_data)
    jsonstr =Template('{"to":"tataru.andrei.emanuel@gmail.com","from":"andrei.tataru.metrosystems@gmail.com","subject":"$subject","body":"$body"}').safe_substitute({"subject":subject,"body":body})



    url     = 'https://us-central1-animated-bonsai-195009.cloudfunctions.net/function-2?sg_key=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'
    #payload = {"to":"tataru.andrei.emanuel@gmail.com","from":"andrei.tataru.metrosystems@gmail.com","subject":"Hello from Sendgrid!","body":"Hello World!"}
    
    print jsonstr
    json = simplejson.loads(jsonstr)
    headers = {"Content-Type":"application/json"}
    #res = requests.post(url, data=payload, headers=headers)
    res = requests.post(url, json=json, headers=headers)
    print res
    #print res.status_code

if __name__ == "__main__":
    call_cld_func({'deviceId':'rb1','moisture':'13'})
