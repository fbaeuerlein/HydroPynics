# HydroPynics

## Description
In 2019 i started to do some experiments with hydroponics. So i decided to do some automation to control necessary pumps and have a better overview of the environmental conditions. Finally i came up with some electrical parts to recycle to a small automation solution with a Raspberry Pi. 

To do all the communication with sensors and acquiring the data, i implemented a small python script that is reading gpios and I2C to gather all the data and finally publishes via MQTT. Currently i use Nodred for visualization and remote control.

## Software

### Requirements

TODO

### Installation

TODO

### Nodered flows

See the nodered folder for the current flow i'm using.

## Hardware

### Wiring

**I'm dealing with 230 V AC and i'm not a professional electrician. All images, schemes, etc. were made to my best knowledge, but i'm not responsible for any damage, harms and losses resulting from the use of my work!**

![Image of the complete controller unit](https://github.com/fbaeuerlein/HydroPynics/blob/master/images/control.jpg)

### Components

- Ground fault circuit interruptor: Merlin Gerin 230V 30mA (This one is very important because we're dealing with water and voltage!)
- Power supply: Meanwell 50 Watt 24V 
- Power regulator: LM2596 DC-DC Converter
- Relays for switching pumps: IDEC 2-channel (important to switch both wires of the 230V!)
- Relays to switch 24V control voltage: 8-Channel relay card (the default one you find everywhere in the internet)
- ADS1115 for reading the NTCs
- NTCs: Some old ones from central heatings
- Raspberry Pi 3B
- Mounting: DIN Rail
- Other parts: wires, LEDs, screws, glue, pcbs, etc.

### Wiring scheme

A fritzing scheme is currently under construction ...
