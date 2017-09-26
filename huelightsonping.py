import pprint
import time
import os
import subprocess
import phue
import sys
from platform import system as system_name
from phue import Bridge
from webcomponent import WebConfig

"""
# State 0 - Lights permanently off.
# State 1 - Lights permanently on.
# State 2 - Lights should be activated by ping. State is only active during the waiting of a ping response.
# State 3 - Lights are turned on by ping.
# State 4 - Lights are turned off by ping.

This is where you should set the settings to your liking.
"""
conf_begin_state = 2  # Start with the state based on ping
conf_ip_to_check = '192.168.1.1'  # Which IP should be checked by the ping.
conf_bridge_ip = '192.168.1.1'  # Hue bridge IP.
conf_interval_seconds = 3  # How many seconds should be in between pings.
conf_listen_host = '192.168.1.1'  # What ip should be listened too. 0.0.0.0 for open, localhost for local.
conf_listen_port = '1234'  # what port should be listened too.
conf_enable_api = True  # Do you want to enable the web components.


class HueLightsStateMachine:
    def __init__(self, begin_state, ip_to_check, bridge_ip, interval_seconds, listen_host, listen_port, enable_api):
        self.state = begin_state
        self.ip_to_check = ip_to_check
        self.interval_seconds = interval_seconds
        self.listen_address = listen_host
        self.listen_port = listen_port

        try:
            self.bridge = Bridge(bridge_ip)
            self.bridge.connect()
            pprint.pprint(self.bridge.get_api())
            print('Connection to bridge successful')
        except phue.PhueRegistrationException:
            print('You did not press the bridge button in the last 30 seconds. Please retry.')
            sys.exit(0)

        if enable_api:
            self.web = WebConfig(self.listen_address, self.listen_port,
                                 self.enter_state0, self.enter_state1, self.enter_state2)
            self.web.start_web_servers()

    def run(self):
        state_routines = {0: self.enter_state0,
                          1: self.enter_state1,
                          2: self.enter_state2,
                          3: self.enter_state3,
                          4: self.enter_state4}
        state_routines[self.state]()
        while True:
            print('Current state: ', self.state)
            if self.state >= 2:
                self.act_on_ping()
            if self.state == 0:  # This is to make sure when power goes down and up you remember you turned it off.
                self.turn_off_lights()
            time.sleep(self.interval_seconds)

    def enter_state0(self):  # Turning the lights OFF permanently
        if self.state == 1 or self.state >= 2:  # Only if it is currently permanently on or based on ping.
            # Turn off lights.
            self.state = 0

    def enter_state1(self):  # Turning the lights ON permanently
        if self.state == 0 or self.state >= 2:  # Only if it is currently permanently off or based on ping.
            # Turn ON lights.
            self.state = 1

    def enter_state2(self):  # Turning the lights on or off based on ping.
        if self.state == 0 or self.state == 1:  # Only if it is currently set to anything permanently.
            # Check now based on ping.
            self.state = 2
            self.act_on_ping()

    def enter_state3(self):  # Turning the lights on based on a ping response.
        if self.state == 2 or self.state == 4:
            # turn on lights
            self.turn_on_lights()
            self.state = 3

    def enter_state4(self):  # Turning the lights off based on a non responding ping
        if self.state == 2 or self.state == 3:
            # turn off lights
            self.turn_off_lights()
            self.state = 4

    def act_on_ping(self):
        if self.execute_ping():
            self.enter_state3()
        else:
            self.enter_state4()

    def execute_ping(self):
        with open(os.devnull, 'w') as DEVNULL:
            try:
                param1 = "-n 1" if system_name().lower() == "windows" else "-c 1"
                subprocess.check_call(
                    ['ping', param1, '1', self.ip_to_check],
                    stdout=DEVNULL,  # suppress output
                    stderr=DEVNULL
                )
                return True
            except subprocess.CalledProcessError:
                return False
        #
        # # Ping parameters as function of OS
        # parameters = "-n 1" if system_name().lower() == "windows" else "-c 1"
        # # Pinging
        # return system_call("ping " + parameters + " " + self.ip_to_check) == 0

    def turn_on_lights(self):
        # Turn on the lights.
        lights = self.bridge.lights
        for l in lights:
            l.on = True
            l.brightness = 254

    def turn_off_lights(self):
        # Turn off all the lights.
        lights = self.bridge.lights
        for l in lights:
            l.on = False


hlm = HueLightsStateMachine(
    conf_begin_state,
    conf_ip_to_check,
    conf_bridge_ip,
    conf_interval_seconds,
    conf_listen_host,
    conf_listen_port,
    conf_enable_api
)

hlm.run()
