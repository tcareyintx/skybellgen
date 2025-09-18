# SkyBellGen

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacs-badge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

## Description

![SkyBell](skybell.png)

The **SkyBellGen** integration is used to integrate with doorbell devices from [SkyBell](https://skybell.com/).
The access to the doorbell is via the [SkyBellGen communication driver](https://pypi.org/project/aioskybellgen/)
that implements the [SkyBell cloud API](https://api.skybell.network/docs/). The integration can be used in automations that use changes and event's detected by SkyBell doorbell. See the [examples](#examples) section for more ideas of how to use this integration.

## Prerequisites

1. Open the app store and install the **SkyBell** app.
2. [Create an account](https://support.skybell.com/hc/en-us/articles/36672108421645-Account-Creation-and-Verification).
   You will use the username(email) and password to connect to the SkyBell cloud API.
3. Follow the app instructions to discover the SkyBell devices.

## Installation

### HACS

Installation through [HACS][hacs] is the preferred installation method.

[![Open the SkyBellGen integration in HACS][hacs-badge]][hacs-open]

1. Click the button above or go to HACS &rarr; Integrations &rarr; search for
   "SkyBellGen" &rarr; select it.
1. Press _DOWNLOAD_.
1. Select the version (it will auto select the latest) &rarr; press _DOWNLOAD_.
1. Restart Home Assistant then continue to [the setup section](#setup).

### Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `skybellgen`.
4. Download _all_ the files from the `custom_components/skybellgen/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant then continue to [the setup section](#setup).

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/skybellgen/translations/en.json
custom_components/skybellgen/__init__.py
custom_components/skybellgen/binary_sensor.py
custom_components/skybellgen/button.py
custom_components/skybellgen/camera.py
custom_components/skybellgen/config_flow.py
custom_components/skybellgen/const.py
custom_components/skybellgen/coordinator.py
custom_components/skybellgen/diagnostics.py
custom_components/skybellgen/entity.py
custom_components/skybellgen/icons.json
custom_components/skybellgen/kvs.py
custom_components/skybellgen/light.py
custom_components/skybellgen/manifest.json
custom_components/skybellgen/number.py
custom_components/skybellgen/select.py
custom_components/skybellgen/sensor.py
custom_components/skybellgen/services.py
custom_components/skybellgen/services.yaml
custom_components/skybellgen/strings.json
custom_components/skybellgen/switch.py
custom_components/skybellgen/text.py
```

## Removing the integration

This integration follows standard integration removal via the UI.

1. Go to Settings > Devices & Services
2. Click on the SkyBellGen integration that you loaded
3. Delete all the hubs by selecting each hub and then delete from the options menu (vertical dots)

## Setup

Configuration is done via the Home Assistant UI after installation.

1. Navigate to "Settings" &rarr; "Devices & Services"
1. Click "+ Add Integration"
1. Search for and select &rarr; "SkyBellGen"

Follow the instructions to configure the integration.

## Configuration flow

This integration uses the HA configuration flow to setup a new SkyBellGen hub by selecting the Add hub option from the integration.

email:

- description: Your email that you used when setting up the account on the SkyBell app.

password:

- description: Your password that you used when setting up the account on the SkyBell app. If you
  change your password you can use the reconfigure or re-authentication options of the integration configuration flow.

use local UDP server for event capture:

- description: When checked and the local UDP event server has been started (via a service), you will receive Button Pressed and Motion Detection events locally that are broadcasted by the device.

## Data updates {#data-updates}

The SkyBellGen integration fetches data from the device via the SkyBell cloud API every 600 seconds (10 minutes). When enabled, the SkyBellGen integration updates local Button Pressed and Motion detection events every 5 seconds.

The SkyBellGen integration will refresh hub and session data at least every 3600 seconds (1 hour). The timeframe may be sooner passed on the session refresh expiration period received from the Cloud API server.

If the refresh cycle for the device data isn't frequent enough, you can create an automation for any entity in the device that receives it's data from the cloud API to manually update its data at a faster pace. It is recommended that the shortest interval is 30 seconds as to not overload the Cloud API server with many requests. If you need a faster poll cycle, look into using the local event server.

## Examples {#examples}

The SkyBellGen integration provides actuators to modify attributes of the SkyBell devices. Additionally the integration provides sensors that are updated with the refresh cycle documented in the [Data updates](#data-updates) section.
These actuators and sensors provided by the integration permits example automations as described in this section.

### Turning on the exterior lights when motion is detected by the SkyBell

If the doorbell is pressed or motion is detected, the SkyBellGen integration's sensors can detect the event and activate, via automations, other entities that can turn on exterior lighting.

### Monitoring the last motion event detected by the SkyBell

When a motion event is detected by the SkyBell, a video is recorded that can be viewed and/or downloaded by the SkyBellGen integration.

### Modifying the configuration for a SkyBell doorbell

The SkyBellGen integration provides actuators to configure attributes of the SkyBellGen inorder to modify the behavior of the device. For example, the sensitivity of the motion being detected by the doorbell's camera can be adjusted in order to provide a better viewing experience.

## Supported devices

The following devices are known to be supported by the SkyBellGen integration:

- SkyBell SlimLine II - Model number: SB_SLIM2_0001

## Unsupported devices

The following devices are not supported by the integration:

- Devices that have not been migrated to the SkyBell Genv5 API and associated SkyBell app.

## Supported functionality

The SkyBellGen integration provides support for the platforms listed below.

| Platform        | Description                                         |
| --------------- | --------------------------------------------------- |
| `binary_sensor` | Show info from switch and light actuators.          |
| `button`        | Trigger actions like reboot doorbell.               |
| `camera`        | Show snapshot images, videos of activities and view real-time(live) video from the doorbell camera.|
| `light`         | Actuator for the doorbell's led.                    |
| `number`        | Actuator for entities that input numeric values.    |
| `select`        | Actuator for entities that input enumerated values. |
| `sensor`        | Show info from actuators and diagnostic sensors.    |
| `switch`        | Actuator for entities that input binary values.     |
| `text`          | Actuator for entities that input text values.       |

### Entities

The SkyBellGen integration provides the following entities.

#### Binary Sensors

Sensors for corresponding entities in Light and Switch entities. These sensors can be used when the doorbell is shared and the user has "read-only" privileges.

#### Buttons

- **Reboot doorbell**
  - **Description**: Reboots the doorbell.

#### Camera

- **Last activity**
  - **Description**: The last recorded activity such as a livestream, button press or motion detection event.

- **Livestream**
  - **Description**: The real-time (live) stream from the doorbell's camera.

- **Snapshot**
  - **Description**: The last recorded snapshot using the doorbell's camera.

#### Light

- **Button light**
  - **Description**: The led for the doorbell's button.
  - **Remarks**: The brightness is not used, only the ability to turn-on and off the led along with setting the button led's color.

#### Numbers

- **Motion sensitivity**
  - **Description**: The sensitivity used by the doorbell's camera to determine if there is motion detected.
  - **Remarks**: Values are expressed as percentages between .3 and 100.0 percent.

- **Human detection sensitivity**
  - **Description**: The sensitivity used by the doorbell's camera to determine if there is a human body is detected.
  - **Remarks**: Values are expressed as percentages between .3 and 100.0 percent.

- **Facial detection sensitivity**
  - **Description**: The sensitivity used by the doorbell's camera to determine if there is a human face detected.
  - **Remarks**: Values are expressed as percentages between .3 and 100.0 percent.

- **Infrared sensitivity**
  - **Description**: The infrared radiation (heat) sensitivity used by the doorbell's camera to determine if there is motion detected.
  - **Remarks**: Values are expressed as percentages between .3 and 100.0 percent.

- **Location latitude**
  - **Description**: The latitude coordinate for where the doorbell is located.

- **Location longitude**
  - **Description**: The langitude coordinate for where the doorbell is located.

#### Selects

- **Outdoor chime volume**
  - **Description**: When the outdoor chime is enabled, the volume of the outdoor chime.
  - **Options**: Low, Medium, High

- **Speaker volume**
  - **Description**: When using a livestream vent, the volume of the audio speaker.
  - **Options**: Low, Medium, High

- **Image quality**
  - **Description**: Resolutions associated with video recordings
  - **Options**: Low (480p), Medium (720p), High (720p), Highest (1080p)

#### Switches

- **Detect button pressed**
  - **Description**: When enabled, notifications are emitted with the doorbell button is pressed.

- **Detect motion**
  - **Description**: Motion detection is enabled or disabled.

- **Detect motion - debug**
  - **Description**: When motion detection is enabled, a box is drawn around the detected person or face when is enabled.

- **Notify on motion detection event**
  - **Description**: Wnen motion detection is enabled, determines if notifications are emitted.

- **Record on motion detection event**
  - **Description**: Wnen motion detection is enabled, determines if video is recorded.

- **Notify on human body detection event**
  - **Description**: Wnen motion detection is enabled, determines if notifications are emitted.

- **Record on human body detection event**
  - **Description**: Wnen motion detection is enabled, determines if video is recorded.

- **Notify on facial detection event**
  - **Description**: Wnen motion detection is enabled, determines if notifications are emitted.

- **Record on facial detection event**
  - **Description**: Wnen motion detection is enabled, determines if video is recorded.

- **Indoor chime**
  - **Description**: Wnen enabled, the indoor mechanical chime will be used.

- **Indoor digital chime**
  - **Description**: Wnen enabled, the indoor digital chime will be used.
  - **Remarks**: Not this entity should be off if the Indoor chime is enabled.

- **Outdoor chime**
  - **Description**: Wnen enabled, the outdoor chime will be used.

#### Sensors

Sensors for corresponding entities in Number, Select and Text entities. These sensors can be used when the doorbell is shared and the user has "read-only" privileges and are considered diagnostic sensors. Additionally:

- **Last button event**
  - **Description**: The timestamp of the last recorded doorbell button pressed event provided by the Cloud API.

- **Last motion event**
  - **Description**: The timestamp of the last recorded doorbell motion event provided by the Cloud API.

- **Last local button event**
  - **Description**: The timestamp of the last recorded doorbell button pressed event broadcast by the device.

- **Last local motion event**
  - **Description**: The timestamp of the last recorded doorbell motion event broadcast by the device.

- **Last livestream event**
  - **Description**: The timestamp of the last recorded doorbell livestream event.

- **Last seen**
  - **Description**: The last time the doorbell has checked in with the SkyBell cloud.
  - **Remarks**: Diagnostics, disabled by default

- **Last connected**
  - **Description**: The timestamp of the last recorded doorbell connection event.
  - **Remarks**: Diagnostics, disabled by default

- **Last disconnected**
  - **Description**: The timestamp of the last recorded doorbell disconnection event.
  - **Remarks**: Diagnostics, disabled by default

- **Wi-Fi SSID**
  - **Description**: The SSID that the doorbell's of the Access Point to which the doorbell is connected.
  - **Remarks**: Diagnostics, disabled by default

- **Wi-Fi link quality**
  - **Description**: The link quality (xx/100) of the doorbell's Wi-Fi connection.
  - **Remarks**: Diagnostics, disabled by default

#### Texts

- **Doorbell name**
  - **Description**: The name that will be associated with the doorbell.
  - **Remarks**: Entities for the doorbell use the name of the doorbell when the device is first discovered. Changing the name does not change the entity ids for the doorbell's entities.

- **Location place**
  - **Description**: The name that will be associated with the location's longitude and latitude coordinates.

## Services

The SkyBell integration exposes the following services (actions) that can be used in automations.

### Start local event server

This service starts the local event server that is used to capture UDP broadcast events from the SkyBell doorbell. The Button Pressed and Motion Detection events are captured and presented to Home Assistant via the associated Last local button event and Last local motion event sensors.

#### Fields

interface: The interface field is an optional string field that, when provided, will restrict the local event service to the specified interface. If the field is empty or not provided, then all interfaces "0.0.0.0" is used.

### Stop local event server

This service stops the local event server that is used to capture UDP broadcast events from the SkyBell doorbell.

## Known limitations

The SkyBell integration exposes many of the capabilities and attributes of the SkyBell doorbell. However, there are capabilities and attributes that are not currently exposed using the integration. For these limitations, the SkyBell app should be used.

### SkyBellGen integration capabilities that are not supported

1. Currently devices are discovered when the a new hub is created. If devices are added or removed via the SkyBell cloud API, the hub in the will continue to remove stale devices as well as add new devices. However, if Home Assistant is restarted, information that permits the integration to keep track of stale devices is lost. In this scenario the user can still manually delete the stale device through the Home Assistant UI.

### SkyBell cloud API capabilities that are not supported

1. Maintaining the SkyBell cloud API account. Including changing the password and sharing access to devices
2. The use of Access tokens to log into the SkyBell cloud API
3. Adding and removing new devices to the SkyBell cloud API
4. Maintaining (deleting) and viewing the historical activity events
5. Webhook triggers emitted by the Cloud API for various doorbell events

### SkyBell cloud API attributes that are not supported

1. SkyBell premium account attributes and capabilities
2. Setting chime tones for the doorbell press and motion detection events
3. Advanced motion detection zones

### Multiple camera viewers for real-time(live) streaming is not supported

1. Currently only one camera can view the real-time(live) streaming event at a time. If the livestream camera is used by another device or a different browser (viewer) on the same device, the new viewer will see the snapshot of the livestream but will not be able to view the livestream.

## Troubleshooting

### Diagnostics

Redacted diagnostics is available for each Hub entry and/or device. These can be downloaded using the Home Assistant diagnostic interface for the SkyBellGen Hub and Device information entities.

### My password has changed

#### Symptom: “Invalid authentication”

If the password has changed or the session authentication tokens have timed out.

##### Description

This means the integration has to re-authenticate with the SkyBell cloud.

##### Resolution

To resolve this issue, follow the steps in the reauthentication flow. If the password was changed using the SkyBell cloud API or SkyBell app, you can reconfigure the integration and supply the new password before the authentication timeout.

### I still see a stale device

#### Symptom: “The SkyBellGen hub continues to show the device”

If the device as removed via the SkyBell cloud API or SkyBell app but Home Assistant has been restarted, stale devices may still
exist in the Home Assistant device registry.

##### Description

This means the integration doesn't recognize that the device is a stale device.

##### Resolution

To resolve this issue, manually delete the device from the SkyBellGen Hub.

<!---->

## Contributions are welcome

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Credits

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template.

The project used the Home Assistant core [SkyBell](https://www.home-assistant.io/integrations/skybell/) core component as the starting point.

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/tcareyintx/skybellgen.svg?style=for-the-badge
[commits]: https://github.com/tcareyintx/skybellgen/commits/main
[hacs]: https://hacs.xyz/
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[hacs-open]: https://my.home-assistant.io/redirect/hacs_repository/?owner=tcareyintx&repository=SkyBellGen&category=integration
[releases]: https://github.com/tcareyintx/skybellgen/releases
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/tcareyintx/skybellgen.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40tcareyintx-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/tcareyintx/skybellgen.svg?style=for-the-badge
[user_profile]: https://github.com/tcareyintx
