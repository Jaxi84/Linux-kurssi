#!/bin/bash

# luodaan streamlit-data-analysis.service
sudo tee /etc/systemd/system/streamlit-data-analysis.service > /dev/null <<EOL
[Unit]
Description=Streamlit Data Analysis App
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/lemp-app
Environment="PATH=/home/ubuntu/venv/bin"
ExecStart=/home/ubuntu/venv/bin/streamlit run /home/ubuntu/lemp-app/lemp_app.py \
  --server.port 8501 \
  --server.address 127.0.0.1 \
  --server.headless true \
  --server.baseUrlPath data-analysis \
  --browser.gatherUsageStats false
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# luodaan streamlit-weather.service
sudo tee /etc/systemd/system/streamlit-weather.service > /dev/null <<EOL
[Unit]
Description=Streamlit Weather App
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/myapiapp
Environment="PATH=/home/ubuntu/myapiapp/venv/bin"
ExecStart=/home/ubuntu/myapiapp/venv/bin/streamlit run /home/ubuntu/myapiapp/weather_app.py \
  --server.port 8502 \
  --server.address 127.0.0.1 \
  --server.headless true \
  --server.baseUrlPath weather \
  --browser.gatherUsageStats false
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# systemd pävitys ja palveluiden käynnistys
sudo systemctl daemon-reload
sudo systemctl enable streamlit-data-analysis.service
sudo systemctl enable streamlit-weather.service
sudo systemctl start streamlit-data-analysis.service
sudo systemctl start streamlit-weather.service

# status check
systemctl status streamlit-data-analysis.service --no-pager
systemctl status streamlit-weather.service --no-pager
