#!/bin/bash

set -e
[ -z $1 ] && echo "No configuration file specified!" && exit 1

TARGET="./deployment"
TARGET_MOSQUITTO=$TARGET/mosquitto
TARGET_NODERED=$TARGET/nodered
TARGET_GRAFANA=$TARGET/grafana
TARGET_TELEGRAF=$TARGET/telegraf
mkdir -p $TARGET $TARGET_NODERED $TARGET_MOSQUITTO $TARGET_GRAFANA $TARGET_TELEGRAF

cp mosquitto/mosquitto.conf $TARGET_MOSQUITTO
cp nodered/Dockerfile $TARGET_NODERED

echo "Generating docker-compose.yml"
mustache $1 docker-compose.yml.mustache > $TARGET/docker-compose.yml

# generate passwords for mosquitto
echo "Generating mosquitto password file"

#generate the password file (unencrypted)
mustache $1 ./mosquitto/mosquitto.passwd.mustache > mosquitto.passwd

# run mosquitto_passwd within container and generate encrypted password file
docker run --name eclipse-mosquitto-hydro --rm -i -v $(pwd):/config -t eclipse-mosquitto mosquitto_passwd -U /config/mosquitto.passwd 
mv mosquitto.passwd $TARGET_MOSQUITTO

# generate password for nodered
echo "Generating nodered credential config"

# generate a shell script that is executed within the nodered container
mustache $1 ./nodered/passwd.sh.mustache > nodered_passwd.sh

# this generates the file nodered.config.json
docker run --name nodered-hydro --rm -i -v $(pwd):/config --entrypoint /bin/bash -t nodered/node-red  /config/nodered_passwd.sh

# generate settings.js from generated password file
mustache nodered.config.json ./nodered/settings.js.mustache > $TARGET_NODERED/settings.js


# generate grafana settings
echo "Generating grafana datasource configuration"
mustache $1 grafana/influx.yaml.mustache > $TARGET_GRAFANA/influx.yaml

echo "Generating telegraf config"
mustache $1 telegraf/telegraf.conf.mustache > $TARGET_TELEGRAF/telegraf.conf

echo "Cleaning up ..."
rm nodered_passwd.sh
rm nodered.config.json
