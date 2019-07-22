# Raspberry PI Temperature Sensor

## Introduction

This detailed example can be used to configure Edge One™ on a Raspberry Pi-3 to read data from a number of popular sensors.  Note that we only describe how to read data into Edge One. Publishing the data into
CloudPlugs IoT requires the configuration of an Edge One Message Router or Flows project.

In this section we show:

1. How to [read data without using Docker](#Read-data-without-using-Docker).
2. How to [read sensor data using Docker](#Read-data-using-Docker).  Here we describe all steps to:
	* Configure a custom container.
	* Publish the container to the CloudPlugs IoT registry
3. An [example of a SmartPlug App](#Sample-SmartPlug-App-container-orchestrator) that can be used to orchestrate and run a Docker container. Such container may be an Edge One™ Docker Container or a Custom Docker Container.

## Supported sensors

The sensors supported include:

* DHT 11
* DHT 22
* DHT 2302
* DS18B20 (one-wire)

The DHT should be wired using the GPIO pins of the Raspberry Pi.

## Prerequisites

Edge One™ should be installed and configured in the Raspberry Pi.

## Read data without using Docker

This section describes how to read the sensor data with Edge One™ without using Docker.  Note that **this example only publishes data to the Edge One™ message broker.**  To send the
data to CloudPlugs IoT you must either:

  1. Set up a route using the Edge One™ [Message Router](https://docs.cloudplugs.com/edge-one/Gateway/Modules/message-router/Router-Overview), or
  2. Use Edge One™ [Flows](https://docs.cloudplugs.com/edge-one/Gateway/Modules/flows/Flows-Overview) to send the data.
  
The following steps indicate how to install and configure the device to send data to Edge One™.

1. Install the required dependencies as root:

```
sudo su
apt-get install python-dev python-setuptools
pip install paho-mqtt
```

2. Build and install the Adafruit_DHT library with the following commands:

```
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
python setup.py install
cd ..
```

Once the library is configured, you are ready to read data from the sensors.  Here are two examples on how to **read data into an Edge One™ Project** called **io-test-project** from two different sensors:

### Read data from a DS18B20 attached through 1-wire

```
MQTT_USER="uid" MQTT_PASS="pwd" SENSOR="DS18B20" PIN=0 PROJECT_ID="iot-test-project" python main.py
```

Where the "uid" of MQTT_USER is the id of a valid user of Edge One and "pwd" is the user's password.

### Read data from a DHT22 attached to GPIO4:

```
MQTT_USER="uid" MQTT_PASS="pwd" SENSOR="22" PIN=4 PROJECT_ID="iot-test-project" python main.py
```

Where the "uid" is the id of a valid user of Edge One and "pwd" is the user's password.

## Read data using Docker

Follow these steps:

1. [Build the container image](#Build-the-container-image-locally).
2. [Create and start the container layer](#Create-and-start-the-container-layer).
3. [Publish the container](#Publish-the-container-to-CloudPlugs-IoT) into CloudPlugs IoT.  From here, it can be associated and deployed to multiple devices.

### Build the container image locally

In this example we build an image named **rpi-temp-sensor** with tag equal to **latest**.

```
docker build -t rpi-temp-sensor .
```

### Create and start the container layer

We use **docker run** to create and start the container layer to read data from the sensor and to publish the data into an Edge One Project with ID **iot-test-project**.

The format of the command is as follows:

```
docker run --privileged rpi-temp-sensor -e SENSOR=[11|22|2302|DS18B20] -e PIN=GPIOpin# -e MQTT_USER=uid -e MQTT_PASS=pwd -e PROJECT_ID="iot-test-project"
```

where SENSOR must equal the target sensor, PIN should equal the target GPIO pin, **uid** is the id of a valid Edge One user and **pwd** is the user's password.

For example, to read from a DHT22 attached to GPIO4:

```
docker run --privileged rpi-temp-sensor -e SENSOR=22 -e PIN=4 -e MQTT_USER=uid -e MQTT_PASS=pwd -e PROJECT_ID="iot-test-project"
```

To publish the data into CloudPlugs IoT you must either:

  1. Set up a route using the Edge One™ [Message Router](https://docs.cloudplugs.com/edge-one/Gateway/Modules/message-router/Router-Overview), or
  2. Use Edge One™ [Flows](https://docs.cloudplugs.com/edge-one/Gateway/Modules/flows/Flows-Overview) to send the data.

### Publish the container to CloudPlugs IoT

The container image can be published into the CloudPlugs IoT Registry to be distributed to other devices running Edge One™ or a SmartPlug™.  To push and publish a container to the 
CloudPlugs IoT Registry, you can following the procedure described in the [documentation](https://docs.cloudplugs.com/kb/User-Guides/Containers/Containers#push).

Remember to **create** the **namespace** and the **container image placeholder** as described in the documentation.

For reference, here are the commands to publish the container image **rpi-temp-sensor**:

```
docker tag rpi-temp-sensor registry.cloudplugs.com/my-edge-namespace/rpi-temp-sensor:latest

docker login registry.cloudplugs.com
(You need to use the credentials of a CloudPlugs IoT user account allowed to publish images. Your company credentials with the email and password can be used).

docker push registry.cloudplugs.com/my-edge-namespace/rpi-temp-sensor:latest
```

**Verify** that the container shows in the CloudPlugs IoT registry.

Using the CloudPlugs IoT Web Desktop, the container can now be associated with the Production Template that has serial numbers of Raspberry Pi devices or to Things that are Raspberry Pi devices with a DHT temperature sensor attached to it.

To orchestrate and run the container using a SmartPlug™ (either the Edge One™ SmartPlug™ or a standalone SmartPlug™), use the SmartPlug App described in the next section.

## Sample SmartPlug App container orchestrator

Here is a SmartPlug™ application that can be used to orchestrate the container created in the previous section.  It can be easily modified to orchestrate any container.

1. Open the **SmartPlug Apps** application in the CloudPlugs IoT Web Desktop.
2. In the **Scripts** panel, click on **+** to create a New application of Type **Automatic Execution*.*
3. Copy the code below and paste it to the new script application.  Make sure that you make the adjustments necessary for your example.

```
var docker = require('cloudplugs').docker;

var containerName = 'rpi-temp-sensor';
var yourContainer = 'my-edge-namespace/' + containerName;

var origin = 'registry.cloudplugs.com/' + yourContainer + ':latest';

docker.pull(origin, function(err, res) {
	if (err) {
		console.log("ERR PULL" + origin + ": " + err);
	} else {
		docker.tag(origin, yourContainer + ':latest', function(err, res) {
			if(err) console.log("ERR TAG "+origin+": " + err);
			else {
				var dockconf = {
					name: containerName,
					Image: yourContainer,
					Cmd: [],
					Env: [],
					AttachStdin: false,
					AttachStdout: false,
					AttachStderr: false,
					Tty: false,
					OpenStdin: false,
					StdinOnce: false,
					HostConfig: {
						AutoRemove: true,
						Privileged: true,
						Mounts: []
					}
				}
				docker.docker.createContainer(dockconf, function(err, container) {
					if(err) {
						return console.error("Cannot create container " + yourContainer + ": " + err);
					}
					return container.restart(function(err) {
						if(err) return console.error("Cannot start container " + yourContainer + ": " + err);
					})
				})
			}
		})
	}
});
```

4. **Save and Commit** the application.
5. **Deploy** the application (cloud icon) from the **Scripts** panel.
6. Associate the application with a Thing or Production Template through **SmartPlug->SmartPlug Apps** using the Templates or Things Management console, and **Save** to deploy and run the
application on the SmartPlug of the target devices.
7. The target device SmartPlug will run the application which downloads and executes the container.

