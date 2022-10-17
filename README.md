# pylcn
a python project for communication between alexa and LCN-PCHK.
The Amazon Echo is able to control certain types of home automation devices by voice. 
the package Fauxmo provides emulated Belkin Wemo devices that the Echo can turn on and off by voice, locally, and with minimal lag time. 
Currently these Fauxmo devices can be configured to make requests to an HTTP server or to a Home Assistant instance via its Python API and 
only require a JSON config file(lcn_device.json) for setup.

## usage
1. in you python env. install Fauxmo and pypck
2. adjust the configuration in lcn_device.json, etc. seg_id, mod_id, control_type...
   currently only support R8H and DIMOutput, you could self add the implementation in lcn_plugin.py. 
4. start pypck.py or run run.bar directly
5. use Alexa App search the new devices, that you in lcn_device.json defined.
6. append the found devices into Alexa Device manager, then have a good fun!
