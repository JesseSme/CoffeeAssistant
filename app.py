import pyaudio
import wave
import audioop
import time
import requests

ifttt_url = "https://maker.ifttt.com/trigger/yelling/with/key/dX1X_bNGRmua0rRZmMY2Ji"
ifttt_json = {
    "value1": "",
    "value2": "",
    "value3": ""
}


url = "http://172.27.241.67:8123/api/services/switch/turn_" #Raspberry IP in emblab
json_object = {
    "entity_id": "switch.tradfri_outlet" #Specify the affected "smart device"
    }
headers = {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIxMTg3MmIzMGQ3MjU0NjRhOWE4Zjc3ZGQzYzViY2FjMiIsImlhdCI6MTYwNjIwNjIyMywiZXhwIjoxOTIxNTY2MjIzfQ.8BNnjgh9lI1ZymHCHoMlWtQ7MdHC5goR2x8JbiEkySg",
        "content-type": "application/json"
}

#Initialize audio input parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

# RECORD_SECONDS = 5
#WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

threshold_time = 0
light_status = "on"
prev_state = "off"
coffee_timer = 1800


def create_input():

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    return stream


def volume_check(stream):

    data = stream.read(CHUNK)
    rms = audioop.rms(data, 2)

    return rms

#Call the homeassistant backend with the specified state. (entity is hardcoded in to the payload)
#Manages the on and off-states of the given device.
def call_hass(state):
    global prev_state
    global threshold_time
    time_now = time.time()
    if (int(time_now - threshold_time)) > 0.1 and prev_state != state:
        if state == "on":
            prev_state = state
            response = requests.post(url+state, headers=headers, json={"entity_id": "switch.tradfri_outlet"})
            print(response)
        else:
            prev_state = state
            response = requests.post(url+state, headers=headers, json={"entity_id": "switch.tradfri_outlet"})
            print(response)
        threshold_time = time.time()

    pass

#Phone alert when coffee machine is turned on.
def send_ifttt_notification():

    ifttt_json["value1"] = time.strftime("%H:%M:%S", time.localtime())

    response = requests.post(ifttt_url, json=ifttt_json)
    print(response)
    pass


def main():
    stream = create_input()
    global prev_state

    #Check if the volume threshold has been crossed, keep the device {counter} seconds on and then turn off.
    #For test we've only set to counter to 5 seconds.
    while True:
        if volume_check(stream) > 5000:
            call_hass("on")

            #Send a phone alert every time the coffee machine is turned on
            send_ifttt_notification()

            counter = 5
            while counter > 0:
                counter = counter - 1
                print(counter)
                time.sleep(1)
        else:
            call_hass("off")
        time.sleep(0.1)



main()
