<div align="center">

# MQTTR

This is a lightweight MQTT Reciever for a Raspberry Pi Pico W to control (in our case) a 3D printed drone. It connects to an MQTT broker and listens for messages on a specified topic and uses the received messages to control the drone's motors via PWM signals.

</div>

> [!CAUTION]
> This project is a work in progress and should be used with caution. Always test in a safe environment.

## Expected Setup

RC = "laptop"
mqtt broker = "mosquitto"

It is laid out (hard coded) that:

- a mqtt broker is running on the laptop
- (x) the laptop is running a hotspot, and the Raspberry Pi Pico W is connected to the hotspot
- the broker has `listener 1883 0.0.0.0` and `allow_anonymous true` in its config
- firewall is disabled, or the laptop allows inbound connections on port 1883
- (x) the env.example.py file is renamed to env.py, and the hotspot SSID and password are added
- (x) recommended. not required: use pycharm with the micropython plugin, and a run configuration called 'Execute' will be available.

## Usage

0. Make sure you did the setup above.
1. (x) Upload all files (except those that start with `.`) from here directly to the Raspberry Pi Pico W and run the main.py file.
2. (x) (the pico will have successfully connected to the broker if its LED stopped blinking)
3. Go to `\.controller\` and run `startup.ps1` and your browser should open and go to [localhost:8000](http://localhost:8000/)
4. (x) Use the UI to control the drone.

## Installation

There is a installer script which will automate everything, except those steps marked with an x.

### **Run the installer with an elevated (ADMIN) powershell window:**

**Main**

`iex "& { $(iwr -useb 'https://raw.githubusercontent.com/IDPA-IMS/MQTTR/refs/heads/main/.installer.ps1') }"`

or

**Mirror**

`iex "& { $(iwr -useb 'https://idpa-ims.github.io/MQTTR/.installer.ps1') }"`

## **DISCLAIMER**

**THIS PROJECT IS PROVIDED "AS IS" WITHOUT ANY WARRANTIES, EXPRESS OR IMPLIED. THE AUTHOR DISCLAIMS ALL WARRANTIES INCLUDING, BUT NOT LIMITED TO, IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.**

> [!WARNING]
> This project is intended for educational purposes only. Ensure you understand the risks involved in controlling a drone and always operate it in a safe environment.
