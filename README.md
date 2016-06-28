# Smart Button

A simple GPIO-controlled button for the Raspberry Pi.

## Prerequisites

* Python version 3
* [RPi.GPIO](https://pypi.python.org/pypi/RPi.GPIO) (at least version 0.5.2)

## Usage

Unfortunately, you will have to run the `smart-button.py` with
super-user privileges, i.e. invoke `sude ./smart-button.py`.

~~~~~~~~~~
smart-button.py [-q] [-P port] [-t timeout] [-d debounce] [-l action] [-c action]

    -q          quiet: suppress diagnostic output
    -P port     act on button connected to specified BCM port (default: 21)
    -t timeout  timeout value for long press (default: 5.0)
    -d debounce time (default: 0.15)
    -l action   the action to be run on long press
    -c action   the action to be run on normal press
~~~~~~~~~~

## Examples

~~~~~~~~~~
smart-button.py -P 16 -c 'curl -X POST https://maker.ifttt.com/trigger/button/with/key/$YOUR_KEY'
~~~~~~~~~~

This example connects the button on BCM port 16 to the given
command. As a result, pressing the button triggers the given
[IFTTT](https://ifttt.com) action.

~~~~~~~~~~
smart-button.py -t 3.2 -c 'echo "short press"' -l 'echo "long press"'
~~~~~~~~~~

Prints the string „short press“ if the button is pressed quickly, or
the string „long press“ when the button is held down for at least 3.2
seconds.

## Using as a System Service

In combination with a
[systemd](http://www.freedesktop.org/wiki/Software/systemd/) service,
you could create a shutdown button for your Raspi as follows:

1. Copy the file `shutdown.service` into your platform's systemd
home, e.g.`/etc/systemd/system` on Debian.
1. Copy the file `smart-button.py` into `/usr/local/bin` (or wherever
you want it to be.)
1. Start `shutdown.service`: `sudo systemctl start shutdown.service`. 

The file `shutdown.service` could have the following contents:
~~~~~~~~~~
[Unit]
Description=Shutdown button

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/smart-button.py -q -l 'shutdown -h now'
StandardOutput=syslog

[Install]
WantedBy=multi-user.target
~~~~~~~~~~

# License

This software is licensed under the MIT License (MIT), see `LICENSE`.
