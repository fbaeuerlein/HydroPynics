# HydroPynics

## Description
In 2019 i started to do some experiments with hydroponics. So i decided to do some automation to control necessary pumps and have a better overview of the environmental conditions. Finally i came up with some electrical parts to recycle to a small automation solution with a Raspberry Pi. 

To do all the communication with sensors and acquiring the data, i implemented a small python script that is reading gpios and I2C to gather all the data and finally publishes via MQTT. Currently i use Nodred for remote control and grafana for visualization of the time series data.

In addition to that, i wanted to do some monitoring and remote controlling, so i tried to grab my whole docker knowledge to create some small monitoring solution that is also easily deployable into the cloud or some vserver.


## Software

### General requirements

The client software runs with python3 on Raspberry Pi (currently just tested with a model 3B). 
For the monitoring setup you need docker (at the server side).

### Running

#### Install required python packages
```
cd HydroPynics
pip3 install -r requirements.txt
```

#### Add user to gpio and i2c group
```
usermod -aG gpio <USER>
usermod -aG i2c <USER>
```

#### Configuration
Create a configuration file according to config_sample.json: 

```json
{
    "general" :
    {
        "device_id" : "hydro01"          # device id used to annotate MQTT messages
    },
    "mqtt" :                             # MQTT server settings 
    {
        "host" : "localhost",         
        "port" : 1883, 
        "user" : "hydro01", 
        "password" : "password"
    }
}
```

### Monitoring

See the monitoring subfolder for detailed documentation.

## Hardware

### Wiring

**I'm dealing with 230 V AC and i'm not a professional electrician. All images, schemes, etc. were made to my best knowledge, but i'm not responsible for any damage, harms and losses resulting from the use of my work!**

**Working with this voltage can result in serious injuries, death and other damages!**

**I just had this box left, so this is not the way a professional electrical cabinet should look like! Different voltages are mixed within it on the same rail and also the wires are not strictly separated. Think about your and the safety of others!**

**The whole construction is not part of a fixed electrical installation. So you can't be sure which of the 230 V wires is ground and which one is the phase conductor! For that reason i'm switching both wires. Otherwise it can happen that there's still a connection to the pahse conductor. Do NOT switch the protective conductor! It saves lives!**

![Image of the complete controller unit](https://github.com/fbaeuerlein/HydroPynics/blob/master/images/control.jpg)

### Components

#### Electrical parts

- Ground fault circuit interruptor: Merlin Gerin 230V 30mA (This one is very important because we're dealing with water and voltage!)
- Power supply: Meanwell 50 Watt 24V 
- Power regulator: LM2596 DC-DC Converter
- Relays for switching pumps: IDEC 2-channel (important to switch both wires of the 230V!)
- Relays to switch 24V control voltage: 8-Channel relay card (the default one you find everywhere in the internet)
- ADS1115 for reading the NTCs
- HC SR04 Ultrasonic sensor for tank level measuring
- NTCs: Some old ones from central heatings
- Raspberry Pi 3B
- Mounting: DIN Rail
- Other parts: wires, LEDs, screws, glue, pcbs, PVC-pipes, etc.
- Parts that are controlled: fish tank air pump, fish tank pump for circulation

#### Printed parts
- Raspberry PI DIN rail mount [Thingiverse](https://www.thingiverse.com/thing:2659908)
- DIN rail mount for the LM2596 [Thingiverse](https://www.thingiverse.com/thing:4415585)
- DIN rail mount for MW power supply [Thingiverse](https://www.thingiverse.com/thing:4415618)

### Wiring scheme

Still to be done some day ...
