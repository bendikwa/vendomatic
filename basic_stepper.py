#!/usr/bin/env python3

import sys
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

output_pins = [17,22,23,24]
for pin in output_pins:
  GPIO.setup(pin,GPIO.OUT)
  GPIO.output(pin, False)

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

rpm = 15

def reset():
  for pin in output_pins:
    GPIO.output(pin, False)

def get_sleep_time():
  base = 60000 / steps_per_revolution
  sleep_ms = base / rpm
  return sleep_ms / 1000

def step_one(direction=1):
  global current_step
  current_step = current_step + direction
  for index,pin in enumerate(output_pins):
      GPIO.output(pin, step_seq[current_step%step_count][index])

  time.sleep(get_sleep_time())

def step(steps=1, direction=1):
  for _ in range(steps):
      step_one(direction)


step(4096)
reset()
