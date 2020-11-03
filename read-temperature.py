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

PAUSED = False
seed(1)


def send_device_temperature():
    global PAUSED
    try:
        if not PAUSED:
            temperature = 45 + gauss(0, 1)
            client.publish(
                topic='machine/temperature',
                queueFullPolicy="AllOrException",
                payload=json.dumps({"CPU": temperature, "message": "Running", "time": "{}".format(datetime.now())})
            )
        else:
            logger.info("Send temperature paused")

    except Exception as exc:
        logger.error('Error publishing temperature: ' + repr(exc))

    Timer(10, send_device_temperature).start()


send_device_temperature()


def function_handler(event, context):
    global PAUSED
    logger.info("Event received: " + json.dumps(event, indent=2))
    if event['send'] == 1:
        if PAUSED:
            PAUSED = False
            logger.info("Resuming transmission")
            client.publish(
                topic='machine/temperature',
                queueFullPolicy="AllOrException",
                payload=json.dumps({"message": "Resume", "time": "{}".format(datetime.now())})
            )
        else:
            logger.info("Device is transmitting")
    elif event['send'] == 0:
        if not PAUSED:
            PAUSED = True
            logger.info("Suspending transmission")
            client.publish(
                topic='machine/temperature',
                queueFullPolicy="AllOrException",
                payload=json.dumps({"message": "Suspend", "time": "{}".format(datetime.now())})
            )
        else:
            logger.info("Device is already paused")
    return
