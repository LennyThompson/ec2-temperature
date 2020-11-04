# Greengrass IoT Lambda - at the edge

Edge device - IoT Core - lambda.

Publishes device 'temperature' to Iot-Data MQTT on topic 'machine/temperature'.

Should be subscribed to a topic that will allow the control of the device, for instance 'machine/control'.

## CI/CD

Has none. Needs further investigation.

Manual deploy process:

1. Add/Update lambda with zipped content of the python
```bash
zip -r read_temperature_python_lambda.zip greengrasssdk read-temperature.py
```

    * Upload the zipped file to the AWS lambda Greengrass_ReadTemperature
    * Publish
    * Add alias
2. Delete/remove any existing lambda configuration in the AWS IoT Greengrass group 'GreengrassDeviceSetup_Group_e689ca44-e8fb-40a1-ae94-b428001e87bf'
3. Add the lambda alias above as a lambda in the group, and subscribe as a source to 'machine/temperature', and as a destination for 'machine/control'
4. Make sure the lambda is configure for 25 second timeout, 'Make this function long-lived and keep it running indefinitely' is checked
5. Deploy the configuration.

 Note that the 'edge device' must be running prior to the deployment, and greengrass daemon running.
 
 Start the ec2 instance
 Use the following to start the greengrass daemon
 
 ```bash
cd /greengrass/ggc/core/
sudo ./greengrassd start 
```

### Test the lambda is running from the AWS console
    * AWS IoI -> Test
    * Use the topic 'machine/temperature'
    * If no temperatures appear try publish to 'machine/control' the data { 'send': 1 }
    * Should see data arriving every 10 seconds
 
 