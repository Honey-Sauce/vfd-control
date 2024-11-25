# VFD Control
Interface between vacuum florescent displays with 14-pin connectors and a Raspberry Pi-type device with a GPIO interface. 

- Time and Weather: Includes a clock display mode that shows the time and weather and a media mode to display now playing data from the upcoming BEE-TV API

- Home Automation Ready: Interfaces with the Home Assistant API to display weather data, leaving the door open to bring forward other HA sensor data in the future

- Ready to Interface with the Broadcast Emulation Engine: Preconfigured to interface with the BEE to display metadata from live media.

# INSTALLATION
Download files to a raspberry pi, set configuration options in config.py and run with python3
To run the VCR display script on boot, add `python3 /path/to/file/vcr.py` to your `/etc/rc.local` file
