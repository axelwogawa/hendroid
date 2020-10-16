# Hendroid Raspi Client
## System Setup
- `python 3.5`
-

## Systemd Service
- (re-) start service: `sudo systemctl restart hendroid-clientd.service`
- (re-)enable service: `sudo systemctl enable hendroid-clientd.service`
- service config file: `/etc/systemd/system/hendroid-clientd.service`:
```
  [Unit]
  Description=Hendroid RasPi client service
  After=multi-user.target network.target

  [Service]
  Type=idle
  ExecStart=/usr/bin/python3.5 /home/pi/hendroid/client-raspi/init.py >> /home/pi/hendroid.log 2>&1

  [Install]
  WantedBy=multi-user.target
  Restart=always
```

## App
- path: `~/hendroid/`
- manually start app: `python3 client-raspi/init.py`
- update: `git pull && pip3 install -r client-raspi/requirements.txt`
- logs: `client-raspi/hendroid.log`
