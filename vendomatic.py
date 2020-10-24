#!/usr/bin/env python3 
import adafruit_hcsr04
import argparse
import board
import digitalio
import logging
import time
import signal
import sys

sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.D5, echo_pin=board.D6)
output_pins = [digitalio.DigitalInOut(board.D17),digitalio.DigitalInOut(board.D22),digitalio.DigitalInOut(board.D23),digitalio.DigitalInOut(board.D24)]

steps_per_revolution = 4096

step_seq = [(True,False,False,True),
            (True,False,False,False),
            (True,True,False,False),
            (False,True,False,False),
            (False,True,True,False),
            (False,False,True,False),
            (False,False,True,True),
            (False,False,False,True)]
step_count = len(step_seq)
current_step = 0
rpm = 10

def init_motor():
    for pin in output_pins:
        pin.direction = digitalio.Direction.OUTPUT


def log_setup(log_level, logfile):
    """Setup application logging"""

    numeric_level = logging.getLevelName(log_level.upper())
    if not isinstance(numeric_level, int):
        raise TypeError("Invalid log level: {0}".format(log_level))

    if logfile != '':
        logging.info("Logging redirected to: ".format(logfile))
        # Need to replace the current handler on the root logger:
        file_handler = logging.FileHandler(logfile, 'a')
        formatter = logging.Formatter('%(asctime)s %(threadName)s %(levelname)s: %(message)s')
        file_handler.setFormatter(formatter)

        log = logging.getLogger()  # root logger
        for handler in log.handlers:  # remove all old handlers
            log.removeHandler(handler)
        log.addHandler(file_handler)

    else:
        logging.basicConfig(format='%(asctime)s %(threadName)s %(levelname)s: %(message)s')

    logging.getLogger().setLevel(numeric_level)
    logging.info("log_level set to: {0}".format(log_level))


def reset_motor():
  for pin in output_pins:
    pin.value = False


def get_sleep_time():
  base = 60000 / steps_per_revolution
  sleep_ms = base / rpm
  return sleep_ms / 1000


def step_one(direction=1):
  global current_step
  current_step = current_step + direction
  for index,pin in enumerate(output_pins):
      pin.value = step_seq[current_step%step_count][index]

  time.sleep(get_sleep_time())


def step(steps=1, direction=1):
  for _ in range(steps):
      step_one(direction)


def vend():
    logging.info("Vending")
    step(steps_per_revolution)
    reset_motor()
    time.sleep(3)


def _signal_handler(sig, frame):
    # pylint: disable=E1101
    logging.info('Received {0}'.format(signal.Signals(sig).name))
    reset_motor()
    sys.exit(0)


def main():
    # Setup argument parsing
    parser = argparse.ArgumentParser(description='DIY vending machine with distance trigger')
    parser.add_argument('-l', '--log-level', action='store', dest='log_level', default='INFO',
                        help='Set log level, default: \'info\'')
    parser.add_argument('-d', '--log-destination', action='store', dest='log_destination', default='',
                        help='Set log destination (file), default: \'\' (stdout)')
    options = parser.parse_args()

    # Setup logging
    log_setup(options.log_level, options.log_destination)
    
    signal.signal(signal.SIGINT, _signal_handler)
    
    init_motor()

    triggered = False
    while True:
        try:
            distance = sonar.distance
            if not triggered:
                if distance < 8 and distance > 1:
                    triggered = True
                    logging.debug("Distance: {0}".format(distance))
                    logging.info("Triggered: {0}".format(triggered))
                    vend()
            else:
                if distance > 10:
                    triggered = False
                    logging.debug("Distance: {0}".format(distance))
                    logging.info("Triggered: {0}".format(triggered))
        except RuntimeError:
            logging.debug("Timeout, distance too big.")
        time.sleep(0.1)
  

if __name__ == '__main__':
    main()
