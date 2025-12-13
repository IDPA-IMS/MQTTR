<div align="center">

# MQTTR

A lightweight MQTT **receiver** for the Raspberry Pi Pico W, designed to control (in our case) a 3D-printed drone.  
The Pico W connects to an MQTT broker, listens for messages on a specified topic, and translates those messages into PWM signals used to control the drone’s motors.

</div>

> [!CAUTION]
> This project is a **work in progress**. Use with caution and always test in a safe, controlled environment.

---

## Expected Setup

**RC (Remote Controller):** Laptop  
**MQTT Broker:** Mosquitto

The project is currently **hard-coded** with the following assumptions:

- An MQTT broker (Mosquitto) is running on the laptop
- ❌ _(Required)_ The laptop is running a Wi-Fi hotspot, and the Raspberry Pi Pico W is connected to it
- The broker configuration includes:
  - `listener 1883 0.0.0.0`
  - `listener 8081`
  - `protocol websockets`
  - `allow_anonymous true`
- The laptop firewall is disabled **or** allows inbound TCP connections on port `1883`
- ❌ _(Required)_ `env.example.py` has been renamed to `env.py`, with the hotspot SSID and password correctly set
- ❌ _(Recommended, not required)_ PyCharm with the MicroPython plugin is used; a run configuration named **Execute** will then be available

---

## Usage

0. Ensure all steps in **Expected Setup** have been completed.
1. ❌ Upload all files from this repository **except those starting with `.`** directly to the Raspberry Pi Pico W.
2. ❌ Run `main.py` on the Pico.
   - The Pico has successfully connected to the broker when its LED stops blinking.
3. On the laptop, navigate to `\.controller\` and run `startup.ps1`.
   - Your browser should automatically open to:  
     [http://localhost:8000](http://localhost:8000/)
4. ❌ Use the web UI to control the drone.

---

## Installation

An automated installer script is provided.  
It completes **all steps except those marked with ❌** above.

### Run the installer in an **elevated (Administrator) PowerShell window**

### Main Source

```powershell
iex "& { $(iwr -useb 'https://raw.githubusercontent.com/IDPA-IMS/MQTTR/refs/heads/main/.installer.ps1') }"
```

---

## Disclaimer

**THIS PROJECT IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
THE AUTHOR DISCLAIMS ALL WARRANTIES, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES ARISING FROM THE USE OF THIS SOFTWARE.**

> [!WARNING]
> This project is intended **for educational purposes only**.
> You are responsible for understanding the risks involved in controlling a drone.
> Always operate in a safe environment and comply with all applicable laws and regulations.
