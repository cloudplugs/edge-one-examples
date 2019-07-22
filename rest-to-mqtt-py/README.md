# Simple REST to MQTT Bridge

## Introduction

This Python example creates a REST endpoint that takes the variable "name" as an input and relays the information using the Edge One data structure.
The example creates and uses an Edge One Project called **iot-test-project.**

## Prerequisites

Edge One should be installed and configured in the target device.

## Use the Bridge without Docker

Install the dependencies as root:

```
apt-get install python-dev python-setuptools
pip install paho-mqtt flask-restful
```

You can run the bridge with the default port 3000:

```
MQTT_USER="uid" MQTT_PASS="pwd" PROJECT_ID="iot-test-project" python main.py
```

Where **uid** is the id of a valid Edge One user and **pwd** is his password.

In another Edge One (SmartPlug) terminal, you can send a sample request with:

```
curl -X POST http://localhost:3000/api/data -d name="John"
```

The data will be displayed in the Project **iot-test-project** Data.

## Use the Bridge with Docker

Follow these steps:

1. [Build the container image](#Build-the-container-image-locally).
2. [Create and start the container layer](#Create-and-start-the-container-layer).
3. [Publish the container](#Publish-the-container-to-CloudPlugs-IoT) into the CloudPlugs IoT Container Registry.  From here, it can be associated and deployed to other devices.

### Build the container image locally

In this example we build an image named **rest-mqtt-bridge** with tag equal to **latest**.

```
docker build -t rest-mqtt-bridge .
```

### Create and start the container layer

We use **docker run** to create and start the bridge, and to expose the default port 3000 associated with an Edge One Project called **iot-test-project.**

```
docker run --privileged rest-mqtt-bridge -e MQTT_USER=uid -e MQTT_PASS=pwd -e PROJECT_ID="iot-test-project" -p 3000:3000
```

Where **uid** is the id of a valid Edge One user and **pwd** is his password.

You can send a sample request with:

```
curl -X POST http://localhost:3000/api/data -d name="John"
```
### Publish the container to CloudPlugs IoT

The container image can be published into the CloudPlugs IoT Registry to be distributed to other devices running Edge One™ or a SmartPlug™.  To push and publish a container to the 
CloudPlugs IoT Registry, you can following the procedure described in the [documentation](https://docs.cloudplugs.com/kb/User-Guides/Containers/Containers#push).

Remember to **create** the **namespace** and the **container image placeholder** as described in the documentation.

For reference, here are the commands to publish the container image **rest-mqtt-bridge**:

```
docker tag rest-mqtt-bridge registry.cloudplugs.com/my-edge-namespace/rest-mqtt-bridge:latest

docker login registry.cloudplugs.com
(You need to use the credentials of a CloudPlugs IoT user account allowed to publish images. Your company credentials with the email and password can be used).

docker push registry.cloudplugs.com/my-edge-namespace/rest-mqtt-bridge:latest
```

**Verify** that the container shows in the CloudPlugs IoT registry.

Using the CloudPlugs IoT Web Desktop, the container can now be associated with a Production Template or with individual Things that will operate as a bridge.

To orchestrate and run the container using a SmartPlug™ (either the Edge One™ SmartPlug™ or a standalone SmartPlug™), use the SmartPlug App described in the next section.

## Sample SmartPlug App container orchestrator

Here is a SmartPlug™ application that can be used to orchestrate the container created in the previous section.  It can be easily modified to orchestrate any container.

1. Open the **SmartPlug Apps** application in the CloudPlugs IoT Web Desktop.
2. In the **Scripts** panel, click on **+** to create a New application of Type **Automatic Execution*.*
3. Copy the code below and paste it to the new script application.  Make sure that you make the adjustments necessary for your example.

```
var docker = require('cloudplugs').docker;

var containerName = 'rest-mqtt-bridge';
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


