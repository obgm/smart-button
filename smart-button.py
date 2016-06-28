#! /usr/bin/env python3
'''
Copyright (c) 2016 Olaf Bergmann
'''

import getopt, sys
import os, threading, time
import RPi.GPIO as GPIO

BUTTON=21
DEBOUNCE=0.15
TIMEOUT=5
SHORT_CMD=""
LONG_CMD=""
QUIET=False
DROP=True
prg=os.path.basename(__file__)

def log(*msg, **attr):
  if not QUIET:
    print(*msg, **attr)

try:
  opts, args = getopt.getopt(sys.argv[1:], "P:t:d:l:c:qD",
    ["port=", "timeout=", "debounce=", "long-press=", "command=", "quiet"])
  for opt, arg in opts:
    if opt in ("-P", "--port"):
      BUTTON=int(arg)
    elif opt in ("-t", "--timeout"):
      TIMEOUT=float(arg)
    elif opt in ("-d", "--debounce"):
      DEBOUNCE=float(arg)
    elif opt in ("-c", "--command"):
      SHORT_CMD=arg
    elif opt in ("-l", "--long-press"):
      LONG_CMD=arg
    elif opt in ("-q", "--quiet"):
      QUIET=True
    elif opt in ("-D"):
      DROP=False
except getopt.GetoptError:
  log("usage: %s [-q] [-D] [-P port] [-t timeout] [-d debounce] [-l action] [-c action]\n" % (prg),
    file=sys.stderr)
  log("    -q   \tquiet: suppress diagnostic output", file=sys.stderr)
  log("    -D   \tDon't drop privileges to normal user (dangerous)", file=sys.stderr)
  log("    -P port\tact on button connected to specified BCM port (default: %d)" % (BUTTON), file=sys.stderr)
  log("    -t timeout\ttimeout value for long press (default: %3.1f)" % (TIMEOUT), file=sys.stderr)
  log("    -d debounce time (default: %4.2f)" % (DEBOUNCE), file=sys.stderr)
  log("    -l action\tthe action to be run on long press", file=sys.stderr)
  log("    -c action\tthe action to be run on normal press", file=sys.stderr)
  sys.exit(2)

if os.getuid() != 0:
  log("Running as normal user. This is good but you may experience")
  log("issues with this script due to missing access privileges.")
  log("If you get a runtime exception from wait_for_edge(), try")
  log("running with sudo.\n")

GPIO.setmode(GPIO.BCM)

GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

if LONG_CMD != "" or SHORT_CMD != "":
  log("%s: listen on port %d" % (prg, BUTTON))
if LONG_CMD != "":
  log("hold button down for %d seconds to trigger long-command" % (TIMEOUT))
sys.stdout.flush()

time_stamp = time.time()
t = None

def timer_callback():
  global t
  if t:
    t.cancel()
    t = None
  if LONG_CMD != "":
    os.system(LONG_CMD)

def changed(channel):
  '''
  The debouncing strategy is documented in 
http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-2
  '''
  global t
  global time_stamp
  time_now = time.time()
  if (time_now - time_stamp) > DEBOUNCE:
    if GPIO.input(BUTTON) and t:
      t.cancel()
      t = None
      if SHORT_CMD != "":
        os.system(SHORT_CMD)
    elif not GPIO.input(BUTTON) and not t:
      t = threading.Timer(TIMEOUT, timer_callback)
      t.start()
  time_stamp = time_now

GPIO.add_event_detect(BUTTON, GPIO.BOTH)
GPIO.add_event_callback(BUTTON, changed)

'''
Drop privileges to normal user.
FIXME: With normal user privileges, GPIO events are not reported anymore.
'''
#if DROP and int(os.environ['SUDO_UID']):
#  os.seteuid(int(os.environ['SUDO_UID']))
#  log("Dropping privileges to user '%s' (uid %s)" % (os.environ['SUDO_USER'], os.environ['SUDO_UID']))

'''
Idle from here.
'''
try:
  while 1:
    time.sleep(86400)
except KeyboardInterrupt:
  pass
finally:
  GPIO.cleanup()

