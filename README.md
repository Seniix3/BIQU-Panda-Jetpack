<p align="center">
  <img src="images/logo.png" alt="BIQU logo" width="180">
</p>

# Panda Jetpack for Home Assistant

Custom integration for the **BIGTREETECH Panda Jetpack** LED controller
(Bifrost Engine web interface), controlled over its local WebSocket API.

## Entities

| Entity | Type | Function |
|---|---|---|
| Panda Jetpack | `light` | On/off, brightness (0-100%), light effect selection |
| Effect speed | `number` | Speed of animated effects (0-100%) |

Supported effects: Static, Breathing, Strobing, Wave, Marquee, Color Cycle,
Rainbow, Warning Hot, Fan Speed, H2D Style.

Note: brightness and speed are stored **per effect** by the device, and the
speed slider only affects animated effects (it does nothing for Static / H2D
Style) — the same behaviour as the device's own web interface.

## Installation

### Via HACS (custom repository)

1. Push this folder to a GitHub repository (see structure below).
2. HACS -> three-dot menu -> **Custom repositories** -> add the repo URL,
   category **Integration**.
3. Install "Panda Jetpack" from HACS and restart Home Assistant.

### Manual

1. Copy `custom_components/panda_jetpack/` into your Home Assistant
   `config/custom_components/` folder.
2. Restart Home Assistant.

## Configuration

Settings -> Devices & services -> **Add integration** -> search for
"Panda Jetpack" -> enter the device's IP address. No YAML needed.

## Repository structure (for HACS)

```
your-repo/
├── hacs.json
├── README.md
└── custom_components/
    └── panda_jetpack/
        ├── __init__.py
        ├── api.py
        ├── config_flow.py
        ├── const.py
        ├── entity.py
        ├── light.py
        ├── manifest.json
        ├── number.py
        ├── strings.json
        └── translations/
            ├── en.json
            └── nl.json
```

## Integration icon in Home Assistant (brands repo)

Home Assistant only loads integration icons from `brands.home-assistant.io`,
so the icon cannot be bundled with the integration itself. Ready-to-use icon
files are included in the `brands/` folder of this repository:

```
brands/custom_integrations/panda_jetpack/icon.png      (256x256)
brands/custom_integrations/panda_jetpack/icon@2x.png   (512x512)
```

To get the icon showing in Home Assistant:

1. Fork [home-assistant/brands](https://github.com/home-assistant/brands).
2. Copy the `custom_integrations/panda_jetpack/` folder from `brands/` into
   the fork (same path).
3. Open a pull request. Once merged, the icon appears automatically —
   no changes to the integration needed.

Until then Home Assistant shows a generic placeholder; everything else
works normally.
