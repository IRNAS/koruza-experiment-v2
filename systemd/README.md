# Systemd service

To enable the KORUZA experiment systemd service, run:
```
cd /etc/systemd/system
sudo ln -s /home/pi/koruza-experiment-mb/systemd/koruza-experiment.service
sudo systemctl daemon-reload
sudo systemctl start koruza-experiment
```
