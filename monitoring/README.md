# Setup control and monitoring stack with docker-compose

This is the description to run a control and monitoring stack with docker. Inspired by https://github.com/ttncat/ttncat-docker-compose.

Following components are used:

- Mosquitto MQTT broker for sending/receiving messages
- Nodered for easy generation of data flows between the components
- Grafana for visualization of time series data
- InfluxDB for easy storage of time series data 

## Configure settings

## Run docker

`docker-compose up`


### Configure mosquitto

I'm using a pretty easy configuration for mosquitto. Currently only user/password authentication is
used. So you have to provide the right passwd file for mosquitto that contain the users with the corresponding password hashes.

#### Generate password 

Install mosquitto locally:

`apt-get install mosquitto`

Write specified user and password to password file:

`mosquitto_passwd -c <password file> <username>`

Example:

`mosquitto_passwd -c mosquitto/mosquitto.passwd client01`


### Configure Influx

#### Authentication

Set reading and writing user credentials within the docker-compose.yml.
For a general reading access the INFLUXDB_READ_USER settings have to be adapted.
The same has to be done for a writing user with INFLUXDB_WRITE_USER.

#### Database creation

The database is currently created with the env parameter INFLUXDB_DB. 
This just seems to work with 1.7 currently. I tried with 1.8 but that wasn't successful so far (also the init scripts didn't work).


### Configure Grafana

#### Authentication

On first login, the default credentials are admin/admin. So just log in and you will be requested to change the password.

#### Database connection

Add a new influxdb datasource. Set the hostname to the container name and the according path. 
Example: http://hydropynics_influxdb:8086

Set basic auth to active and use the credentials for the reading user previously set for the influx container within the docker.compose.yml.


### Configure nodered

#### Authentication

Tutorial from https://nodered.org/docs/user-guide/runtime/securing-node-red#http-node-security

Create a bcrypt hashed password and adapt the settings.js accordingly.

To generate a hashed password, go to the nodered container with 

`docker exec -it container_id /bin/bash` 

and execute 

`node -e "console.log(require('bcryptjs').hashSync(process.argv[1], 8));" your-password-here`. 

#### MQTT to Influx flow

See nodered folder in / and the sample_influx.json