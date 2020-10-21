# docker-cellar-panel

cellar panel w/ auth and timeseries data recording

![desktop panel](https://github.com/mattotodd/docker-cellar-panel/blob/main/docs/img/desktop_screenshot.png?raw=true)

## Overview

multi-container services running via [docker-compose](https://docs.docker.com/compose/) on a raspberrypi

* authentication
* remote monitor/control
* data-recording
* master-alarm

### Auth Service

**container name:** `auth`
**container port(s):** `80,443`

The auth service sits in front of any internal apps we are using so that we dont expose applications and services to the outside world. Using [Pomerium](https://www.pomerium.com/) we can proxy any internal applications and make use of the fact that we already use G-Suite for user authentication (pomerium supports many [identity providers](https://www.pomerium.io/docs/identity-providers/)).


It works by chosing a domain/sub-domain for your internal services, for example `corp.brewco.com` and forwarding all DNS traffic for `*.corp.brewco.com` to the host server where these containers are running. Many services can be behind a single proxy, but for the purposes of this program, we really only care about the `cellar-webapp`

If ports `80` and `443` are forwared correctly to the box running these containers, SSL certs will be automatically generated the first time you run the containers. Thanks [LetsEncrypt](https://letsencrypt.org/)!!

We can then point `cellar.corp.brewco.com` at the `cellar-webapp`. First time uses will be redirect to `auth.corp.brewco.com` where they will first be asked to log into the identity provider (G-Suite in our case), and if they successfully login, their traffic will then be proxied to the other services described below.


### Cellar Service

**container name:** `cellar-service`
**container port:** `5000`

The cellar service is a [Flask](https://flask.palletsprojects.com/en/1.1.x/quickstart/) application that acts as an intermediary between the actual cellar panel and anything that relies on it. 

Every 60 seconds it:
- Reads temp/setpoint/valve data from the cellar panel and caches that data, so any downstream services read from the cache and do not hit the cellar panel directly.
- Records the data to [InfluxDB](https://www.influxdata.com/) (they offer a free tier with 30 days data retention - [cloud2.influxdata.com](https://cloud2.influxdata.com))
- Sends a heartbeat metric to [AWS Cloudwatch](https://aws.amazon.com/cloudwatch/) to monitor if the system goes down

We also sync with a google spreadsheet to get production batch information about the beer in each vessel.

### Web App Service

**container name:** `cellar-webapp`
**container port:** `3000`

The web app is a [next.js](https://nextjs.org/) responsive web application that displays all the cellar info, beer info, and allows for setting vessel setpoints (by dragging the temp dial to the desired setpoint). It talks to the `cellar-service` to get data or make changes to setpoints.

<img src="https://github.com/mattotodd/docker-cellar-panel/blob/main/docs/img/mobile_screenshot.jpeg?raw=true" width="200"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><img src="https://github.com/mattotodd/docker-cellar-panel/blob/main/docs/img/mobile_screenshot_2.JPG?raw=true" width="200">

## Data Rentention

Timesseries data can be retreieved using the InfluxDB cloud explorer.

![Influx DB Explorer](https://github.com/mattotodd/docker-cellar-panel/blob/main/docs/img/InfluxDB_Explorer.png?raw=true)


## Alarms

The `cellar-servcie` current records a heartbeat to AWS Cloudwatch. We can then set alarms based off conditions in the brewery. For now, we trigger an alarm if we dont have any readings for more than 5 minutes; this is our master alarm. We have issues with the power going out, so its nice to be notified.

The the alarm conditions are pushed to [Squadcast](https://www.squadcast.com/) we can manage on-call responses and escalate the issue through our brewery team (they offer a free tier for less than 10 employees which works for us).

In a future rev, the plan is to trigger an alarm when any tank if moving up when it should be going down, but it was out of scope for this initial release.


## Setup 

1. [Setup a new rasberrypi SD card](https://www.raspberrypi.org/documentation/installation/installing-images/) using the [32bit lite image](https://www.raspberrypi.org/downloads/raspberry-pi-os/)

2. Log into your new pi and run the following commands to get the pi setup with the correct dependencies to run docker-compose.

```
sudo apt update
sudo apt install -y \
     apt-transport-https \
     ca-certificates \
     curl \
     gnupg2 \
     software-properties-common
curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg | sudo apt-key add -
echo "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
     $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update
sudo apt install -y --no-install-recommends docker-ce cgroupfs-mount
sudo systemctl enable docker
sudo systemctl start docker
sudo apt update
sudo apt install -y python3-pip libffi-dev
sudo pip3 install docker-compose
sudo gpasswd -a $USER docker
newgrp docker
sudo apt install git
```

3. Clone this repo onto the pi

```
git clone https://github.com/mattotodd/docker-cellar-panel.git
```

4. Change into the repository directory and setup your ENVIRONMENT VARIABLES

You will need to create a file called `.env` with the following variable set (see: env_example):

```
cd docker-cellar-panel
nano .env
```

Then set the follow vars described below:

```
CELLAR_NAME =  name of cellar - used for cloudwatch metric
CELLAR_PANEL_IP = IP address of the Alpha cellar panel on your local network
# pomerium
AUTHENTICATE_SERVICE_URL= domain where pomerium auth will take place
AUTOCERT=true # use lets encrypt to get SSL certs
# Generate 256 bit random keys  e.g. `head -c32 /dev/urandom | base64`
COOKIE_SECRET= # generate a secret
IDP_PROVIDER=google
IDP_CLIENT_ID= see: https://www.pomerium.io/docs/identity-providers/google.html
IDP_CLIENT_SECRET= see: https://www.pomerium.io/docs/identity-providers/google.html
POMERIUM_POLICY= base64 encoded policies see: https://www.pomerium.io/reference/#policy
INFLUX_CLIENT_URL=https://us-west-2-1.aws.cloud2.influxdata.com
INFLUX_DB_TOKEN = # created from influxdb cloud
INFLUX_ORG= # created from influxdb cloud
INFLUX_BUCKET= # created from influxdb cloud
AWS_REGION=us-east-1
AWS_ACCESS_KEY= # aws access credentials with PutMetricData write access to cloudwatch
AWS_SECRET_KEY= # aws access credentials with PutMetricData write access to cloudwatch
PRODUCTION_SPREADSHEET_ID= # google spreadsheet id
MAIN_SHEET_NAME= # sheet name
GOOGLE_SERVICE_AUTH=based64 encoded service auth creds
```

5. Build and run the services:
```
docker-compose up -d
```
This will run the services in the background, so you wont see much.  But in just a few moments, you should be able to navigate to `cellar.corp.brewco.com` and check on your cellar.

docker should automatically restart the services if you reboot the pi.


