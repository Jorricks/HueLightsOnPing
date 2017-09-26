# Hue lights on ping
Simple state program that has the option to stay on, turn on/of based on
ping results or stay off.

## Installation

- Get the code from the github (get it with `git clone https://github.com/JorricksTU/HueLightsOnPing.git`) for latest version.
- Install flask and phue(
`
pip3 install flask phue
`)

## Usage
Change the config at the top of the file huelightsonping.py and run using
`python3 huelightsonping.py`

## How to create a service
One can create a linux service by creating a file called hueonping.service in /etc/systemd/system with the following contents
Do not forget to change username into your username.
(Note: You might have to change the python path too.)
``` linux
[Unit]
Description=Hue lights on ping daemon
[Service]
WorkingDirectory=/home/username/HueLightsOnPing/
Type=simple
User=username
UMask=007
ExecStart=/usr/bin/python3.5 /home/username/HueLightsOnPing/huelightsonping.py
Restart=on-failure
TimeoutStopSec=300
[Install]
WantedBy=multi-user.target
```

After you created the file in the right directory, run the following commands.
```linux
sudo systemctl enable /etc/systemd/system/hueonping.service
sudo service hueonping start
sudo service hueonping stop
```
## Dependencies
- [Flask](http://flask.pocoo.org/)
- [phue](https://github.com/studioimaginaire/phue)