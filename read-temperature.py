import json
import logging
import sys
from threading import Timer

import greengrasssdk
from datetime import datetime

from random import (seed, gauss)

# Set up logging to stdout
# TODO - add logging to file or dynamodb

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Attach the client to the 'io-data' which is the greengrass core

client = greengrasssdk.client("iot-data")

# Global PAUSED variable, used to control flow of temperatures

PAUSED = False

# Global MACHINE_NAME variable, part of message published

MACHINE_NAME = "greengrass-ec2"
seed(1)


# Timed event to publish the current 'temperature' to the iot-data MQTT
# on the topic 'machine/temperature'

def send_device_temperature():
    global PAUSED
    global MACHINE_NAME
    try:
        if not PAUSED:
            # If the temperature publishing is not paused, publish the 'temperature to the queue
            # Since we are running on an ec2 instance, well just make up a temperature

            temperature = 45 + gauss(0, 1)
            client.publish(
                topic='machine/temperature',
                queueFullPolicy="AllOrException",
                payload=json.dumps({"machine": MACHINE_NAME, "CPU": temperature, "message": "Running", "time": "{}".format(datetime.now())})
            )
        else:
            logger.info("Send temperature paused")

    except Exception as exc:
        logger.error('Error publishing temperature: ' + repr(exc))

    # Let it go around again in 10 seconds

    Timer(10, send_device_temperature).start()

# Initiate publishing the temperatures

send_device_temperature()


# Lambda function to handle control events

def function_handler(event, context):
    global PAUSED
    global MACHINE_NAME
    logger.info("Event received: " + json.dumps(event, indent=2))

    if event['send'] == 1:

        # If the event payload contains 'send': 1 we are starting the temperature flow

        if PAUSED:
            PAUSED = False
            logger.info("Resuming transmission")
            client.publish(
                topic='machine/temperature',
                queueFullPolicy="AllOrException",
                payload=json.dumps({"machine": MACHINE_NAME, "message": "Resume", "time": "{}".format(datetime.now())})
            )
        else:
            logger.info("Device is transmitting")

    elif event['send'] == 0:

        # If the event payload contains 'send': 0 we are stopping the temperature flow

        if not PAUSED:
            PAUSED = True
            logger.info("Suspending transmission")
            client.publish(
                topic='machine/temperature',
                queueFullPolicy="AllOrException",
                payload=json.dumps({"machine": MACHINE_NAME, "message": "Suspend", "time": "{}".format(datetime.now())})
            )
        else:
            logger.info("Device is already paused")

    return
