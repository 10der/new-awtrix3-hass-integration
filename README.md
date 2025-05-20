# homeassistant custom_components awtrix3

[![Buy me a cofee](https://cdn.buymeacoffee.com/buttons/default-orange.png)](https://www.buymeacoffee.com/10der)

HASS awtrix3

# example

```
service: notify.awtrix_bedroom
data:
  message: The garage door has been open for 10 minutes.
```

or extend format
```
service: notify.awtrix_bedroom
data:
  message: The garage door has been open for 10 minutes.
  data:
    icon: "33655"
    sound: beep
```

# Create a custom app

```
service: awtrix.awtrix_bedroom_push_app_data
data: 
  name: test
  data:
    text : "Hello, AWTRIX Light!"
    rainbow: true
    icon: "87"
    duration: 5
    pushIcon: 2
    lifetime: 900
    repeat: 1
```

# Remove app

```
service: awtrix.awtrix_bedroom_push_app_data
data: 
  name: test
```

# Change Settings

```
service: awtrix.awtrix_bedroom_settings
data:
    WD: false 
    TIME_COL: 
      - 255
      - 0
      - 0
    TMODE: 0 
    BRI: 1
    ABRI: false
    ATRANS: false
```

# Switch to App name

```
service: awtrix.awtrix_bedroom_switch_app
data: 
  name: Time
```

# back

```
service: awtrix.awtrix_bedroom_settings
data:
    WD: true 
    TIME_COL: 
      - 255
      - 255
      - 255
    TMODE: 1 
    BRI: 1
    ABRI: true
    ATRANS: true
```

```
service: awtrix.awtrix_bedroom_rtttl
data: 
 rtttl: "two_short:d=4,o=5,b=100:16e6,16e6"
```

```
service: awtrix.awtrix_bedroom_sound
data:
 sound: beep
```

Hold notification
```
service: notify.awtrix_bedroom
data:
  message: "Hello!"
  data: 
    hold: true
```

Dismiss hold notification
```
service: notify.awtrix_bedroom
data:
  message: ""
```

```
simple automation

```
alias: bathroom current temperature
description: bathroom current temperature
trigger:
  - platform: time_pattern
    minutes: /5
condition: []
action:
  - service: awtrix.awtrix_bedroom_push_app_data
    data:
      name: home_temperature
      data:
        text: "{{states('sensor.bathroom_current_temperature')}}°"
        icon: "2056"
        duration: 5
        pushIcon: 2
        lifetime: 900
        repeat: 1
mode: single
```
