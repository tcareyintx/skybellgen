# SkybellGen

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

## Description
![Skybell](skybell.png)

The **SkybellGen** integration is used to integrate with doorbell devices from [Skybell](https://skybell.com/).
The access to the doorbell is via the [SkybellGen communication driver](https://pypi.org/project/aioskybellgen/)
that implements the [Skybell cloud API](https://api.skybell.network/docs/).
The integration provides support for the platforms listed below.

| Platform        | Description                                                        |
| --------------- | ------------------------------------------------------------------ |
| `binary_sensor` | Show info from SkybellGen API for switch and light actuators.      |
| `button`        | Trigger actions like reboot doorbell using the SkybellGen API.     |
| `camera`        | Show images and videos of activities.                              |
| `light`         | Actuator for SkybellGen API led lights.                            |
| `number`        | Actuator for SkybellGen API entities that input numeric values.    |
| `select`        | Actuator for SkybellGen API entities that input enumerated values. |
| `sensor`        | Show info from SkybellGen API actuators.                           |
| `switch`        | Actuator for SkybellGen API entities that input binary values.     |
| `text`          | Actuator for SkybellGen API entities that input text values.       |

## Prerequisites

1. Open the app store and install the **Skybell** app.
2. [Create an account](https://support.skybell.com/hc/en-us/articles/36672108421645-Account-Creation-and-Verification).
You will use the username(email) and password to connect to the Cloud API.
3. Follow the app instructions to discover the Skybell devices.

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `skybellgen`.
4. Download _all_ the files from the `custom_components/skybellgen/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "SkybellGen"

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

## Configuration is done in the UI
This integration uses the HA configuration flow to setup the SkybellGen hub.
email:
- description: Your email that you used when setting up the account on the Skybell app.
password:
- description: Your password that you used when setting up the account on the Skybell app.
If you change your password you can use the reconfigure or re-authentication options of the integration configuration flow.

<!---->

## Contributions are welcome!

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
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/tcareyintx/skybellgen.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40tcareyintx-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/tcareyintx/skybellgen.svg?style=for-the-badge
[releases]: https://github.com/tcareyintx/skybellgen/releases
[user_profile]: https://github.com/tcareyintx
