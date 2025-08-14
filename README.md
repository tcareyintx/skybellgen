# SkybellGen

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

![Skybell](skybell.png)

The **SkybellGen** integration is used to integrate with doorbell devices from [Skybell](https://skybell.com/).
The access to the doorbell is via the [SkybellGen communication driver](https://pypi.org/project/aioskybellgen/)
that implements the [Skybell cloud API](https://api.skybell.network/docs/). The integration be used in automations that use changes and event's detected by Skybell doorbell. See the [examples](#examples) section for more ideas of how to use this integration.

## Prerequisites

1. Open the app store and install the **Skybell** app.
2. [Create an account](https://support.skybell.com/hc/en-us/articles/36672108421645-Account-Creation-and-Verification).
   You will use the username(email) and password to connect to the Skybell cloud API.
3. Follow the app instructions to discover the Skybell devices.

## Installation

### HACS

Installation through [HACS][hacs] is the preferred installation method.

[![Open the SkybellGen integration in HACS][hacs-badge]][hacs-open]

1. Click the button above or go to HACS &rarr; Integrations &rarr; search for
   "SkybellGen" &rarr; select it.
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
custom_components/skybellgen/entity.py
custom_components/skybellgen/icons.json
custom_components/skybellgen/light.py
custom_components/skybellgen/manifest.json
custom_components/skybellgen/number.py
custom_components/skybellgen/select.py
custom_components/skybellgen/sensor.py
custom_components/skybellgen/strings.json
custom_components/skybellgen/switch.py
custom_components/skybellgen/text.py
```

## Removing the integration

This integration follows standard integration removal via the UI.

1. Go to Settings > Devices & Services
2. Click on the SkybellGen integration that you loaded
3. Click Delete

## Setup

Configuration is done via the Home Assistant UI after installation.

1. Navigate to "Settings" &rarr; "Devices & Services"
1. Click "+ Add Integration"
1. Search for and select &rarr; "SkybellGen"

Follow the instructions to configure the integration.

## Configuration flow

This integration uses the HA configuration flow to setup the SkybellGen hub.

email:

- description: Your email that you used when setting up the account on the Skybell app.

password:

- description: Your password that you used when setting up the account on the Skybell app. If you
  change your password you can use the reconfigure or re-authentication options of the integration configuration flow.

## Data updates {#data-updates}

The SkybellGen integration fetches data from the device via the Skybell cloud API every 30 seconds.

## Examples {#examples}

The SkybellGen integration provides actuators to modify attributes of the Skybell devices. Additionally the integration provides sensors that are updated with the refresh cycle documented in the [Data updates](#data-updates) section.
This actuators and sensors provided by the integration permits example automations as described in this section.

### Turning on the exterior lights when motion is detected by the Skybell

If the doorbell is pressed or motion is detected, the SkybellGen integration's sensors can detect the event and activate, via automations, other entities that can turn on exterior lighting.

### Monitoring the last motion event detected by the Skybell

When a motion event is detected by the Skybell, a video is recorded that can be viewed and/or downloaded by the SkybellGen integration.

### Modifying the configuration for a Skybell doorbell

The SkybellGen integration provides actuators to configure attributes of the SkybellGen inorder to modify the behavior of the device. For example, the sensitivity of the motion being detected by the doorbell's camera can be adjusted in order to provide a better viewing experience.

## Supported devices

The following devices are known to be supported by the SkybellGen integration:

- Skybell SlimLine II - Model number: SB_SLIM2_0001

## Unsupported devices

The following devices are not supported by the integration:

- Devices that have not been migrated to the Skybell Genv5 API and associated Skybell app.

## Supported functionality

The SkybellGen integration provides support for the platforms listed below.

| Platform        | Description                                         |
| --------------- | --------------------------------------------------- |
| `binary_sensor` | Show info from switch and light actuators           |
| `button`        | Trigger actions like reboot doorbell                |
| `camera`        | Show images and videos of activities                |
| `light`         | Actuator for the doorbell's led.                    |
| `number`        | Actuator for entities that input numeric values.    |
| `select`        | Actuator for entities that input enumerated values. |
| `sensor`        | Show info from actuators and diagnostic sensors.    |
| `switch`        | Actuator for entities that input binary values.     |
| `text`          | Actuator for entities that input text values.       |

### Entities

The SkybellGen integration provides the following entities.

#### Binary Sensors

Sensors for corresponding entities in Light and Switch entities. These sensors can be used when the doorbell is shared and the user has "read-only" privileges.

#### Buttons

- **Reboot doorbell**
  - **Description**: Reboots the doorbell.

#### Camera

- **Last activity**

  - **Description**: The last recorded activity such as a livestream, button press or motion detection event.

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

  - **Description**: The timestamp of the last recorded doorbell button pressed event.

- **Last motion event**

  - **Description**: The timestamp of the last recorded doorbell motion event.

- **Last livestream event**

  - **Description**: The timestamp of the last recorded doorbell livestream event.

- **Last seen**

  - **Description**: The last time the doorbell has checked in with the Skybell cloud.
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

## Known limitations

The Skybell integration exposes many of the capabilities and attributes of the Skybell doorbell. However, there are capabilities and attributes that are not currently exposed using the integration. For these limitations, the Skybell app should be used.

### SkybellGen integration capabilities that are not supported

1. Currently devices are discovered when the a new hub is created. If devices are added or removed via the Skybell cloud API, the hub in the SkybellGen integration will continue to remove stale devices as well as add new devices. However, if Home Assistant is restarted information that permits the integration to keep track of stale devices is lost. In this scenario the user can still manually delete the stale device through the
Home assistant UI.

### Skybell cloud API capabilities that are not supported

1. Maintaining the Skybell cloud API account. Including changing the password and sharing access to devices
2. The use of Access tokens to log into the Skybell cloud API
3. Adding and removing new devices to the Skybell cloud API
4. Maintaining (deleting) and viewing the historical activity events
5. Livestreaming through the doorbell's camera

### Skybell cloud API attributes that are not supported

1. Skybell premium account attributes and capabilities
2. Setting chime tones for the doorbell press and motion detection events
3. Advanced motion detection zones

## Troubleshooting

### My password has changed

#### Symptom: “Invalid authentication”

If the password has changed or the session authentication tokens have timed out.

##### Description

This means the integration has to re-authenticate with the Skybell cloud.

##### Resolution

To resolve this issue, follow the steps in the reauthentication flow. If the password was changed using the Skybell cloud API or Skybell app, you can reconfigure the integration and supply the new password before the authentication timeout.

### I still see a stale device

#### Symptom: “The SkybellGen hub continues to show the device”

If the device as removed via the Skybell cloud API or Skybell app but Home Assistant has been restarted, stale devices may still
exist in the Home Assistant device registry.

##### Description

This means the integration doesn't recognize that the device is a stale device.

##### Resolution

To resolve this issue, manually delete the device from the SkybellGen Hub.

<!---->

## Contributions are welcome

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Credits

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template.

The project used the Home Assistant core [Skybell](https://www.home-assistant.io/integrations/skybell/) core component as the starting point.

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/tcareyintx/skybellgen.svg?style=for-the-badge
[commits]: https://github.com/tcareyintx/skybellgen/commits/main
[hacs]: https://hacs.xyz/
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[hacs-open]: https://my.home-assistant.io/redirect/hacs_repository/?owner=tcareyintx&repository=SkybellGen&category=integration
[releases]: https://github.com/tcareyintx/skybellgen/releases
[config-flow-start]: https://my.home-assistant.io/redirect/config_flow_start/?domain=smartcar
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
